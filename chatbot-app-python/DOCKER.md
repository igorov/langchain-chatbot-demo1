# Docker Setup para Chatbot App Python

Este documento contiene las instrucciones para construir y ejecutar la aplicación de chatbot usando Docker.

## Prerrequisitos

- Docker instalado en tu sistema
- Docker Compose (opcional, pero recomendado)

## Construcción y Ejecución

### Opción 1: Usando Docker directamente

1. **Construir la imagen**:
   ```bash
   docker build -t chatbot-app-python .
   ```

2. **Ejecutar el contenedor**:
   ```bash
   docker run -d \
     --name chatbot-app \
     -p 5000:5000 \
     -e CHATBOT_API_BASE_URL=http://localhost:8080 \
     -e SECRET_KEY=chatbot-secret-key-2025 \
     chatbot-app-python
   ```

3. **Ver logs del contenedor**:
   ```bash
   docker logs chatbot-app
   ```

4. **Acceder a la aplicación**:
   - Abrir navegador en: http://localhost:5000

### Opción 2: Usando Docker Compose (Recomendado)

1. **Construir y ejecutar**:
   ```bash
   docker-compose up -d --build
   ```

2. **Ver logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Detener la aplicación**:
   ```bash
   docker-compose down
   ```

4. **Acceder a la aplicación**:
   - Abrir navegador en: http://localhost:5000

## Variables de Entorno

Las siguientes variables de entorno pueden ser configuradas:

- `CHATBOT_API_BASE_URL`: URL base de la API externa del chatbot (default: http://localhost:8080)
- `SECRET_KEY`: Clave secreta para las sesiones de Flask

## Configuración de Red

Si necesitas que el contenedor se comunique con otros servicios:

### Para API externa en el host
```bash
docker run -d \
  --name chatbot-app \
  -p 5000:5000 \
  -e CHATBOT_API_BASE_URL=http://host.docker.internal:8080 \
  chatbot-app-python
```

### Para API externa en otro contenedor
```yaml
# docker-compose.yml
version: '3.8'
services:
  chatbot-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - CHATBOT_API_BASE_URL=http://external-api:8080
    depends_on:
      - external-api
    networks:
      - chatbot-network

  external-api:
    # Configuración de tu API externa
    networks:
      - chatbot-network

networks:
  chatbot-network:
    driver: bridge
```

## Comandos Útiles

### Gestión de Contenedores
```bash
# Ver contenedores en ejecución
docker ps

# Detener contenedor
docker stop chatbot-app

# Eliminar contenedor
docker rm chatbot-app

# Ver logs en tiempo real
docker logs -f chatbot-app
```

### Gestión de Imágenes
```bash
# Listar imágenes
docker images

# Eliminar imagen
docker rmi chatbot-app-python

# Limpiar imágenes no utilizadas
docker image prune
```

### Acceso al Contenedor
```bash
# Ejecutar bash dentro del contenedor
docker exec -it chatbot-app bash

# Ver archivos del contenedor
docker exec chatbot-app ls -la /app
```

## Troubleshooting

### Error de conexión a la API externa
- Verificar que `CHATBOT_API_BASE_URL` esté configurado correctamente
- Si la API está en el host, usar `http://host.docker.internal:8080`
- Verificar que la API externa esté ejecutándose

### Puerto ya en uso
```bash
# Cambiar el puerto del host
docker run -p 8080:5000 chatbot-app-python
```

### Ver logs detallados
```bash
# Logs con timestamps
docker logs -t chatbot-app

# Últimas 100 líneas de logs
docker logs --tail 100 chatbot-app
```

## Optimizaciones de Producción

Para producción, considera estas modificaciones:

1. **Usar un servidor WSGI como Gunicorn**:
   ```dockerfile
   # En el Dockerfile, cambiar la última línea por:
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
   ```

2. **Configurar variables de entorno de producción**:
   ```bash
   docker run -d \
     -e FLASK_ENV=production \
     -e SECRET_KEY=tu-clave-secreta-muy-segura \
     chatbot-app-python
   ```

3. **Usar volúmenes para persistencia** (si es necesario):
   ```bash
   docker run -d \
     -v /host/path/logs:/app/logs \
     chatbot-app-python
   ```
