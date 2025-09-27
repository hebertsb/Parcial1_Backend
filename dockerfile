FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libssl-dev \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
    libboost-all-dev \
    git \
    curl \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos
COPY requirements.txt /app/requirements.txt

WORKDIR /app

# Instalar dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código fuente
COPY . /app

# Exponer el puerto (ajusta si usas otro)
EXPOSE 8000

# Comando para lanzar el servidor (ajusta si usas gunicorn, etc.)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]