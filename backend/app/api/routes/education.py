# app/api/routes/education.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.education_service import EducationService

router = APIRouter(prefix="/education", tags=["education"])

# Local dependency to extract clerk_user_id from authenticated user
async def get_clerk_user_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.clerk_user_id

class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None

@router.post("/chat")
async def chat_with_education_bot(
    request: ChatMessage,
    clerk_user_id: str = Depends(get_clerk_user_id)
) -> Dict[str, Any]:
    try:
        response = await EducationService.get_financial_education_response(
            user_question=request.message,
            clerk_user_id=clerk_user_id,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/suggested-topics")
async def get_suggested_topics() -> Dict[str, Any]:
    try:
        topics = await EducationService.get_suggested_topics()
        return {"success": True, "topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/history")
async def get_chat_history(
    limit: int = 20,
    clerk_user_id: str = Depends(get_clerk_user_id)
) -> Dict[str, Any]:
    try:
        history = await EducationService.get_chat_history(clerk_user_id, limit)
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")