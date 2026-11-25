import math
import re
from collections import Counter

STOP = set(
    """a an the and or but if then of to in on at by for with from as is are was were be been being it its this that
these those we i you they he she our your their my me us them can could should would shall will may might must do does
did done have has had not no also so very just than too into onto over under about any all each every some more most
other such only own same there here when where which who whom what how why up down out off again further once both few
need needs want wants like get gets make makes use used using able etc ok yes sure please""".split()
)

# Light synonym normalisation so "keep the register" matches "retain the records".
SYN = {
    "keep": "retain", "store": "retain", "preserve": "retain", "retention": "retain", "retained": "retain",
    "register": "record", "log": "record", "ledger": "record", "entry": "record", "entries": "record",
    "medicine": "drug", "medicines": "drug", "medication": "drug", "tablet": "drug", "tablets": "drug",
    "expiry": "expir", "expire": "expir", "expired": "expir", "expiration": "expir",
    "sell": "sale", "selling": "sale", "sold": "sale", "dispensing": "dispens", "dispense": "dispens",
    "dispensed": "dispens", "invoice": "bill", "billing": "bill", "bills": "bill",
    "mandatory": "requir", "required": "requir", "require": "requir", "compulsory": "requir",
}


def stem(w: str) -> str:
    w = w.lower()
    if w in SYN:
        return SYN[w]
    for suf in ("ing", "edly", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            w = w[: -len(suf)]
            break
    return SYN.get(w, w)


def tokens(text: str, keep_stop: bool = False) -> list[str]:
    ws = re.findall(r"[A-Za-z][A-Za-z0-9\-]*|\d+", text.lower())
    out = []
    for w in ws:
        if not keep_stop and w in STOP:
            continue
        out.append(stem(w))
    return out


_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])|\n+")


def split_sentences(text: str) -> list[str]:
    parts = []
    for chunk in _SENT_SPLIT.split(text):
        chunk = chunk.strip(" \t-•*")
        if chunk:
            parts.append(chunk)
    return parts


class TfIdf:
    """Small in-memory TF-IDF index (swap for a vector DB such as Chroma/pgvector in production)."""

    def __init__(self, docs: list[str]):
        self.docs = [Counter(tokens(d)) for d in docs]
        n = len(docs)
        df = Counter()
        for d in self.docs:
            df.update(d.keys())
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.vecs = [self._vec(d) for d in self.docs]

    def _vec(self, counter: Counter) -> dict:
        v = {t: (1 + math.log(c)) * self.idf.get(t, 1.0) for t, c in counter.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def query(self, text: str) -> list[float]:
        q = self._vec(Counter(tokens(text)))
        return [sum(q.get(t, 0.0) * w for t, w in dv.items()) for dv in self.vecs]

    def pair_sim(self, i: int, j: int) -> float:
        a, b = self.vecs[i], self.vecs[j]
        return sum(a.get(t, 0.0) * w for t, w in b.items())


def jaccard(a: str, b: str) -> float:
    A, B = set(tokens(a)), set(tokens(b))
    return len(A & B) / len(A | B) if A and B else 0.0
