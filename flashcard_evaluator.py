def evaluate_flashcard(card):
    """
    Returns a quality score between 0 and 1.
    Here we use a simple heuristic based on the length of the question
    and answer.
    """
    score = 0.0
    if len(card["question"]) > 20:
        score += 0.5
    if len(card["answer"]) > 100:
        score += 0.5
    return score

def is_good_flashcard(card, threshold=0.7):
    score = evaluate_flashcard(card)
    return score >= threshold

if __name__ == '__main__':
    example = {
        "question": "What does the following text describe: Processes in OS?",
        "answer": "Detailed explanation of process management...",
        "topic": "Operating Systems"
    }
    print("Card qualifies:", is_good_flashcard(example)) 