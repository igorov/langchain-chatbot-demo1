# Chatbot App Python

Una aplicación de chatbot desarrollada en Python con Flask que replica la funcionalidad y diseño de la aplicación original de Next.js.

## Tecnologías Utilizadas

### Backend
- **Flask**: Framework web de Python
- **API Externa**: Se conecta a una API de chatbot externa (configurable)
- **Requests**: Para realizar llamadas HTTP a la API externa
- **Flask-CORS**: Para manejar CORS
- **python-dotenv**: Para variables de entorno

### Frontend
- **HTML5 & CSS3**: Estructura y estilos
- **JavaScript (ES6+)**: Lógica del frontend
- **Tailwind CSS**: Framework de CSS para estilos
- **Font Awesome**: Iconos

## Uso

1. **Ejecutar la aplicación**:
   ```bash
   python app.py
   ```

2. **Abrir en el navegador**:
   - Navegar a `http://localhost:5000`

3. **Usar la aplicación**:
   - Ingresar tu nombre en la pantalla de login
   - Comenzar a chatear con el asistente AI
   - Usar los botones de la interfaz para gestionar el chat

## Estructura del Proyecto

```
chatbot-app-python/
├── app.py                 # Aplicación principal de Flask
├── requirements.txt       # Dependencias de Python
├── .env.example          # Ejemplo de variables de entorno
├── README.md             # Este archivo
├── templates/
│   └── index.html        # Plantilla HTML principal
└── static/
    ├── css/
    │   └── styles.css    # Estilos personalizados
    └── js/
        └── app.js        # Lógica del frontend
```

## API Endpoints

- `GET /` - Página principal
- `POST /api/login` - Iniciar sesión con nombre de usuario
- `POST /api/logout` - Cerrar sesión
- `POST /api/chat` - Enviar mensaje al chatbot
- `GET /api/history` - Obtener historial de chat
- `POST /api/clear-history` - Limpiar historial de chat

## Configuración de la API Externa

Esta aplicación se conecta a una API de chatbot externa. Los endpoints utilizados son:

### Endpoints de la API Externa

**1. Enviar mensaje al chatbot:**
```
POST {CHATBOT_API_BASE_URL}/api/chatbot
```
Request body:
```json
{
    "question": "¡Hola! ¿Cómo estás?",
    "user": "usuario1"
}
```
Response:
```json
{
    "user": "usuario1",
    "question": "¡Hola! ¿Cómo estás?",
    "response": "¡Hola! Estoy muy bien, gracias por preguntar.",
    "timestamp": "2025-07-25T17:54:52.831627",
    "status": "success"
}
```

**2. Obtener historial de chat:**
```
GET {CHATBOT_API_BASE_URL}/api/chatbot/history?user=usuario1
```
Response:
```json
{
    "user": "usuario1",
    "messages": [
        {
            "id": 0,
            "content": "¡Hola! ¿Cómo estás?",
            "timestamp": "2025-07-25T17:54:57.119722",
            "role": "user"
        },
        {
            "id": 1,
            "content": "¡Hola! Estoy muy bien, gracias por preguntar.",
            "timestamp": "2025-07-25T17:54:57.119722",
            "role": "assistant"
        }
    ],
    "total_messages": 2,
    "conversation_id": "user_usuario1",
    "status": "success"
}
```

### Configuración

Para configurar la URL de la API externa, edita el archivo `.env`:
```
CHATBOT_API_BASE_URL=http://localhost:8080
```

**Nota:** Asegúrate de que la API externa esté ejecutándose en la URL configurada antes de usar la aplicación.
