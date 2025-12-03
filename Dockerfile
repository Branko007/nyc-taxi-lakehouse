# 1. Imagen Base: Python 3.10 slim (Ligera y segura)
FROM python:3.10-slim

# 2. Variables de entorno para Python y uv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# 3. Instalar dependencias del sistema mínimas (curl para instalar uv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalar uv (Gestor de paquetes moderno)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 5. Configurar directorio de trabajo
WORKDIR /app

# 6. Copiar archivos de dependencias primero (Cache Layering)
COPY pyproject.toml uv.lock ./

# 7. Instalar dependencias del proyecto usando uv
# --system instala en el python global del contenedor (correcto para Docker)
RUN uv pip install --system -r pyproject.toml

# 8. Copiar el código fuente
COPY src/ ./src/

# 9. Punto de entrada (Entrypoint)
# Por defecto ejecuta el script, pero espera argumentos
ENTRYPOINT ["python", "src/ingestion/ingest_manager.py"]