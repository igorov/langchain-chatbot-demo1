from typing import Dict, Any
import os
import datetime
from src.llm.llm_factory import LLMFactory
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from pydantic import BaseModel, Field

class InMemoryChatHistory(BaseChatMessageHistory, BaseModel):
    """Implementación de memoria de chat en RAM"""
    
    messages: list = Field(default_factory=list)

    def add_messages(self, messages):
        """Agrega mensajes a la memoria"""
        self.messages.extend(messages)

    def clear(self):
        """Limpia la memoria"""
        self.messages = []

class ChatbotService:
    def __init__(self):
        self.llm = LLMFactory().create_chat_model(os.getenv('MODEL_PROVIDER', 'openai'))
        # Diccionario para almacenar historiales de chat por usuario en RAM
        self.chat_histories: Dict[str, InMemoryChatHistory] = {}
        
        # Template para el prompt de conversación 
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente útil y amigable. Responde de manera clara y concisa. Mantén el contexto de la conversación y recuerda información importante que el usuario comparta contigo."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Crear la cadena básica
        self.chain = self.prompt | self.llm

    def _get_user_memory(self, user: str) -> InMemoryChatHistory:
        """Obtiene o crea la memoria para un usuario específico"""
        if user not in self.chat_histories:
            self.chat_histories[user] = InMemoryChatHistory()
        return self.chat_histories[user]
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Función requerida para RunnableWithMessageHistory"""
        return self._get_user_memory(session_id)

    async def process_question(self, question: str, user: str) -> Dict[str, Any]:
        """Procesa una pregunta del usuario y mantiene el historial de conversación"""
        try:
            # Crear la cadena con historial
            chain_with_history = RunnableWithMessageHistory(
                self.chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="history",
            )
            
            # Procesar la pregunta
            response = await chain_with_history.ainvoke(
                {"input": question},
                config={"configurable": {"session_id": user}}
            )
            
            return {
                "user": user,
                "question": question,
                "response": response.content,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "user": user,
                "question": question,
                "response": f"Error al procesar la pregunta: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "error"
            }
    
    async def get_chat_history(self, user: str) -> Dict[str, Any]:
        """Obtiene el historial de chat para un usuario específico"""
        try:
            chat_history = self._get_user_memory(user)
            
            # Convertir los mensajes a un formato más legible
            messages = []
            for i, message in enumerate(chat_history.messages):
                message_data = {
                    "id": i,
                    "content": message.content,
                    "timestamp": getattr(message, 'timestamp', datetime.datetime.now().isoformat())
                }
                
                if isinstance(message, HumanMessage):
                    message_data["role"] = "user"
                elif isinstance(message, AIMessage):
                    message_data["role"] = "assistant"
                else:
                    message_data["role"] = "unknown"
                    message_data["message_type"] = type(message).__name__

                messages.append(message_data)
            
            return {
                "user": user,
                "messages": messages,
                "total_messages": len(messages),
                "conversation_id": f"user_{user}",
                "status": "success"
            }
            
        except Exception as e:
            return {
                "user": user,
                "messages": [],
                "total_messages": 0,
                "error": str(e),
                "status": "error"
            }