#!/bin/bash

# Script de inicio para Railway
set -e

echo "🚀 Iniciando aplicación Django en Railway..."

# Ejecutar migraciones
echo "📦 Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@ejemplo.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superusuario {username} creado exitosamente")
else:
    print("✅ Superusuario ya existe")
EOF

# Verificar configuración de OCR
echo "🔍 Verificando configuración de OCR..."
python -c "
import pytesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f'✅ Tesseract OCR versión: {version}')
except Exception as e:
    print(f'⚠️  Advertencia OCR: {e}')
"

# Verificar configuración de Face Recognition
echo "👁️  Verificando configuración de Face Recognition..."
python -c "
try:
    import face_recognition
    import cv2
    print('✅ OpenCV y Face Recognition configurados correctamente')
except Exception as e:
    print(f'⚠️  Advertencia Face Recognition: {e}')
"

echo "🎯 Configuración completada. Iniciando servidor..."

# Iniciar la aplicación
exec "$@"