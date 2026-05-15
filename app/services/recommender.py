from __future__ import annotations

from typing import Any, Dict, List

from app.services.retriever import retrieve_assessments


def needs_clarification(state: Dict[str, Any]) -> bool:
    return not state.get("job_role") and not state.get("technical_skills")


def recommend(state: Dict[str, Any]) -> List[Dict[str, str]]:
    query_parts = [state.get("job_role") or "", " ".join(state.get("technical_skills", []))]
    if state.get("personality_requirements"):
        query_parts.append("personality")
    if state.get("cognitive_requirements"):
        query_parts.append("cognitive")
    return retrieve_assessments(" ".join(query_parts).strip(), top_k=10)
