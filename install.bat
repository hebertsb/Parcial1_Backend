@echo off
REM ===================================
REM Script de Instalación - Windows
REM Sistema de Reconocimiento Facial IA
REM ===================================

echo 🚀 Iniciando instalación del Sistema de IA...
echo ==================================================

REM 1. Verificar Python
echo.
echo ℹ️  Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.12 o superior.
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
)

REM 2. Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no encontrado. Instala pip.
    pause
    exit /b 1
) else (
    echo ✅ pip encontrado
)

REM 3. Crear entorno virtual
echo.
echo ℹ️  Creando entorno virtual...
if not exist ".venv" (
    python -m venv .venv
    echo ✅ Entorno virtual creado
) else (
    echo ⚠️  Entorno virtual ya existe
)

REM 4. Activar entorno virtual
echo ℹ️  Activando entorno virtual...
call .venv\Scripts\activate.bat
echo ✅ Entorno virtual activado

REM 5. Actualizar pip
echo ℹ️  Actualizando pip...
python -m pip install --upgrade pip
echo ✅ pip actualizado

REM 6. Verificar dependencias del sistema
echo.
echo ℹ️  Verificando dependencias del sistema...
echo ⚠️  En Windows necesitas instalar manualmente:
echo    - Visual Studio Build Tools
echo    - CMake
echo    - Tesseract OCR
echo.
set /p deps="¿Ya tienes las dependencias del sistema instaladas? (y/n): "
if /i not "%deps%"=="y" (
    echo ⚠️  Por favor instala las dependencias antes de continuar
    echo    Consulta README.md para instrucciones detalladas
    pause
    exit /b 1
)

REM 7. Instalar dependencias Python
echo.
echo ℹ️  Instalando dependencias Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
) else (
    echo ✅ Dependencias Python instaladas
)

REM 8. Configurar variables de entorno
echo.
echo ℹ️  Configurando variables de entorno...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ Archivo .env creado desde .env.example
        echo ⚠️  ¡IMPORTANTE! Edita .env y configura tus variables
        echo ⚠️  Especialmente DROPBOX_ACCESS_TOKEN es obligatorio
    ) else (
        echo ❌ No se encontró .env.example
        pause
        exit /b 1
    )
) else (
    echo ⚠️  Archivo .env ya existe
)

REM 9. Ejecutar migraciones
echo.
echo ℹ️  Ejecutando migraciones de base de datos...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Error en migraciones
    pause
    exit /b 1
) else (
    echo ✅ Migraciones completadas
)

REM 10. Crear superusuario (opcional)
echo.
set /p createuser="¿Quieres crear un superusuario ahora? (y/n): "
if /i "%createuser%"=="y" (
    python manage.py createsuperuser
    echo ✅ Superusuario creado
)

REM 11. Verificar instalación
echo.
echo ℹ️  Verificando instalación...
python manage.py check
if errorlevel 1 (
    echo ❌ Error en verificación
    pause
    exit /b 1
) else (
    echo ✅ Verificación completada
)

REM 12. Instrucciones finales
echo.
echo ==================================================
echo ✅ ¡Instalación completada exitosamente! 🎉
echo ==================================================
echo.
echo ℹ️  Próximos pasos:
echo 1. Edita el archivo .env con tus configuraciones
echo 2. Configura DROPBOX_ACCESS_TOKEN (obligatorio)
echo 3. Ejecuta: python manage.py runserver
echo 4. Visita: http://localhost:8000
echo.
echo ℹ️  Para activar el entorno virtual en el futuro:
echo .venv\Scripts\activate
echo.
echo ℹ️  Documentación completa en README.md
echo.
echo ✅ ¡Disfruta tu sistema de IA! 🤖
echo.
pause