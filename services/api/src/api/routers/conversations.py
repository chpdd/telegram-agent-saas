from core.dependencies import get_db_session
from fastapi import APIRouter, Depends
from schemas.conversation import ConversationMessageRequest, ConversationMessageResponse
from services.conversation import run_conversation_turn
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/{conversation_id}/messages", response_model=ConversationMessageResponse)
async def create_conversation_message(
    conversation_id: str,
    payload: ConversationMessageRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> ConversationMessageResponse:
    result = await run_conversation_turn(
        session,
        tenant_id=payload.tenant_id,
        chat_id=payload.chat_id,
        conversation_id=conversation_id,
        user_content=payload.content,
        model=payload.model,
        system_prompt=payload.system_prompt,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        extra=payload.extra,
    )
    return ConversationMessageResponse.model_validate(result)
