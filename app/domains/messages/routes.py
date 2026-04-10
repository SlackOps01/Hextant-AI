from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from app.core.deps import get_current_user, get_db
from app.core.oauth2 import TokenData
from sqlalchemy.orm import Session
from app.domains.messages.service import MessageService
from app.domains.messages.schemas import MessageCreate


router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.post("/{conversation_id}", status_code=status.HTTP_200_OK)
async def create_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Pre-flight validation — raises normal HTTP exceptions (404, 400)
    # before the stream starts, so clients get proper error responses.
    agent, message_parts, message_history, user_message, deps, conv_id, model_id = (
        await MessageService.validate_and_prepare(
            conversation_id=conversation_id,
            data=data,
            db=db,
            current_user=current_user,
        )
    )

    # Return SSE stream
    return StreamingResponse(
        MessageService.stream_response(
            agent=agent,
            message_parts=message_parts,
            message_history=message_history,
            user_message=user_message,
            deps=deps,
            conversation_id=conv_id,
            model_id=model_id,
            db=db,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
def list_messages(
    conversation_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MessageService.list_messages(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )
