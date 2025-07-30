from fastapi import APIRouter
import httpx
from src.entities.chatbot_entities import WahaRequest
from src.mapper.waha_mapper import map_to_chatbot_payload, map_to_send_text_payload
import os

router = APIRouter(prefix="/waha", tags=["waha"])

async def send_waha_message(user: str, message: str, session: str):
    """Send a message to WAHA API sendText endpoint"""
    try:
        payload = map_to_send_text_payload(user, message, session)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.getenv('WAHA_API_URL')}/api/sendText",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error sending message to WAHA: {str(e)}")
        return None


async def handle_error_response(request: WahaRequest, user_message: str, technical_message: str, chatbot_data=None):
    """Handle error response by sending WAHA message and returning error dict"""
    await send_waha_message(request.payload.from_, user_message, request.session)
    error_response = {"status": "error", "message": technical_message}
    if chatbot_data:
        error_response["chatbot_response"] = chatbot_data
    return error_response

@router.post("/webhook", summary="Process webhook")
async def chatbot_endpoint(request: WahaRequest):
    print(f"Received webhook request: {request}")
    try:
        chatbot_payload = map_to_chatbot_payload(request)
        
        # Call the chatbot API
        async with httpx.AsyncClient() as client:
            chatbot_response = await client.post(
                f"{os.getenv('CHATBOT_API_URL')}/api/chatbot",
                json=chatbot_payload,
                headers={"Content-Type": "application/json"}
            )
            chatbot_response.raise_for_status()
            chatbot_data = chatbot_response.json()
        
        # Validate chatbot API response
        if chatbot_response.status_code != 200 or chatbot_data.get("status") != "success":
            return await handle_error_response(
                request,
                "Lo siento, no puedo procesar tu mensaje en este momento. Por favor intenta nuevamente más tarde.",
                f"Chatbot API error - Status code: {chatbot_response.status_code}, Status: {chatbot_data.get('status', 'unknown')}",
                chatbot_data
            )
        
        response_text = chatbot_data.get("response", "")
        
        # Send the chatbot response to WAHA
        send_data = await send_waha_message(
            user=request.payload.from_,
            message=response_text,
            session=request.session
        )
        
        return {
            "status": "success",
            "message": "Message processed and sent successfully",
            "chatbot_response": chatbot_data,
            "send_response": send_data
        }
        
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {str(e)}")
        return await handle_error_response(
            request,
            "Lo siento, hay un problema de conexión. Por favor intenta nuevamente más tarde.",
            f"HTTP error occurred: {str(e)}"
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return await handle_error_response(
            request,
            "Lo siento, ocurrió un error inesperado. Por favor intenta nuevamente más tarde.",
            f"An error occurred: {str(e)}"
        )
