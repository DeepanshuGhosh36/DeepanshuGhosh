from __future__ import annotations

from typing import Dict, List


def compare_assessments(names: List[str], candidates: List[Dict]) -> str:
    chosen = [c for c in candidates if any(n.lower() in c["name"].lower() for n in names)]
    if len(chosen) < 2:
        return "I can compare assessments once you specify at least two assessment names from the recommendations."
    lines = ["Here is a grounded comparison:"]
    for c in chosen:
        lines.append(f"- {c['name']}: type={c['test_type']}; focus={c.get('description','n/a')}")
    return "\n".join(lines)
