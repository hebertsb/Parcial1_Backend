@echo off
echo ============================================
echo 🚀 INSTALADOR AUTOMATICO - Sistema de Reconocimiento Facial
echo ============================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo 📋 Instrucciones:
    echo 1. Descarga Python desde: https://python.org/downloads/
    echo 2. Durante la instalación, marca "Add Python to PATH"
    echo 3. Reinicia la terminal y ejecuta este script nuevamente
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado
python --version

:: Verificar si pip está disponible
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: pip no está disponible
    pause
    exit /b 1
)

echo ✅ pip disponible
echo.

:: Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual creado
echo.

:: Activar entorno virtual
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual activado
echo.

:: Actualizar pip
echo 📈 Actualizando pip...
python -m pip install --upgrade pip

:: Instalar dependencias
echo 📚 Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudieron instalar las dependencias
    echo.
    echo 🔧 Intentando instalación alternativa...
    pip install Django==5.2.6
    pip install djangorestframework
    pip install djangorestframework-simplejwt
    pip install drf-spectacular
    pip install Pillow
    pip install python-dotenv
    
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Instalación fallida. Revisar requirements.txt
        pause
        exit /b 1
    )
)

echo ✅ Dependencias instaladas
echo.

:: Crear archivo .env si no existe
if not exist .env (
    echo 📝 Creando archivo de configuración...
    copy .env.example .env
    echo ✅ Archivo .env creado desde .env.example
) else (
    echo ℹ️  Archivo .env ya existe
)
echo.

:: Ejecutar migraciones
echo 🗄️  Ejecutando migraciones...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ ERROR: Fallo en migraciones
    pause
    exit /b 1
)

echo ✅ Migraciones completadas
echo.

:: Crear usuarios del sistema
echo 👥 Creando usuarios del sistema...
python manage.py crear_usuarios_facial
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: No se pudieron crear usuarios automáticamente
    echo    Puedes crearlos manualmente después con: python manage.py crear_usuarios_facial
) else (
    echo ✅ Usuarios creados exitosamente
)
echo.

:: Crear datos de prueba (opcional)
echo 🧪 ¿Quieres crear datos de prueba? (s/n)
set /p create_test_data="Respuesta: "
if /i "%create_test_data%"=="s" (
    echo 📊 Creando datos de prueba...
    python manage.py create_test_data
    if %errorlevel% neq 0 (
        echo ⚠️  WARNING: No se pudieron crear datos de prueba
    ) else (
        echo ✅ Datos de prueba creados
    )
)
echo.

:: Verificar instalación
echo 🧪 Verificando instalación...
python manage.py check
if %errorlevel% neq 0 (
    echo ❌ ERROR: La verificación del sistema falló
    pause
    exit /b 1
)

echo ✅ Verificación completada
echo.

echo ============================================
echo 🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!
echo ============================================
echo.
echo 📋 CREDENCIALES POR DEFECTO:
echo ┌─────────────────┬─────────────────────────────┬─────────────────┐
echo │ ROL             │ EMAIL                       │ PASSWORD        │
echo ├─────────────────┼─────────────────────────────┼─────────────────┤
echo │ 👑 Administrador │ admin@facial.com           │ admin123        │
echo │ 🛡️  Seguridad    │ seguridad@facial.com       │ seguridad123    │
echo │ 🏠 Propietario   │ maria.gonzalez@facial.com  │ propietario123  │
echo │ 🔑 Inquilino     │ carlos.rodriguez@facial.com│ inquilino123    │
echo └─────────────────┴─────────────────────────────┴─────────────────┘
echo.
echo 🌐 URLs IMPORTANTES:
echo   • Servidor:        http://127.0.0.1:8000
echo   • Admin Panel:     http://127.0.0.1:8000/admin/
echo   • API Docs:        http://127.0.0.1:8000/api/docs/
echo   • Login API:       http://127.0.0.1:8000/api/auth/login/
echo.
echo 🚀 PARA INICIAR EL SERVIDOR:
echo   1. python manage.py runserver
echo   2. Abrir navegador en: http://127.0.0.1:8000
echo.
echo 📚 DOCUMENTACIÓN:
echo   • Ver INSTALLATION_GUIDE.md para más detalles
echo   • Ver POSTMAN_AUTHZ_GUIDE.md para probar la API
echo.
echo ⚠️  NOTA: El reconocimiento facial está en modo SIMULADO
echo    Para modo real, ver INSTALLATION_GUIDE.md sección "Instalación Avanzada"
echo.
echo ¿Quieres iniciar el servidor ahora? (s/n)
set /p start_server="Respuesta: "
if /i "%start_server%"=="s" (
    echo.
    echo 🚀 Iniciando servidor...
    python manage.py runserver
) else (
    echo.
    echo 🎯 Sistema listo. Para iniciar: python manage.py runserver
)

pause