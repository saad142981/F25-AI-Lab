import csv
import json
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from task2_chunks import make_chunks


def evaluate(scores, chunks, items):
    hits, reciprocal = [], []
    for row, q in zip(scores, items):
        if q["doc"] is None:
            continue
        top = np.argsort(-row, kind="stable")[:3]
        good = [
            rank
            for rank, i in enumerate(top, 1)
            if chunks[i]["doc"] == q["doc"]
            and q["evidence"] in chunks[i]["text"]
        ]
        hits.append(bool(good))
        reciprocal.append(1 / good[0] if good else 0)
    return (
        (float(np.mean(hits)), float(np.mean(reciprocal)))
        if hits
        else (None, None)
    )


def main():
    with open("corpus.json", encoding="utf-8") as f:
        docs = json.load(f)
    with open("queries.json", encoding="utf-8") as f:
        items = json.load(f)
    assert docs and items
    for q in items:
        assert q["split"] in {"dev", "test"}
        if q["doc"] is not None:
            assert q["evidence"] and q["evidence"] in docs[q["doc"]]
    t = time.perf_counter()
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2", device="cpu"
    )
    print("Model load seconds", time.perf_counter() - t)
    query_texts = [q["query"] for q in items]
    logs = []
    for strategy in ["0", "10", "sentence"]:
        chunks = make_chunks(docs, strategy)
        texts = [c["text"] for c in chunks]
        lengths = [
            len(model.tokenizer(t_str, truncation=False)["input_ids"])
            for t_str in texts + query_texts
        ]
        if max(lengths) > model.max_seq_length:
            raise ValueError(
                "Model limit exceeded; rechunk or shorten query"
            )
        for method in ["tfidf", "embedding"]:
            t = time.perf_counter()
            if method == "tfidf":
                vectorizer = TfidfVectorizer()
                C = vectorizer.fit_transform(texts)
                Q = vectorizer.transform(query_texts)
            else:
                C = model.encode(texts, normalize_embeddings=True)
                Q = model.encode(query_texts, normalize_embeddings=True)
            encode_seconds = time.perf_counter() - t
            t = time.perf_counter()
            scores = (
                (Q @ C.T).toarray() if method == "tfidf" else Q @ C.T
            )
            search_seconds = time.perf_counter() - t
            for split in ["dev", "test"]:
                indices = [
                    i
                    for i, q in enumerate(items)
                    if q["split"] == split
                ]
                result = evaluate(
                    scores[indices],
                    chunks,
                    [items[i] for i in indices],
                )
                print(
                    strategy,
                    method,
                    split,
                    "Hit/MRR",
                    result,
                    "chunks",
                    len(chunks),
                    "encode/search seconds",
                    encode_seconds,
                    search_seconds,
                )
            for row, q in zip(scores, items):
                for rank, i in enumerate(
                    np.argsort(-row, kind="stable")[:3], 1
                ):
                    c = chunks[i]
                    record = dict(
                        strategy=strategy,
                        method=method,
                        query=q["query"],
                        split=q["split"],
                        rank=rank,
                        score=float(row[i]),
                        chunk_id=c["id"],
                        doc=c["doc"],
                        start=c["start"],
                        end=c["end"],
                        text=c["text"],
                        answerable=q["doc"] is not None,
                    )
                    logs.append(record)
                    print(record)
    with open(
        "retrieval_log.csv", "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(logs[0]))
        writer.writeheader()
        writer.writerows(logs)


if __name__ == "__main__":
    main()
