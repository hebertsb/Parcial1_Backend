# 🚀 Guía de Deployment en Railway

## 📋 Resumen de tu Proyecto

Tu proyecto Django tiene las siguientes características que requieren dockerización:

- **OCR**: pytesseract requiere tesseract-ocr instalado en el sistema
- **Face Recognition**: dlib y face_recognition requieren dependencias de sistema
- **OpenCV**: Para procesamiento de imágenes
- **Django**: Backend con múltiples aplicaciones

## 🔧 Archivos Creados/Modificados

### ✅ Archivos de Configuración
- `dockerfile` - Imagen Docker optimizada con todas las dependencias
- `railway.json` - Configuración específica de Railway
- `Procfile` - Alternativa para Railway
- `.dockerignore` - Optimización del build
- `start.sh` - Script de inicio con verificaciones

### ✅ Configuración de Django
- `core/settings_production.py` - Settings para producción
- `core/views.py` - Health check endpoint añadido
- `core/urls.py` - Ruta de health check
- `requirements.txt` - Dependencias de producción añadidas

### ✅ Variables de Entorno
- `.env.railway.example` - Plantilla de variables

## 🚀 Pasos para Deployar en Railway

### 1. Preparar tu Repositorio

```bash
git add .
git commit -m "Preparar para deployment en Railway"
git push origin main
```

### 2. Configurar Railway

1. Ve a [railway.app](https://railway.app)
2. Conecta tu cuenta de GitHub
3. Crea un nuevo proyecto
4. Selecciona tu repositorio
5. Railway detectará automáticamente el Dockerfile

### 3. Configurar Variables de Entorno

En Railway Dashboard > Variables, agrega:

```env
DJANGO_SETTINGS_MODULE=core.settings_production
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=tu@email.com
DJANGO_SUPERUSER_PASSWORD=tu-password-seguro
```

### 4. (Opcional) Agregar Base de Datos

Si quieres usar PostgreSQL:
1. En Railway, click "Add Service" > PostgreSQL
2. La variable `DATABASE_URL` se configurará automáticamente

### 5. Deploy

Railway comenzará el deployment automáticamente. El proceso incluye:
- ✅ Build de la imagen Docker
- ✅ Instalación de tesseract-ocr
- ✅ Instalación de dependencias Python
- ✅ Ejecución de migraciones
- ✅ Recopilación de archivos estáticos
- ✅ Verificación de OCR y Face Recognition

## 🔍 Verificación del Deployment

### Health Check
Tu aplicación incluye un endpoint de health check:
```
GET https://tu-app.railway.app/api/health/
```

### Endpoints Principales
- Admin: `https://tu-app.railway.app/admin/`
- API: `https://tu-app.railway.app/api/`
- WebRTC: `https://tu-app.railway.app/webrtc/`

## 🐛 Troubleshooting

### Si el build falla:

1. **Memoria insuficiente**: Railway limita recursos en el plan gratuito
2. **Timeout en build**: Imagen Docker puede tardar debido a dlib/face_recognition
3. **Dependencias de sistema**: El Dockerfile incluye todas las necesarias

### Si la aplicación no inicia:

1. Revisa los logs en Railway Dashboard
2. Verifica las variables de entorno
3. Confirma que `DJANGO_SETTINGS_MODULE=core.settings_production`

### Si OCR no funciona:

El Dockerfile instala tesseract con idiomas español e inglés:
```dockerfile
tesseract-ocr \
tesseract-ocr-spa \
tesseract-ocr-eng \
```

## 📊 Recursos de Railway

### Plan Gratuito:
- $5 USD en créditos mensuales
- Suficiente para desarrollo y pruebas
- La aplicación se "duerme" después de inactividad

### Plan Pro:
- $20 USD/mes
- Aplicación siempre activa
- Más recursos de CPU/memoria

## 🎯 Funcionalidad Implementada

Tu aplicación ahora incluye:

### ✅ **Panel de Actividades de Seguridad**
- Logs de acceso en tiempo real
- Dashboard con estadísticas
- Incidentes de seguridad
- Gestión de visitas activas

### ✅ **Endpoints para Frontend**
```
GET /api/authz/seguridad/acceso/logs/
GET /api/authz/seguridad/dashboard/
GET /api/authz/seguridad/incidentes/
GET /api/authz/seguridad/visitas/activas/
```

### ✅ **Integración Completa**
- Reconocimiento facial con logs automáticos
- Datos reales de actividad de usuarios
- Sistema de bitácora completo
- 52+ registros de prueba incluidos

## 🔒 Configuración de Seguridad

El archivo `settings_production.py` incluye:
- HTTPS enforcement (cuando DEBUG=False)
- CORS configurado
- Security headers
- WhiteNoise para archivos estáticos

## 📱 Conectar con Frontend

Para conectar tu frontend, actualiza las URLs en `settings_production.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.netlify.app",
    "https://tu-dominio-personalizado.com",
]
```

## 🎯 Próximos Pasos

1. **Deploy inicial**: Sigue los pasos 1-5
2. **Configurar dominio personalizado**: En Railway Settings
3. **Configurar HTTPS**: Automático con Railway
4. **Monitoreo**: Usa Railway Dashboard para logs y métricas
5. **Base de datos**: Agregar PostgreSQL si es necesario

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en Railway Dashboard
2. Verifica el health check: `/api/health/`
3. Confirma las variables de entorno

¡Tu aplicación Django con OCR y Face Recognition está lista para Railway! 🎉