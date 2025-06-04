# cs_flash_pipeline.py
# -------------------
# A LangChain-based pipeline to ingest PDFs, split into semantic chunks,
# extract key CS concepts, filter by novelty via embeddings, and generate
# Anki flashcards, pointing at a Chroma REST service.

from dotenv import load_dotenv
load_dotenv()  # This will load variables from your .env file into the environment

import os
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# --- Configuration via env vars ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://host.docker.internal:8765")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
CHROMA_PERSIST = os.getenv("CHROMA_PERSIST_DIR", "/chroma/chroma")
NOVELTY_THRESHOLD = float(os.getenv("NOVELTY_THRESHOLD", 0.85))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
PDF_PATH = os.getenv("PDF_PATH", "ostep.pdf")

# --- 2. Initialize Chroma REST client ---
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectordb = Chroma(
    embedding_function=embeddings,
    client_settings=Settings(
        chroma_server_host=CHROMA_HOST,
        chroma_server_http_port=CHROMA_PORT,
        anonymized_telemetry=False
    )
)

print("init chroma")

# --- 3. Set up LLM chains ---
llm = OpenAI(model="gpt-4o", temperature=0.2, openai_api_key=OPENAI_API_KEY)
importance_prompt = PromptTemplate(
    input_variables=["text"],
    template=(
        "From a computer-science perspective, extract ALL key concepts or facts "
        "from the following passage:\n\n{text}\n\n" 
        "Return each concept on its own line."
    )
)
importance_chain = LLMChain(llm=llm, prompt=importance_prompt)
flashcard_prompt = PromptTemplate(
    input_variables=["concept", "context"],
    template=(
        "Generate an Anki flashcard for the concept below. Use 'Q:' and 'A:' markers.\n\n"  
        "Concept: {concept}\nContext: {context}"
    )
)
flashcard_chain = LLMChain(llm=llm, prompt=flashcard_prompt)

# Add a chain to validate the quality of the flashcard
validate_flashcard_prompt = PromptTemplate(
    input_variables=["flashcard"],
    template=(
        "Validate the quality of the flashcard below. Return 'valid' or 'invalid'.\n\n"
        "Flashcard: {flashcard}"
    )
)
validate_flashcard_chain = LLMChain(llm=llm, prompt=validate_flashcard_prompt)

# --- 4. Helper: AnkiConnect add-note ---
def add_to_anki(question: str, answer: str, deck: str = "OSTEP"):
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck,
                "modelName": "Basic",
                "fields": {"Front": question, "Back": answer},
                "tags": [deck.replace(" ", "_")]
            }
        }
    }
    resp = requests.post(ANKI_CONNECT_URL, json=payload).json()
    if resp.get("error"):
        print("Anki error:", resp.get("error"))

def generate_flashcards():
    # --- 0. Load & chunk PDF ---
    loader = PyPDFLoader(PDF_PATH)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    docs = loader.load()
    chunks = splitter.split_documents(docs)
    print(f"[+] Split into {len(chunks)} semantic chunks.")

    # --- 5. Main pipeline loop ---
    for chunk in chunks:
        text = chunk.page_content
        # 5a. Embed the chunk
        vec = embeddings.embed_documents([text])[0]
        # 5b. Novelty check against top 5 neighbors
        results = vectordb.similarity_search_by_vector(vec, k=5, return_scores=True)
        sims = [res.score if hasattr(res, 'score') else res[1] for res in results]
        if all(s > NOVELTY_THRESHOLD for s in sims):
            continue  # skip chunks with only near-duplicates

        # 5c. Extract key concepts
        concepts_raw = importance_chain.run(text=text)
        concepts = [c.strip() for c in concepts_raw.split("\n") if c.strip()]

        # 5d. Generate flashcards for each concept
        for concept in concepts:
            qa = flashcard_chain.run(concept=concept, context=text)
            print(qa)
            if "Q:" in qa and "A:" in qa:
                q_part, a_part = qa.split("A:", 1)
                question = q_part.replace("Q:", "").strip()
                answer = a_part.strip()
                add_to_anki(question, answer)

        # 5e. Persist new embedding
        vectordb.add_documents(
            documents=[chunk],
            ids=[chunk.metadata.get("page")],
            embeddings=[vec]
        )
    vectordb.persist()

    print("[+] Pipeline complete: new cards added to Anki.")


if __name__ == "__main__":
    # Start with a sample extract text about operating systems;
    example_text = """
    It turns out that the operating system, with some help from the hard-ware, is in charge of this illusion, i.e., the illusion that the system has
    a very large number of virtual CPUs. Turning a single CPU (or a small
    set of them) into a seemingly infinite number of CPUs and thus allowing
    many programs to seemingly run at once is what we call virtualizing the
    CPU, the focus of the first major part of this book.
    Of course, to run programs, and stop them, and otherwise tell the OS
    which programs to run, there need to be some interfaces (APIs) that you
    can use to communicate your desires to the OS. We’ll talk about these
    APIs throughout this book; indeed, they are the major way in which most
    users interact with operating systems.
    You might also notice that the ability to run multiple programs at once
    raises all sorts of new questions. For example, if two programs want to
    run at a particular time, which should run? This question is answered by
    a policy of the OS; policies are used in many different places within an
    OS to answer these types of questions, and thus we will study them as
    we learn about the basic mechanisms that operating systems implement
    (such as the ability to run multiple programs at once). Hence the role of
    the OS as a resource manager.
    """

    # 1. Try llm chains and verify output
    important_parts = importance_chain.run(text=example_text)
    print(important_parts)
    flashcard_chain.run(concept="virtualizing the CPU", context=important_parts)
    qa = flashcard_chain.run(concept="virtualizing the CPU", context=example_text)
    print(qa)
    validate_flashcard_chain.run(flashcard=qa)
