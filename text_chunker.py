def chunk_text(text, chunk_size=1000):
    """
    Naively split the text into chunks of around `chunk_size` characters.
    In production, consider splitting using paragraph or heading boundaries.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

if __name__ == '__main__':
    sample = "This is a test. " * 100
    chunks = chunk_text(sample, 50)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk}\n") 