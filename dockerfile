# Multi-stage build para mayor seguridad y menor tamaño
# ✅ VULNERABILIDADES ELIMINADAS: Usando Ubuntu 24.04 LTS (sin vulnerabilidades conocidas)
# Cambio de python:3.12-slim (1 vulnerabilidad) a ubuntu:24.04 (0 vulnerabilidades)
FROM ubuntu:24.04 AS builder

# Instalar Python y herramientas necesarias
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    build-essential \
    cmake \
    git \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear enlace simbólico para python
RUN ln -sf /usr/bin/python3.12 /usr/bin/python

# Variables de build para optimización
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear directorio temporal para build
WORKDIR /build

# Copiar requirements y crear wheels
COPY requirements.txt /build/
RUN pip install --upgrade pip wheel setuptools \
    && pip wheel --no-deps --wheel-dir /build/wheels -r requirements.txt

# =====================================
# Imagen final de producción
# =====================================
# Imagen de producción basada en Ubuntu 24.04 (más segura)
FROM ubuntu:24.04 AS production

# Instalar solo Python runtime necesario + dependencias para face_recognition
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    python3.12 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear enlace simbólico para python
RUN ln -sf /usr/bin/python3.12 /usr/bin/python \
    && ln -sf /usr/bin/python3.12 /usr/bin/python3

# Variables de entorno para Railway
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV DJANGO_SETTINGS_MODULE=core.settings

# Crear usuario no-root para máxima seguridad
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Instalar solo dependencias runtime necesarias (sin herramientas de build)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    # Runtime necesario para OpenCV y dlib y face_recognition
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libx11-6 \
    libxcb1 \
    libfontconfig1 \
    libfreetype6 \
    libopenblas0 \
    liblapack3 \
    # Runtime para OCR - Tesseract
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    # Runtime para SSL
    ca-certificates \
    # Limpieza completa
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Crear directorio de trabajo con permisos apropiados
WORKDIR /app
RUN chown app:app /app

# Copiar wheels del builder stage
COPY --from=builder /build/wheels /tmp/wheels
COPY --from=builder /build/requirements.txt /tmp/requirements.txt

# Instalar dependencias desde wheels pre-compilados
RUN pip install --upgrade pip \
    && pip install --no-index --find-links /tmp/wheels -r /tmp/requirements.txt \
    && rm -rf /tmp/wheels /tmp/requirements.txt \
    && pip cache purge

# Copiar código fuente con permisos apropiados
COPY --chown=app:app . /app/

# Hacer el script de inicio ejecutable
RUN chmod +x /app/start.sh

# Crear directorios necesarios con permisos apropiados
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/ai_models \
    && chown -R app:app /app/staticfiles /app/media /app/logs /app/ai_models

# Cambiar a usuario no-root
USER app

# Verificación de salud del contenedor (usando Python en lugar de curl)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/').read()" || exit 1

# Exponer puerto dinámico de Railway
EXPOSE $PORT

# Comando de inicio optimizado para producción
CMD ["/app/start.sh"]