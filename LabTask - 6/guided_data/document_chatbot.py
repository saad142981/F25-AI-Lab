import json
from task2_chunks import make_chunks
from lab6_search import Retriever

if __name__ == "__main__":
    with open("corpus.json", encoding="utf-8") as f:
        docs = json.load(f)
    # Deployed with "sentence" chunking and "embedding" backend based on dev metrics.
    engine = Retriever(make_chunks(docs, "sentence"), "embedding")
    print("Evidence assistant. Type exit to stop.")
    while True:
        try:
            query = input("Question: ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() == "exit":
            break
        hits = engine.search(query)
        if not hits:
            print("No candidate evidence; rephrase or contact a human.")
            continue
        print("Candidate evidence; relevance must be checked:")
        for number, (r, score) in enumerate(hits, 1):
            print(
                number,
                r["id"],
                f"{score:.3f}",
                "characters",
                r["start"],
                r["end"],
            )
        chosen = input("Choose 1-3 to inspect; Enter if none apply: ")
        if not chosen.isdigit() or not 1 <= int(chosen) <= len(hits):
            print("No answer selected. Rephrase or contact a human.")
            continue
        r, score = hits[int(chosen) - 1]
        print("Retrieved passage:", r["text"])
        print("Source:", r["doc"], "characters", r["start"], r["end"])
