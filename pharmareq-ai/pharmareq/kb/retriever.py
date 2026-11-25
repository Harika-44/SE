"""Retrieval over the regulation knowledge base (plan sections 5 and 6)."""
import json
from functools import lru_cache
from pathlib import Path

from .. import config
from ..text_utils import TfIdf, stem, tokens

_KB_PATH = Path(__file__).with_name("regulations.json")


@lru_cache(maxsize=1)
def load():
    data = json.loads(_KB_PATH.read_text())
    entries = data["entries"]
    docs = [e["title"] + " " + e["summary"] + " " + " ".join(e["keywords"]) * 2 for e in entries]
    return entries, TfIdf(docs)


def all_entries() -> list[dict]:
    return load()[0]


def get(kb_id: str) -> dict | None:
    return next((e for e in all_entries() if e["id"] == kb_id), None)


def retrieve(text: str, k: int = 3, min_score: float | None = None) -> list[tuple[dict, float]]:
    entries, index = load()
    min_score = config.RETRIEVAL_MIN_SCORE if min_score is None else min_score
    scores = index.query(text)
    ranked = sorted(zip(entries, scores), key=lambda x: -x[1])
    return [(e, round(s, 3)) for e, s in ranked[:k] if s >= min_score]


def _has(word: str, toks: set[str]) -> bool:
    s = stem(word)
    if len(s) <= 2:
        return s in toks
    return any(t == s or s in t for t in toks)


def control_matches(control: dict, text: str) -> bool:
    toks = set(tokens(text, keep_stop=True))
    return all(_has(w, toks) for w in control["all"]) and any(_has(w, toks) for w in control["any"])
