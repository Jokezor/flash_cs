import random

def generate_flashcard(chunk):
    """
    Generate a candidate flashcard from a text chunk.
    In production, an LLM based prompt should produce Q/A pairs.
    """
    sentences = chunk.split('. ')
    # Use the first sentence as a prompt basis for a question.
    question = "What does the following text describe: " + sentences[0] + "?"
    answer = chunk
    # Simulate topic classification by selecting randomly from a set of potential topics.
    topics = [
        "Operating Systems", "Concurrency", 
        "Memory Management", "File Systems", "Networking"
    ]
    topic = random.choice(topics)
    return {"question": question, "answer": answer, "topic": topic}

if __name__ == '__main__':
    sample_chunk = "Processes are a fundamental concept in operating systems. They help isolate running code from each other."
    card = generate_flashcard(sample_chunk)
    print("Generated flashcard:", card) 