from enum import Enum
from typing import Union, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os

class LLMProvider(Enum):
    NVIDIA = "nvidia"
    OPENAI = "openai"

class LLMFactory:
    def __init__(self):
        # Convertir temperature a float con valor por defecto
        temperature_str = os.getenv("MODEL_TEMPERATURE", "0.7")
        try:
            temperature = float(temperature_str)
        except (ValueError, TypeError):
            temperature = 0.7  # Valor por defecto
            
        self.default_configs = {
            LLMProvider.NVIDIA: {
                "model": "meta/llama-4-maverick-17b-128e-instruct",
                "temperature": temperature,
            },
            LLMProvider.OPENAI: {
                "model": "gpt-4o-mini",
                "temperature": temperature,
            }
        }
    
    def create_chat_model(
        self, 
        provider: Union[LLMProvider, str],
        model_name: Optional[str] = None,
        **kwargs
    ) -> Union[ChatNVIDIA, ChatOpenAI]:
        # Convertir string a enum si es necesario
        if isinstance(provider, str):
            provider = LLMProvider(provider.lower())
        
        # Obtener configuración por defecto
        config = self.default_configs[provider].copy()
        
        # Actualizar con parámetros personalizados
        config.update(kwargs)
        
        # Crear el modelo correspondiente
        if provider == LLMProvider.NVIDIA:
            if not os.getenv("NVIDIA_API_KEY"):
                raise ValueError("NVIDIA_API_KEY no está configurada. Asegúrate de definir esta variable de entorno en Cloud Run.")
            return ChatNVIDIA(**config)
        elif provider == LLMProvider.OPENAI:
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY no está configurada. Asegúrate de definir esta variable de entorno en Cloud Run.")
            try:
                return ChatOpenAI(**config)
            except Exception as e:
                raise ValueError(f"Error al crear ChatOpenAI con config {config}: {str(e)}")
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")