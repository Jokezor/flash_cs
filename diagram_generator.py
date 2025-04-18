import matplotlib.pyplot as plt
from collections import Counter

def generate_skills_diagram(flashcards, output_path="example_chart.png"):
    """
    Generate a simple diagram (bar chart) showing the number of flashcards per topic.
    """
    topics = [card.get("topic", "Unknown") for card in flashcards]
    counts = Counter(topics)
    
    topics_list = list(counts.keys())
    counts_list = list(counts.values())

    plt.figure(figsize=(8, 6))
    plt.bar(topics_list, counts_list, color='skyblue')
    plt.xlabel("Topics")
    plt.ylabel("Number of Flashcards")
    plt.title("Coverage of Topics in OSTEP")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Diagram saved as '{output_path}'.")

if __name__ == '__main__':
    # Dummy test
    sample_cards = [
        {"topic": "Operating Systems"},
        {"topic": "Concurrency"},
        {"topic": "Operating Systems"},
        {"topic": "Memory Management"}
    ]
    generate_skills_diagram(sample_cards) 