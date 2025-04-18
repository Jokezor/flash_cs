import requests

def create_deck_if_not_exists(deck_name):
    """
    Ensures an Anki deck exists by using the 'createDeck' action via AnkiConnect.
    """
    url = "http://localhost:8765"
    payload = {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": deck_name}
    }
    response = requests.post(url, json=payload)
    result = response.json()
    if response.status_code != 200 or result.get("error"):
        print("Error creating deck:", result.get("error"))
    else:
        print("Deck ensured:", deck_name)

def sync_flashcards_to_anki(flashcards, default_deck="OSTEP"):
    """
    Sync flashcards to Anki with deck creation per flashcard's topic.
    Each flashcard is added into its respective deck based on its 'topic'. If no topic is provided,
    the default_deck is used.
    """
    url = "http://localhost:8765"
    # Group flashcards by deck name
    flashcards_by_deck = {}
    for card in flashcards:
        deck = card.get("topic", default_deck)
        flashcards_by_deck.setdefault(deck, []).append(card)
    
    for deck, cards in flashcards_by_deck.items():
        create_deck_if_not_exists(deck)
        for card in cards:
            note = {
                "deckName": deck,
                "modelName": "Basic",
                "fields": {
                    "Front": card["question"],
                    "Back": card["answer"]
                },
                "tags": [deck.replace(" ", "_")]
            }
            payload = {
                "action": "addNote",
                "version": 6,
                "params": {"note": note}
            }
            response = requests.post(url, json=payload)
            result = response.json()
            if response.status_code != 200 or result.get("error"):
                print("Error adding note:", result.get("error"))
            else:
                print("Card synced in deck '{}':".format(deck), card["question"][:50] + "...")
            
if __name__ == '__main__':
    # Dummy test for syncing one card (ensure Anki is running with AnkiConnect enabled)
    test_card = {
        "question": "What is a process?",
        "answer": "A process is a running instance of a program within an OS.",
        "topic": "Operating Systems"
    }
    sync_flashcards_to_anki([test_card]) 