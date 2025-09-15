# Sistema de Reconocimiento Facial - FASE 1 BACKEND

Sistema de reconocimiento facial para control de acceso de copropietarios utilizando Django + Django REST Framework.

## 🏗️ Arquitectura

### Tecnologías Implementadas
- **Backend**: Django 5.2.6 + Django REST Framework
- **Autenticación**: JWT (djangorestframework-simplejwt)
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Reconocimiento Facial**: 
  - **Local**: face_recognition library (dlib + OpenCV)
  - **Cloud**: Azure Cognitive Services Face API
- **Documentación API**: OpenAPI 3.0 + Swagger UI
- **Rate Limiting**: DRF Throttling
- **Logging**: Sistema de bitácora completo

## 📊 Modelos de Datos

### 1. Roles
- Gestión de roles del sistema (Administrador, Operador, etc.)

### 2. Usuarios
- Extensión del modelo User de Django
- Vinculación con roles y datos adicionales

### 3. Copropietarios
- Información personal y de residencia
- Documentos de identidad
- Datos de contacto

### 4. ReconocimientoFacial
- Almacenamiento de vectores faciales
- Soporte para múltiples proveedores (Local/Azure)
- Metadatos de enrolamiento y uso

### 5. BitacoraAcciones
- Registro completo de todas las acciones del sistema
- Trazabilidad de operaciones biométricas
- Auditoría de seguridad

## 🔌 API Endpoints

### Autenticación JWT
```
POST /api/auth/login/      # Obtener token JWT
POST /api/auth/refresh/    # Renovar token
POST /api/auth/verify/     # Verificar token
```

### Reconocimiento Facial
```
POST /api/faces/enroll/                      # Enrolar copropietario
POST /api/faces/verify/                      # Verificar identidad
DELETE /api/faces/enroll/<copropietario_id>/ # Eliminar enrolamiento
GET /api/faces/status/<copropietario_id>/    # Consultar estado
```

### Documentación
```
GET /api/docs/             # Swagger UI
GET /api/redoc/            # ReDoc
GET /api/schema/           # Esquema OpenAPI
```

## 🔧 Configuración

### Variables de Entorno (.env)
```bash
# Proveedor de reconocimiento facial
FACE_RECOGNITION_PROVIDER=Local  # Local | Microsoft

# Configuración local
FACE_LOCAL_THRESHOLD=0.6

# Configuración Azure (opcional)
AZURE_FACE_API_KEY=your-api-key
AZURE_FACE_ENDPOINT=https://your-face-service.cognitiveservices.azure.com/
```

### Instalación

1. **Clonar y configurar entorno**:
```bash
git clone <repo>
cd primer_parcial
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Ejecutar migraciones**:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Crear datos de prueba**:
```bash
python manage.py create_test_data
```

5. **Iniciar servidor**:
```bash
python manage.py runserver
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test seguridad

# Tests específicos
python manage.py test seguridad.tests.ModelsTestCase
python manage.py test seguridad.tests.FaceRecognitionAPITestCase
python manage.py test seguridad.tests.BitacoraTestCase
```

## 📝 Uso de la API

### 1. Obtener Token JWT
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "operador", "password": "operador123"}'
```

### 2. Enrolar Copropietario
```bash
curl -X POST http://127.0.0.1:8000/api/faces/enroll/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "copropietario_id=1" \
  -F "imagen=@path/to/face_image.jpg"
```

### 3. Verificar Identidad
```bash
curl -X POST http://127.0.0.1:8000/api/faces/verify/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "copropietario_id=1" \
  -F "imagen=@path/to/verification_image.jpg"
```

