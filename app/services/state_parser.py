from __future__ import annotations

import re
from typing import Any, Dict, List

SENIORITY = ["intern", "junior", "mid", "senior", "lead", "manager", "director"]


def _extract_skills(text: str) -> List[str]:
    candidates = ["java", "python", "sql", "javascript", "stakeholder", "leadership", "personality", "cognitive"]
    return [s for s in candidates if s in text.lower()]


def parse_state(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "job_role": None,
        "seniority": None,
        "technical_skills": [],
        "personality_requirements": False,
        "cognitive_requirements": False,
        "leadership_requirements": False,
        "stakeholder_interaction_requirements": False,
        "refinement_edits": [],
        "comparison_requests": [],
    }

    for m in messages:
        if m.get("role") != "user":
            continue
        text = m.get("content", "")
        low = text.lower()

        role_match = re.search(r"hiring (an?|for)?\s*([a-zA-Z ]+?)(?: with|$)", low)
        if role_match:
            state["job_role"] = role_match.group(2).strip()

        for sen in SENIORITY:
            if sen in low:
                state["seniority"] = sen

        skills = _extract_skills(text)
        for s in skills:
            if s not in state["technical_skills"]:
                state["technical_skills"].append(s)

        if "personality" in low:
            state["personality_requirements"] = True
            if "actually" in low:
                state["refinement_edits"].append("add personality")
        if "cognitive" in low or "aptitude" in low:
            state["cognitive_requirements"] = True
        if "leadership" in low:
            state["leadership_requirements"] = True
        if "stakeholder" in low or "client facing" in low:
            state["stakeholder_interaction_requirements"] = True

        if "difference between" in low or "compare" in low:
            state["comparison_requests"].append(text)

    return state
