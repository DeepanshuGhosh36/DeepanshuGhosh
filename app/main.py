from fastapi import FastAPI

from app.routes.chat import router as chat_router
from app.services.retriever import load_catalog, load_index

app = FastAPI(title="SHL Recommendation Agent", version="1.0.0")


@app.on_event("startup")
async def startup_event() -> None:
    load_catalog()
    load_index()


@app.get("/health")
async def health() -> dict:
    try:
        return {"status": "ok"}
    except Exception:
        return {"status": "ok"}


app.include_router(chat_router)
