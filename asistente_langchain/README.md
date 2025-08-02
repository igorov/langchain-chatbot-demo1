# Asistente Chatbot con LangChain

Este proyecto implementa un chatbot inteligente usando FastAPI y LangChain con memoria conversacional en RAM.

## Características

- **Memoria conversacional moderna**: Usa la implementación actual de LangChain con `RunnableWithMessageHistory`
- **Sin advertencias de deprecación**: Implementación actualizada que sigue las mejores prácticas de LangChain 0.3+
- **Múltiples proveedores LLM**: Soporte para OpenAI y NVIDIA
- **API REST**: Endpoints para interactuar con el chatbot
- **Gestión de historial**: Función para obtener el historial de conversaciones
- **Memoria en RAM**: Almacenamiento eficiente en memoria sin persistencia externa

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Crear archivo `.env` en la raíz del proyecto:
```bash
# Crear el archivo .env
touch .env
```

3. Configurar variables de entorno en el archivo `.env`:
```env
# Variables de entorno para el Asistente Chatbot

# Proveedor de modelo LLM (openai o nvidia)
MODEL_PROVIDER=openai

# Configuración para OpenAI
OPENAI_API_KEY=tu-openai-api-key-aqui

# Configuración para NVIDIA (opcional, solo si usas MODEL_PROVIDER=nvidia)
NVIDIA_API_KEY=tu-nvidia-api-key-aqui

# Temperatura del modelo (0.0 a 1.0)
MODEL_TEMPERATURE=0.7
```

**⚠️ Importante**: Reemplaza `tu-openai-api-key-aqui` con tu clave real de OpenAI.

## Uso

### Ejecutar el servidor
```bash
python -m src.main
```

El servidor estará disponible en `http://localhost:8080`

### Endpoints disponibles

#### 1. Enviar pregunta al chatbot
```http
POST /api/chatbot
Content-Type: application/json

{
    "question": "¡Hola! ¿Cómo estás?",
    "user": "usuario1"
}
```

**Respuesta:**
```json
{
    "user": "usuario1",
    "question": "¡Hola! ¿Cómo estás?",
    "response": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
    "timestamp": "2024-01-01T12:00:00",
    "status": "success"
}
```

#### 2. Obtener historial de conversación
```http
GET /api/chatbot/history?user=usuario1
```

**Respuesta:**
```json
{
    "user": "usuario1",
    "messages": [
        {
            "id": 0,
            "type": "human",
            "role": "user",
            "content": "¡Hola! ¿Cómo estás?",
            "timestamp": "2024-01-01T12:00:00"
        },
        {
            "id": 1,
            "type": "ai",
            "role": "assistant",
            "content": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
            "timestamp": "2024-01-01T12:00:01"
        }
    ],
    "total_messages": 2,
    "conversation_id": "user_usuario1",
    "status": "success"
}
```

## Arquitectura

### Componentes principales

- **ChatbotService**: Lógica principal del chatbot con `RunnableWithMessageHistory` moderno
- **InMemoryChatHistory**: Implementación personalizada de memoria de chat en RAM
- **ChatbotController**: Controlador que maneja las peticiones HTTP
- **ChatbotRouter**: Definición de rutas de la API
- **LLMFactory**: Factory para crear instancias de modelos LLM

### Memoria conversacional

El sistema utiliza `RunnableWithMessageHistory` de LangChain para:
- Mantener el historial completo de cada conversación por usuario
- Proporcionar contexto a las respuestas del modelo
- Permitir conversaciones coherentes y contextuales
- Seguir las mejores prácticas modernas de LangChain

La memoria se almacena en RAM usando `InMemoryChatHistory` personalizada (`self.chat_histories`), lo que significa que:
- ✅ Es rápida y eficiente
- ✅ No requiere configuración de base de datos externa
- ✅ Libre de advertencias de deprecación
- ✅ Compatible con LangChain 0.3+
- ⚠️ Se pierde al reiniciar el servidor
- ⚠️ No es escalable para múltiples instancias del servidor

### Tipos de mensajes en el historial

El sistema reconoce y muestra los tipos de mensajes de `langchain_core.messages`:

