from __future__ import annotations

import re
from typing import Optional

INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"jailbreak",
    r"developer message",
    r"bypass",
]

OFF_TOPIC_PATTERNS = [
    r"salary",
    r"compensation",
    r"offer letter",
    r"employment law",
    r"lawsuit",
    r"visa",
    r"tax",
]


def detect_refusal_reason(text: str) -> Optional[str]:
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return "I can’t help with prompt-manipulation or unsafe instruction bypasses."
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, lowered):
            return "I can only help with SHL assessment recommendation and comparison tasks."
    return None