### 4. Consultar Estado
```bash
curl -X GET http://127.0.0.1:8000/api/faces/status/1/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔒 Seguridad Implementada

### Rate Limiting
- **Enrolamiento**: 5 requests/minuto por usuario
- **Verificación**: 10 requests/minuto por usuario
- **General**: 1000 requests/hora por usuario autenticado

### Autenticación
- JWT con expiración configurable
- Tokens de refresh automático
- Middleware de autenticación obligatorio

### Validaciones
- Validación de formatos de imagen (JPEG, PNG, GIF, BMP)
- Límites de tamaño (máximo 6MB)
- Validación de existencia de copropietarios
- Verificación de enrolamientos activos

## 🎯 Servicios de Reconocimiento Facial

### LocalFaceProvider
- Basado en face_recognition library
- Procesamiento local sin dependencias externas
- Vectores de 128 dimensiones
- Umbral configurable de similitud

### AzureFaceProvider
- Integración con Azure Cognitive Services
- Face API REST
- Detección y verificación en la nube
- Manejo de errores y timeouts

### Factory Pattern
- Selección automática de proveedor según configuración
- Interfaz común para ambos proveedores
- Fácil extensión para nuevos proveedores

## 📊 Respuestas de la API

### Enrolamiento Exitoso (201/200)
```json
{
  "ok": true,
  "proveedor": "Local",
  "face_ref": "encoded_vector...",
  "imagen_url": null,
  "timestamp": "2025-09-11T22:30:00Z",
  "copropietario": {
    "id": 1,
    "nombres": "María Elena",
    "apellidos": "González López",
    "numero_documento": "12345678",
    "unidad_residencial": "Apto 101"
  }
}
```

### Verificación Exitosa (200)
```json
{
  "match": true,
  "confianza": 0.85,
  "proveedor": "Local",
  "umbral": 0.6,
  "copropietario": {
    "id": 1,
    "nombres": "María Elena",
    "apellidos": "González López"
  }
}
```

### Estado de Enrolamiento (200)
```json
{
  "enrolado": true,
  "proveedor": "Local",
  "fecha_enrolamiento": "2025-09-11T20:00:00Z",
  "intentos_verificacion": 5,
  "ultima_verificacion": "2025-09-11T22:25:00Z",
  "copropietario": {
    "id": 1,
    "nombres": "María Elena",
    "apellidos": "González López"
  }
}
```

## 🚨 Manejo de Errores

### Códigos de Estado
- **400**: Datos inválidos
- **401**: No autenticado
- **403**: Sin permisos
- **404**: Recurso no encontrado
- **422**: Error de procesamiento (ej: no se detectó rostro)
- **429**: Rate limit excedido
- **500**: Error interno del servidor

### Formato de Error
```json
{
  "error": "Descripción del error",
  "details": "Detalles específicos del error"
}
```

## 📈 Bitácora y Auditoría

Todas las operaciones se registran automáticamente en `BitacoraAcciones`:

- **ENROLL_FACE**: Enrolamientos biométricos
- **VERIFY_FACE**: Verificaciones de identidad
- **DELETE_FACE**: Eliminaciones de enrolamiento
- **SYSTEM_ERROR**: Errores del sistema

Cada registro incluye:
- Usuario que ejecuta la acción
- Copropietario afectado
- Timestamp preciso
- IP y User-Agent
- Proveedor utilizado
- Resultado y confianza
- Descripción detallada

## 🔧 Administración

### Django Admin
Accede a `http://127.0.0.1:8000/admin/` con:
- **Usuario**: admin
- **Contraseña**: admin

### Management Commands
```bash
# Crear datos de prueba
python manage.py create_test_data

# Crear superusuario
python manage.py createsuperuser
```

## 📁 Estructura del Proyecto

```
primer_parcial/
├── core/                     # Configuración principal
│   ├── settings.py          # Configuración Django + DRF + JWT
│   ├── urls.py              # URLs principales
│   └── wsgi.py
├── seguridad/               # App principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas API
│   ├── serializers.py       # Serializers DRF
│   ├── urls.py              # URLs de la API
│   ├── admin.py             # Configuración admin
│   ├── tests.py             # Tests unitarios
│   ├── services/            # Servicios de reconocimiento facial
│   │   ├── face_provider.py # Interfaz y factory
│   │   ├── azure_face.py    # Proveedor Azure
│   │   └── local_face.py    # Proveedor local
│   └── management/commands/
│       └── create_test_data.py
├── media/                   # Archivos subidos
├── logs/                    # Logs del sistema
├── .env                     # Variables de entorno
├── .env.example            # Ejemplo de configuración
└── requirements.txt        # Dependencias
```

## 🎯 Datos de Prueba

El sistema incluye datos de prueba listos para usar:

### Usuarios
- **admin** / admin (Superusuario)
- **operador** / operador123 (Operador de seguridad)

### Copropietarios Disponibles
1. **ID 1**: María Elena González López (Apto 101)
2. **ID 2**: Carlos Alberto Rodríguez Pérez (Apto 205)
3. **ID 3**: Ana Sofía Martínez Silva (Casa 15)
4. **ID 4**: José Miguel Hernández Torres (Apto 312)

## 🔮 Próximos Pasos (Fases Siguientes)

- **Fase 2**: Frontend React/Vue.js
- **Fase 3**: Aplicación móvil
- **Fase 4**: IoT y control de acceso físico
- **Fase 5**: Analytics y reportes avanzados

## 🤝 Soporte

Para soporte técnico o consultas:
- Revisa la documentación de la API en `/api/docs/`
- Consulta los logs en `logs/face_recognition.log`
- Ejecuta los tests para verificar funcionamiento

---

✅ **Sistema de Reconocimiento Facial - Fase 1 Backend Completado**

🔗 **URLs Útiles**:
- **API Docs**: http://127.0.0.1:8000/api/docs/
- **Admin**: http://127.0.0.1:8000/admin/
- **JWT Login**: http://127.0.0.1:8000/api/auth/login/
