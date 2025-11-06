from fastapi import APIRouter, HTTPException
from typing import List
from app.services.chat_service import chat_service
from app.models.chat import ChatMessage

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/messages", response_model=List[ChatMessage])
async def get_messages(limit: int = 100):
    """Get chat message history"""
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be positive")
    return chat_service.get_recent_messages(limit)

@router.delete("/messages")
async def clear_messages():
    """Clear all messages (for testing)"""
    chat_service.clear_history()
    return {"message": "Chat history cleared"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "active_connections": len(chat_service.get_message_history())
    }