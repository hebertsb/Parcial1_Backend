#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}🚀 INSTALADOR AUTOMATICO - Sistema de Reconocimiento Facial${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERROR: Python3 no está instalado${NC}"
    echo ""
    echo -e "${YELLOW}📋 Instrucciones de instalación:${NC}"
    echo "• Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "• macOS: brew install python3"
    echo "• CentOS/RHEL: sudo yum install python3 python3-pip"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Python detectado${NC}"
python3 --version

# Verificar si pip está disponible
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ ERROR: pip3 no está disponible${NC}"
    echo -e "${YELLOW}Instalar con: sudo apt install python3-pip (Ubuntu) o brew install python3 (macOS)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ pip disponible${NC}"
echo ""

# Crear entorno virtual
echo -e "${BLUE}📦 Creando entorno virtual...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: No se pudo crear el entorno virtual${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Entorno virtual creado${NC}"
echo ""

# Activar entorno virtual
echo -e "${BLUE}🔄 Activando entorno virtual...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: No se pudo activar el entorno virtual${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Entorno virtual activado${NC}"
echo ""

# Actualizar pip
echo -e "${BLUE}📈 Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias
echo -e "${BLUE}📚 Instalando dependencias...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: No se pudieron instalar las dependencias${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Intentando instalación alternativa...${NC}"
    pip install Django==5.2.6 djangorestframework djangorestframework-simplejwt drf-spectacular Pillow python-dotenv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ERROR: Instalación fallida. Revisar requirements.txt${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo ""

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creando archivo de configuración...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado desde .env.example${NC}"
else
    echo -e "${YELLOW}ℹ️  Archivo .env ya existe${NC}"
fi
echo ""

# Ejecutar migraciones
echo -e "${BLUE}🗄️  Ejecutando migraciones...${NC}"
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Fallo en migraciones${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Migraciones completadas${NC}"
echo ""

# Crear usuarios del sistema
echo -e "${BLUE}👥 Creando usuarios del sistema...${NC}"
python manage.py crear_usuarios_facial
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: No se pudieron crear usuarios automáticamente${NC}"
    echo "   Puedes crearlos manualmente después con: python manage.py crear_usuarios_facial"
else
    echo -e "${GREEN}✅ Usuarios creados exitosamente${NC}"
fi
echo ""

# Crear datos de prueba (opcional)
echo -e "${PURPLE}🧪 ¿Quieres crear datos de prueba? (s/n)${NC}"
read -r create_test_data
if [[ $create_test_data == "s" || $create_test_data == "S" ]]; then
    echo -e "${BLUE}📊 Creando datos de prueba...${NC}"
    python manage.py create_test_data
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  WARNING: No se pudieron crear datos de prueba${NC}"
    else
        echo -e "${GREEN}✅ Datos de prueba creados${NC}"
    fi
fi
echo ""

# Verificar instalación
echo -e "${BLUE}🧪 Verificando instalación...${NC}"
python manage.py check
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: La verificación del sistema falló${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Verificación completada${NC}"
echo ""

echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
echo -e "${WHITE}📋 CREDENCIALES POR DEFECTO:${NC}"
echo -e "┌─────────────────┬─────────────────────────────┬─────────────────┐"
echo -e "│ ROL             │ EMAIL                       │ PASSWORD        │"
echo -e "├─────────────────┼─────────────────────────────┼─────────────────┤"
echo -e "│ 👑 Administrador │ admin@facial.com           │ admin123        │"
echo -e "│ 🛡️  Seguridad    │ seguridad@facial.com       │ seguridad123    │"
echo -e "│ 🏠 Propietario   │ maria.gonzalez@facial.com  │ propietario123  │"
echo -e "│ 🔑 Inquilino     │ carlos.rodriguez@facial.com│ inquilino123    │"
echo -e "└─────────────────┴─────────────────────────────┴─────────────────┘"
echo ""
echo -e "${WHITE}🌐 URLs IMPORTANTES:${NC}"
echo -e "  • Servidor:        ${CYAN}http://127.0.0.1:8000${NC}"
echo -e "  • Admin Panel:     ${CYAN}http://127.0.0.1:8000/admin/${NC}"
echo -e "  • API Docs:        ${CYAN}http://127.0.0.1:8000/api/docs/${NC}"
echo -e "  • Login API:       ${CYAN}http://127.0.0.1:8000/api/auth/login/${NC}"
echo ""
echo -e "${WHITE}🚀 PARA INICIAR EL SERVIDOR:${NC}"
echo -e "  1. ${YELLOW}python manage.py runserver${NC}"
echo -e "  2. Abrir navegador en: ${CYAN}http://127.0.0.1:8000${NC}"
echo ""
echo -e "${WHITE}📚 DOCUMENTACIÓN:${NC}"
echo -e "  • Ver ${YELLOW}INSTALLATION_GUIDE.md${NC} para más detalles"
echo -e "  • Ver ${YELLOW}POSTMAN_AUTHZ_GUIDE.md${NC} para probar la API"
echo ""
echo -e "${YELLOW}⚠️  NOTA: El reconocimiento facial está en modo SIMULADO${NC}"
echo -e "   Para modo real, ver INSTALLATION_GUIDE.md sección \"Instalación Avanzada\""
echo ""
echo -e "${PURPLE}¿Quieres iniciar el servidor ahora? (s/n)${NC}"
read -r start_server
if [[ $start_server == "s" || $start_server == "S" ]]; then
    echo ""
    echo -e "${GREEN}🚀 Iniciando servidor...${NC}"
    python manage.py runserver
else
    echo ""
    echo -e "${GREEN}🎯 Sistema listo. Para iniciar: ${YELLOW}python manage.py runserver${NC}"
fi