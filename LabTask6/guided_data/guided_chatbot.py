from lab6_search import Retriever

FAQ = [
    {
        "id": "faq:password",
        "question": "How do I reset my password?",
        "answer": "Use the recovery link on the login page.",
        "source": "it_help.txt",
    },
    {
        "id": "faq:submit",
        "question": "Where do I submit my assignment?",
        "answer": "Use the assignment upload page in the learning portal.",
        "source": "assessment.txt",
    },
    {
        "id": "faq:late",
        "question": "Can illness justify a late submission?",
        "answer": "Request an extension with medical evidence before the deadline.",
        "source": "handbook.txt",
    },
    {
        "id": "faq:vpn",
        "question": "How do I connect to the campus VPN from off-campus?",
        "answer": "Install the university VPN client and authenticate with your student ID and two-factor token.",
        "source": "network_guide.txt",
    },
    {
        "id": "faq:tuition",
        "question": "What is the penalty for late tuition fee payment?",
        "answer": "A late surcharge of 5% is applied after the 10th of the billing month unless a financial aid deferment is approved.",
        "source": "finance_rules.txt",
    },
]


def build_bot(backend="tfidf"):
    records = [
        dict(r, text=r["question"] + " " + r["answer"]) for r in FAQ
    ]
    return Retriever(records, backend)


def reply(engine, query):
    if not query.strip():
        return "Please enter a question."
    for r in FAQ:
        if query.strip().casefold() == r["question"].casefold():
            return r["answer"] + " [source: " + r["source"] + "]"
    hits = engine.search(query)
    if not hits:
        return "No matching FAQ. Please contact the help desk."
    lines = ["Possible matches; choose or rephrase your question:"]
    for r, score in hits:
        lines.append(f'{r["question"]} (similarity {score:.3f})')
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend", choices=["tfidf", "embedding"], default="tfidf"
    )
    args = parser.parse_args()
    engine = build_bot(args.backend)
    print("FAQ assistant. Type exit to stop.")
    while True:
        try:
            query = input("You: ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() == "exit":
            break
        print("Bot:", reply(engine, query))
