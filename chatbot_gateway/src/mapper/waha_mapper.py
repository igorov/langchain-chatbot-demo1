from src.entities.chatbot_entities import WahaRequest
from typing import Dict, Any, Optional

def map_to_chatbot_payload(request: WahaRequest) -> Dict[str, str]:
    return {
        "question": request.payload.body,
        "user": request.payload.from_
    }

def map_to_send_text_payload(
    user: str, 
    response_text: str, 
    session: str,
    reply_to: Optional[str] = None,
    link_preview: bool = True,
    link_preview_high_quality: bool = False
) -> Dict[str, Any]:
    return {
        "chatId": user,
        "reply_to": reply_to,
        "text": response_text,
        "linkPreview": link_preview,
        "linkPreviewHighQuality": link_preview_high_quality,
        "session": session
    }
