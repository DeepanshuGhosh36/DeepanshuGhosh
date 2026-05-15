# Approach Document

## Architecture Decisions
The solution uses modular clean architecture: routes (I/O), schemas (contracts), services (business logic), and data/prompts/utilities. Statelessness is enforced by reconstructing user intent solely from request message history.

## Retrieval Design
A lightweight retriever combines keyword ranking and optional FAISS semantic search artifacts generated offline. Startup loads catalog/index once for low-latency request handling and low memory overhead on Railway free tier.

## Why Gemini + FAISS + LangChain
- **Gemini free tier**: cost-effective conversational phrasing and concise clarification/comparison output.
- **FAISS**: memory-efficient local similarity index with fast top-k retrieval.
- **LangChain**: minimal orchestration layer for prompt + deterministic LLM invocation.

Gemini is intentionally excluded from retrieval/ranking to prevent hallucinated recommendations.

## Evaluation Strategy
Unit/API tests validate schema behavior, clarification, recommendation path, refinement handling, comparison flow, and refusal flow. Runtime fallback ensures stable response envelope on exceptions.

## Optimization Decisions
- No scraping during startup
- No embedding generation during requests
- Global load of catalog/index once
- No pandas usage
- Avoid repeated heavy model initialization except optional Gemini phrasing step

## Failure Cases Encountered
- Empty catalog can yield no recommendations. Handled by user-facing grounded message to run scraper/index pipeline.
- Catalog schema drift from SHL webpage changes. Scraper is defensive and retry-enabled.

## Improvements Made
- Added guardrails for prompt injection/off-topic requests
- Added strict pydantic validation with bounded lengths/counts
- Added robust try/except in route

## Deployment Strategy
Containerized deployment with slim Python 3.11 base, Railway-compatible startup command, and environment-based configuration. Service is ready for Railway free tier operation.
