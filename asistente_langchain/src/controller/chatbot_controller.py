from fastapi import HTTPException
from typing import Dict, Any
from src.service.chatbot_service import ChatbotService
from src.entities.chatbot_entities import ChatbotRequest

class ChatbotController:
    
    def __init__(self):
        self.chatbot_service = ChatbotService()
    
    async def process_chatbot_request(self, request: ChatbotRequest) -> Dict[str, Any]:
        try:
            return await self.chatbot_service.process_question(
                question=request.question,
                user=request.user
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

    async def get_chat_history(self, user: str) -> Dict[str, Any]:
        try:
            return await self.chatbot_service.get_chat_history(user)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")
    
