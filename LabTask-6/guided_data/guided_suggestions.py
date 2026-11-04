from guided_chatbot import build_bot

if __name__ == "__main__":
    engine = build_bot()
    query = "assignment upload"
    print("Suggested questions:")
    for record, score in engine.search(query, k=3):
        if score > 0:
            print(record["question"], f"({score:.3f})")
