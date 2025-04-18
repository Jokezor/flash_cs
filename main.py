from pdf_ingestor import extract_text
from text_chunker import chunk_text
from embedder import embed_text
from flashcard_generator import generate_flashcard
from flashcard_evaluator import is_good_flashcard
from diagram_generator import generate_skills_diagram
from anki_sync import sync_flashcards_to_anki

def main():
    pdf_file = "ostep.pdf"
    
    # Step 1: Ingest the PDF.
    text = extract_text(pdf_file)
    print("Text extracted from PDF.")
    
    # Step 2: Chunk the text.
    chunks = chunk_text(text)
    print(f"Text split into {len(chunks)} chunks.")
    
    flashcards = []
    for chunk in chunks[0:10]:
        # Optional: Get embedding (here just illustrative)
        embedding = embed_text(chunk)
        
        # Step 3: Generate a flashcard candidate.
        card = generate_flashcard(chunk)
        
        # Step 4: Evaluate flashcard quality.
        if is_good_flashcard(card):
            flashcards.append(card)
    
    print(f"Generated {len(flashcards)} flashcards that passed quality checks.")
    
    # Step 5: Generate a diagram image (example_chart.png) showing topic coverage.
    generate_skills_diagram(flashcards)
    
    # Step 6: Sync the flashcards with Anki.
    sync_flashcards_to_anki(flashcards)
    print("Flashcards have been synced to Anki.")

if __name__ == "__main__":
    main() 