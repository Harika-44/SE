"""Sensitive-data masking and prompt-injection screening (plan sections 3 and 17).

Everything that could reach an LLM goes through mask() first. Only synthetic or
anonymised data should be used in the prototype; this is a safety net, not a licence
to submit real patient data.
"""
import re
from collections import Counter

_PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")),
    ("AADHAAR", re.compile(r"(?<!\d)\d{4}\s\d{4}\s\d{4}(?!\d)")),
    ("PAN", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")),
    ("PERSON", re.compile(r"\b(?:Dr|Mr|Mrs|Ms|Shri|Smt)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?")),
    ("PATIENT_ID", re.compile(r"\b(?:UHID|MRN|Patient\s*ID)[:\s#-]*[A-Z0-9-]{4,}\b", re.I)),
]


def mask(text: str) -> tuple[str, dict]:
    counts: Counter = Counter()
    for label, pat in _PATTERNS:
        def _sub(m, label=label):
            counts[label] += 1
            return f"[{label}]"

        text = pat.sub(_sub, text)
    return text, dict(counts)


_INJECTION = [
    r"ignore (?:all |any |the )?(?:previous|prior|above|earlier)",
    r"disregard .{0,40}(?:instruction|rule|polic)",
    r"(?:reveal|print|show|leak) .{0,30}(?:system prompt|instructions|api key|secret|password)",
    r"you are now\b",
    r"\bact as (?:an? )?(?:admin|root|developer|system)",
    r"override (?:your|the) (?:instructions|rules|guidelines|safety)",
    r"</?\s*(?:system|assistant|instructions?)\s*>",
    r"\bjailbreak\b",
    r"mark (?:all )?(?:requirements|everything) as (?:approved|accepted|compliant)",
]
_INJ_RE = re.compile("|".join(_INJECTION), re.I)


def is_injection(sentence: str) -> bool:
    return bool(_INJ_RE.search(sentence))


def wrap_untrusted(text: str) -> str:
    """Delimit stakeholder text so prompts can tell data from instructions."""
    return "<untrusted_stakeholder_text>\n" + text.replace("</untrusted_stakeholder_text>", "") + "\n</untrusted_stakeholder_text>"
