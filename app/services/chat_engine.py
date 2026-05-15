from __future__ import annotations

import os
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.models.schemas import ChatResponse, Recommendation
from app.services.comparator import compare_assessments
from app.services.guardrails import detect_refusal_reason
from app.services.recommender import needs_clarification, recommend
from app.services.state_parser import parse_state


def _gemini_reply(system_text: str, user_text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return user_text
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=api_key)
    prompt = ChatPromptTemplate.from_messages([("system", system_text), ("human", "{input}")])
    return (prompt | llm).invoke({"input": user_text}).content


def run_chat(messages: List[Dict[str, str]]) -> ChatResponse:
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    refusal = detect_refusal_reason(last_user)
    if refusal:
        return ChatResponse(reply=refusal, recommendations=[], end_of_conversation=False)

    state = parse_state(messages)

    if state["comparison_requests"]:
        recs = recommend(state)
        names = [w.strip("?.!,") for w in last_user.split() if w.lower() not in {"what", "is", "the", "difference", "between", "and"}]
        reply = compare_assessments(names, recs)
        return ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)

    if needs_clarification(state):
        text = "What role are you hiring for, and which skills or traits (technical, cognitive, personality, leadership) matter most?"
        reply = _gemini_reply("You are a concise SHL assistant.", text)
        return ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)

    recs = recommend(state)
    if not recs:
        return ChatResponse(reply="I couldn’t find catalog-grounded SHL assessments yet. Please run the scraper/index pipeline and retry.", recommendations=[], end_of_conversation=False)

    reply = _gemini_reply(
        "You are a concise SHL assistant. Explain that recommendations are grounded in catalog entries only.",
        "I selected assessments based on your role and requirement details.",
    )
    return ChatResponse(
        reply=reply,
        recommendations=[Recommendation(name=r["name"], url=r["url"], test_type=r["test_type"]) for r in recs[:10]],
        end_of_conversation=False,
    )
