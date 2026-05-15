from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_engine import run_chat
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        return run_chat([m.model_dump() for m in request.messages])
    except Exception as exc:
        logger.exception("chat endpoint failed: %s", exc)
        return ChatResponse(reply="Internal error occurred", recommendations=[], end_of_conversation=False)
