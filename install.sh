#!/bin/bash
# ===================================
# Script de Instalación Automática
# Sistema de Reconocimiento Facial IA
# ===================================

set -e  # Salir si hay errores

echo "🚀 Iniciando instalación del Sistema de IA..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Verificar Python
echo ""
print_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python encontrado: $PYTHON_VERSION"
else
    print_error "Python 3 no encontrado. Instala Python 3.12 o superior."
    exit 1
fi

# 2. Verificar pip
if command -v pip3 &> /dev/null; then
    print_status "pip3 encontrado"
else
    print_error "pip3 no encontrado. Instala pip3."
    exit 1
fi

# 3. Crear entorno virtual
echo ""
print_info "Creando entorno virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_status "Entorno virtual creado"
else
    print_warning "Entorno virtual ya existe"
fi

# 4. Activar entorno virtual
print_info "Activando entorno virtual..."
source .venv/bin/activate
print_status "Entorno virtual activado"

# 5. Actualizar pip
print_info "Actualizando pip..."
pip install --upgrade pip
print_status "pip actualizado"

# 6. Instalar dependencias del sistema (Ubuntu/Debian)
echo ""
print_info "Verificando dependencias del sistema..."
if command -v apt-get &> /dev/null; then
    print_info "Sistema Ubuntu/Debian detectado"
    print_warning "Es posible que necesites ejecutar con sudo para instalar dependencias del sistema"
    
    # Lista de paquetes necesarios
    PACKAGES="python3-dev build-essential cmake libopenblas-dev liblapack-dev libgl1-mesa-glx libglib2.0-0 tesseract-ocr tesseract-ocr-spa"
    
    echo "Ejecuta el siguiente comando para instalar dependencias del sistema:"
    echo "sudo apt-get update && sudo apt-get install -y $PACKAGES"
    echo ""
    read -p "¿Ya tienes las dependencias del sistema instaladas? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Por favor instala las dependencias del sistema antes de continuar"
        exit 1
    fi
else
    print_warning "Sistema no Ubuntu/Debian. Verifica manualmente las dependencias."
fi

# 7. Instalar dependencias Python
echo ""
print_info "Instalando dependencias Python..."
pip install -r requirements.txt
print_status "Dependencias Python instaladas"

# 8. Configurar variables de entorno
echo ""
print_info "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Archivo .env creado desde .env.example"
        print_warning "¡IMPORTANTE! Edita .env y configura tus variables"
        print_warning "Especialmente DROPBOX_ACCESS_TOKEN es obligatorio"
    else
        print_error "No se encontró .env.example"
        exit 1
    fi
else
    print_warning "Archivo .env ya existe"
fi

# 9. Ejecutar migraciones
echo ""
print_info "Ejecutando migraciones de base de datos..."
python manage.py migrate
print_status "Migraciones completadas"

# 10. Crear superusuario (opcional)
echo ""
read -p "¿Quieres crear un superusuario ahora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
    print_status "Superusuario creado"
fi

# 11. Verificar instalación
echo ""
print_info "Verificando instalación..."
python manage.py check
print_status "Verificación completada"

# 12. Instrucciones finales
echo ""
echo "=================================================="
print_status "¡Instalación completada exitosamente! 🎉"
echo "=================================================="
echo ""
print_info "Próximos pasos:"
echo "1. Edita el archivo .env con tus configuraciones"
echo "2. Configura DROPBOX_ACCESS_TOKEN (obligatorio)"
echo "3. Ejecuta: python manage.py runserver"
echo "4. Visita: http://localhost:8000"
echo ""
print_info "Para activar el entorno virtual en el futuro:"
echo "source .venv/bin/activate"
echo ""
print_info "Documentación completa en README.md"
echo ""
print_status "¡Disfruta tu sistema de IA! 🤖"