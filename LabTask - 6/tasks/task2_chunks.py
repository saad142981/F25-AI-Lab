import re
from lab6_search import Retriever, show_hits

SYNTHETIC_DOCS = {
    "late": "University coursework deadlines are strictly enforced across all undergraduate departments to maintain fair grading schedules and timely academic feedback. Dr. Ahmed in the Academic Affairs Office processes all grading records at 5:00 p.m. every Friday during the regular teaching semester. Late submission is normally penalized at a flat rate of ten percent per calendar day up to five consecutive days, after which a score of zero is recorded. Illness extensions require medical evidence before the deadline. Students who experience sudden hospitalization, severe acute medical emergencies, or documented bereavement within forty-eight hours of the scheduled assessment submission timestamp must upload a certified hospital discharge summary, licensed physician attestation form, and academic advisor notification through the student portal prior to final grade moderation by the departmental assessment board. Retroactive excuses submitted after official marks are published will not be reviewed by the examination committee under any circumstances. Furthermore, computer failures, local power outages, or corrupt storage media on personal laptops do not qualify as valid grounds for deadline waivers. Group project coordinators must ensure that every team member uploads individual contribution logs alongside the main report archive before closure.",
    "password": "Campus identity management systems protect student academic records, digital library databases, and laboratory compute clusters from unauthorized external access or credential harvesting attacks. Multi-factor authentication session tokens expire every thirty days on unmanaged personal laptops and mobile devices. Reset a forgotten password using the recovery link. Never share recovery codes with classmates, teaching assistants, or support staff during troubleshooting sessions under any circumstances. Users whose accounts are automatically locked after five consecutive failed login attempts across the central single sign-on gateway, virtual private network concentrator, or electronic learning portal must wait thirty minutes for automated cooldown unlock unless they verify their original government-issued identification card in person at the IT Service Desk in Room 104B during working hours. Temporary bypass pins issued by Dr. Khan for supervised laboratory examinations remain valid for strictly two hours and cannot be reused across different workstation subnets or wireless guest networks. Standard alumni email accounts follow a separate annual renewal schedule managed by the registrar and do not grant access to internal engineering compute servers.",
    "contractor": "Human Resources operational guidelines establish distinct workplace access rules, network privileges, and telecommuting policies for permanent faculty, full-time administrative staff, and external technical consultants. Permanent salaried employees may request hybrid remote work arrangements for up to two business days per week with written department head approval and quarterly performance reviews. Contractors can work remotely only if the signed contract permits it. Employee rules do not apply to contractors under standard university procurement and information security regulations. External vendors, short-term software engineering consultants, and visiting laboratory maintenance specialists retained under fixed-price service agreements must perform all scheduled technical duties on-site inside designated secure campus facilities unless an explicit remote-access addendum has been countersigned by both the Chief Information Security Officer and the Director of Procurement prior to project onboarding and badge issuance. Unapproved off-site connections from contractor devices to internal staging servers or research databases will trigger immediate credential revocation and contract termination reviews by the legal compliance office."
}

LABELED_CLAUSES = {
    "late": "Illness extensions require medical evidence before the deadline.",
    "password": "Reset a forgotten password using the recovery link.",
    "contractor": "Contractors can work remotely only if the signed contract permits it.",
}
def word_spans(text):
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def windows(text, size=40, overlap=10, offset=0):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    spans = word_spans(text)
    result = []
    for i in range(0, len(spans), size - overlap):
        j = min(i + size, len(spans))
        result.append((offset + spans[i][0], offset + spans[j - 1][1]))
        if j == len(spans):
            break
    return result


def sentence_chunks(text, size=40):
    if size <= 0:
        raise ValueError("size must be positive")
    cuts = (
        [0]
        + [m.end() for m in re.finditer(r"[.!?]\s+", text)]
        + [len(text)]
    )
    out, pending, count = [], None, 0
    for a, b in zip(cuts, cuts[1:]):
        segment = text[a:b]
        n = len(segment.split())
        if not n:
            continue
        if n > size:
            if pending is not None:
                out.append(pending)
            out.extend(windows(segment, size, 0, a))
            pending, count = None, 0
        elif pending is not None and count + n <= size:
            pending, count = (pending[0], b), count + n
        else:
            if pending is not None:
                out.append(pending)
            pending, count = (a, b), n
    if pending is not None:
        out.append(pending)
    return out


def make_chunks(docs, strategy):
    result = []
    for doc_id, text in docs.items():
        spans = (
            sentence_chunks(text)
            if strategy == "sentence"
            else windows(text, 40, int(strategy))
        )
        for i, (a, b) in enumerate(spans):
            result.append(
                dict(
                    id=f"{doc_id}:{i}",
                    doc=doc_id,
                    start=a,
                    end=b,
                    text=text[a:b],
                )
            )
    return result


def run_edge_case_assertions():
    assert windows("") == []
    assert windows("short text") == [(0, 10)]
    try:
        windows("a b", 2, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid overlap was accepted")
    long_sent = " ".join(["word"] * 95) + "."
    assert all(
        len(long_sent[a:b].split()) <= 40
        for a, b in sentence_chunks(long_sent)
    )
    for strategy in ["0", "10", "sentence"]:
        for c in make_chunks(SYNTHETIC_DOCS, strategy):
            assert (
                c["text"] == SYNTHETIC_DOCS[c["doc"]][c["start"] : c["end"]]
            )
            assert 0 <= c["start"] < c["end"] <= len(SYNTHETIC_DOCS[c["doc"]])


def analyze_strategies(docs):
    orig_words = sum(len(t.split()) for t in docs.values())
    print(f"Total corpus words across {len(docs)} documents: {orig_words}")
    for strategy in ["0", "10", "sentence"]:
        chunks = make_chunks(docs, strategy)
        word_counts = [len(c["text"].split()) for c in chunks]
        emitted_words = sum(word_counts)
        dup_words = emitted_words - orig_words
        dup_rate = (dup_words / orig_words) * 100.0
        survived = {}
        for doc_id, clause in LABELED_CLAUSES.items():
            survived[doc_id] = any(
                c["doc"] == doc_id and clause in c["text"] for c in chunks
            )
        print(
            f"Strategy={strategy:<8} | Chunks={len(chunks):<2} | "
            f"AvgWords={sum(word_counts)/len(chunks):.1f} | "
            f"DupWords={dup_words:<3} ({dup_rate:.1f}%) | "
            f"ClauseSurvival={survived}"
        )


def run_semantic_retrieval_check(docs):
    paraphrased_queries = [
        "I was sick and missed the coursework submission date, what proof do I need?",
        "How can I regain access to my locked student account?",
        "Are external consultants allowed to telecommute from home?",
    ]
    chunks = make_chunks(docs, "sentence")
    for backend in ["tfidf", "embedding"]:
        print(f"\n=== Retrieval Check (Strategy: sentence, Backend: {backend}) ===")
        try:
            engine = Retriever(chunks, backend=backend)
            for q in paraphrased_queries:
                print(f"\nQuery: {q}")
                show_hits(engine.search(q, k=2))
        except Exception as exc:
            print(f"Backend {backend} execution notice: {exc}")


if __name__ == "__main__":
    run_edge_case_assertions()
    print("All Task 2 edge-case assertions passed.")
    analyze_strategies(SYNTHETIC_DOCS)
    run_semantic_retrieval_check(SYNTHETIC_DOCS)
