import re
from guided_chatbot import build_bot, reply

samples = [
    "AI, search!",
    "I can't log in.",
    "help@example.com",
    "CS4944 version 2.1",
    "",
    "یہ ایک مثال ہے",
]


def run_token_comparison():
    print("=== Tokenization Comparison (Whitespace vs Unicode Regex) ===")
    for text in samples:
        ws = text.split()
        words = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
        print(f"Original: {repr(text)}")
        print(f"  Whitespace ({len(ws)}): {ws}")
        print(f"  Word-like  ({len(words)}): {words}")
    assert re.findall(r"\b\w+\b", "") == []

    print("\n=== Subword Tokenization (all-MiniLM-L6-v2) ===")
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", device="cpu"
        )
        for text in samples[:4]:
            subwords = model.tokenizer.tokenize(text)
            token_ids = model.tokenizer(text, truncation=False)["input_ids"]
            print(f"Original: {repr(text)}")
            print(f"  Subwords ({len(subwords)}): {subwords}")
            print(f"  Input IDs count (with special tokens): {len(token_ids)}")
    except Exception as exc:
        print(f"Subword model check notice: {exc}")


def run_faq_verification():
    print("\n=== FAQ Chatbot Transcript Verification (TF-IDF) ===")
    engine = build_bot("tfidf")
    test_inputs = [
        "How do I reset my password?",
        "How do I connect to the campus VPN from off-campus?",
        "I forgot my login password and cannot access my account",
        "late tuition fee deferment surcharge",
        "",
        "volcano geology earthquake tectonics",
    ]
    for q in test_inputs:
        response = reply(engine, q)
        print(f"You: {q}")
        print(f"Bot: {response}\n")

    assert "it_help.txt" in reply(engine, "How do I reset my password?")
    assert "network_guide.txt" in reply(
        engine, "How do I connect to the campus VPN from off-campus?"
    )
    assert reply(engine, "") == "Please enter a question."
    assert "No matching FAQ" in reply(engine, "volcano geology")
    assert "Possible matches" in reply(engine, "password recovery")
    print("All Task 1 assertions passed successfully.")


if __name__ == "__main__":
    run_token_comparison()
    run_faq_verification()