- **HumanMessage**: Mensajes del usuario
- **AIMessage**: Respuestas del asistente (incluye metadata y tool_calls si están disponibles)
- **SystemMessage**: Instrucciones del sistema (si existen en la memoria)
- **ToolMessage**: Resultados de herramientas (si existen en la memoria)

Cada mensaje en el historial incluye:
- `id`: Identificador único en la conversación
- `type` y `role`: Tipo de mensaje para compatibilidad
- `content`: Contenido del mensaje
- `timestamp`: Marca de tiempo
- Metadata adicional según el tipo de mensaje

## Ejemplo de uso

### Conversación con memoria
```python
# 1. Primera interacción
POST /api/chatbot
{
    "question": "Mi nombre es Juan y soy desarrollador Python",
    "user": "dev001"
}
# Respuesta: "¡Hola Juan! Es genial conocer a un desarrollador Python..."

# 2. Segunda interacción - el bot recuerda el contexto
POST /api/chatbot
{
    "question": "¿Cuál es mi nombre y profesión?",
    "user": "dev001"
}
# Respuesta: "Tu nombre es Juan y eres desarrollador Python, como me dijiste anteriormente."

# 3. Obtener historial completo
GET /api/chatbot/history?user=dev001
# Retorna toda la conversación con tipos de mensajes estructurados
```

### Flujo típico de uso
1. **Enviar preguntas**: El usuario hace preguntas al chatbot
2. **Memoria automática**: El sistema mantiene automáticamente el contexto de la conversación
3. **Consultar historial**: Se puede obtener el historial completo de la conversación cuando sea necesario

El bot mantendrá toda la información y contexto de conversaciones anteriores automáticamente.

## Actualización técnica

Esta implementación ha sido actualizada de las clases deprecadas de LangChain 0.0.x a la implementación moderna:

### Antes (deprecado):
- `ConversationChain` ❌
- `ConversationBufferMemory` ❌  
- Advertencias de deprecación ❌

### Ahora (moderno):
- `RunnableWithMessageHistory` ✅
- `InMemoryChatHistory` personalizada ✅
- Compatible con LangChain 0.3+ ✅
- Sin advertencias de deprecación ✅

## Despliegue en Google Cloud Run

### Construcción y despliegue

1. **Construir la imagen Docker**:
```bash
docker build -t gcr.io/tu-proyecto/chatbot-langchain .
```

2. **Subir la imagen a Container Registry**:
```bash
docker push gcr.io/tu-proyecto/chatbot-langchain
```

3. **Desplegar en Cloud Run**:
```bash
gcloud run deploy chatbot-langchain \
  --image gcr.io/tu-proyecto/chatbot-langchain \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "MODEL_PROVIDER=openai,MODEL_TEMPERATURE=0.7,OPENAI_API_KEY=tu-api-key-aqui"
```

### Variables de entorno requeridas en Cloud Run

**Para OpenAI (recomendado)**:
```bash
MODEL_PROVIDER=openai
MODEL_TEMPERATURE=0.7
OPENAI_API_KEY=tu-openai-api-key-aqui
```

**Para NVIDIA**:
```bash
MODEL_PROVIDER=nvidia
MODEL_TEMPERATURE=0.7
NVIDIA_API_KEY=tu-nvidia-api-key-aqui
```

### Configuración desde la Consola de Google Cloud

1. Ve a Cloud Run en Google Cloud Console
2. Selecciona tu servicio
3. Haz clic en "Editar y desplegar nueva revisión"
4. En la pestaña "Variables y secretos", agrega:
   - `OPENAI_API_KEY`: Tu clave de API de OpenAI
   - `MODEL_PROVIDER`: `openai` (o `nvidia`)
   - `MODEL_TEMPERATURE`: `0.7`

### Solución de problemas comunes

**Error de validación de Pydantic**:
- Asegúrate de que `MODEL_TEMPERATURE` sea un número (ej: `0.7`, no `"0.7"`)
- Verifica que `OPENAI_API_KEY` esté correctamente configurada

**Error de API Key faltante**:
```
OPENAI_API_KEY no está configurada. Asegúrate de definir esta variable de entorno en Cloud Run.
```
- Configura la variable `OPENAI_API_KEY` en Cloud Run con tu clave real de OpenAI

## Documentación API

Una vez ejecutado el servidor, la documentación interactiva estará disponible en:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc` 