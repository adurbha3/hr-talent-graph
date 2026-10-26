"""Extract known skills from free-form job or self-assessment text: exact
phrase matching against the skill ontology's controlled vocabulary, with a
fuzzy-matching fallback for near-miss wording (abbreviations, typos,
reordered words) -- a lightweight form of the entity-linking-against-a-
controlled-vocabulary problem a semantic layer is built to solve.
"""
from __future__ import annotations

import difflib
import re

from talentgraph.synthetic_data import SKILLS

_ABBREVIATIONS = {
    "ml": "machine learning",
    "pm": "project management",
    "ppt": "powerpoint",
}


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_skills(text: str, fuzzy_cutoff: float = 0.8) -> list[str]:
    """Return every known skill mentioned in text, exact matches first (in
    vocabulary order), then any additional skills found only via fuzzy
    matching on individual words/abbreviations."""
    normalized = _normalize(text)
    words = normalized.split()

    found = []
    for skill in SKILLS:
        if skill in normalized and skill not in found:
            found.append(skill)

    for word in words:
        expanded = _ABBREVIATIONS.get(word)
        if expanded and expanded not in found:
            found.append(expanded)
            continue
        close = difflib.get_close_matches(word, SKILLS, n=1, cutoff=fuzzy_cutoff)
        if close and close[0] not in found:
            found.append(close[0])

    return found
