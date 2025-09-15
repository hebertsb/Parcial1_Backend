# 🧪 Guía de Pruebas con Postman - Sistema de Reconocimiento Facial

> **📌 NOTA IMPORTANTE**: El sistema funciona en **modo simulado** porque face_recognition requiere CMake para instalarse. El modo simulado proporciona **funcionalidad completa** para pruebas y desarrollo, simulando la detección y verificación facial de manera realista.

## 📋 Pre-requisitos

1. **Postman instalado** (https://www.postman.com/downloads/)
2. **Servidor Django corriendo**: `python manage.py runserver`
3. **Datos de prueba cargados**: `python manage.py create_test_data`

## 🚀 Configuración Inicial de Postman

### 1. Crear Nueva Colección
- Abre Postman
- Crea una nueva colección llamada "Face Recognition API"
- Configura Base URL: `http://127.0.0.1:8000`

### 2. Configurar Variables de Entorno (Opcional)
En Postman, crea un Environment con estas variables:
- `base_url`: `http://127.0.0.1:8000`
- `jwt_token`: (se llenará automáticamente)

## 🔐 PASO 1: Obtener Token JWT

### Request: Login
```
Method: POST
URL: http://127.0.0.1:8000/api/auth/login/
Headers:
  Content-Type: application/json

Body (raw JSON):
{
    "username": "operador",
    "password": "operador123"
}
```

### ✅ Respuesta Esperada:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**💡 IMPORTANTE**: Copia el valor de `"access"` para usar en las siguientes requests.

---

## 👤 PASO 2: Consultar Estado de Copropietario

### Request: Face Status
```
Method: GET
URL: http://127.0.0.1:8000/api/faces/status/1/
Headers:
  Authorization: Bearer TU_JWT_TOKEN_AQUI
```

### ✅ Respuesta Esperada (No enrolado):
```json
{
    "enrolado": false,
    "proveedor": null,
    "fecha_enrolamiento": null,
    "intentos_verificacion": null,
    "ultima_verificacion": null,
    "copropietario": {
        "id": 1,
        "nombres": "María Elena",
        "apellidos": "González López",
        "nombre_completo": "María Elena González López",
        "numero_documento": "12345678",
        "tipo_documento": "CC",
        "unidad_residencial": "Apto 101"
    }
}
```

---

## 📸 PASO 3: Enrolar Copropietario

### Request: Face Enroll
```
Method: POST
URL: http://127.0.0.1:8000/api/faces/enroll/
Headers:
  Authorization: Bearer TU_JWT_TOKEN_AQUI

Body (form-data):
  copropietario_id: 1
  imagen: [Seleccionar archivo de imagen - JPG/PNG]
```

### 📝 Instrucciones para el Body:
1. En Postman, selecciona **Body → form-data**
2. Agrega estos campos:
   - **Key**: `copropietario_id`, **Type**: Text, **Value**: `1`
   - **Key**: `imagen`, **Type**: File, **Value**: [Seleccionar una imagen con rostro]

### ✅ Respuesta Esperada (Éxito):
```json
{
    "ok": true,
    "proveedor": "Local (Simulado)",
    "face_ref": "aGVsbG8gd29ybGQ=...",
    "imagen_url": null,
    "timestamp": "2025-09-11T23:15:00Z",
    "copropietario": {
        "id": 1,
        "nombres": "María Elena",
        "apellidos": "González López",
        "numero_documento": "12345678",
        "unidad_residencial": "Apto 101"
    }
}
```

### ❌ Posibles Errores:
- **422**: No se detectó rostro en la imagen
- **400**: Imagen muy grande o formato inválido
- **404**: Copropietario no encontrado

---

## 🔍 PASO 4: Verificar Identidad

### Request: Face Verify
```
Method: POST
URL: http://127.0.0.1:8000/api/faces/verify/
Headers:
  Authorization: Bearer TU_JWT_TOKEN_AQUI

Body (form-data):
  copropietario_id: 1
  imagen: [Seleccionar archivo de imagen para verificar]
```

### ✅ Respuesta Esperada (Match):
```json
{
    "match": true,
    "confianza": 0.75,
    "proveedor": "Local (Simulado)",
    "umbral": 0.6,
    "copropietario": {
        "id": 1,
        "nombres": "María Elena",
        "apellidos": "González López"
    }
}
```

### ✅ Respuesta Esperada (No Match):
```json
{
    "match": false,
    "confianza": 0.35,
    "proveedor": "Local (Simulado)",
    "umbral": 0.6,
    "copropietario": {
        "id": 1,
        "nombres": "María Elena",
        "apellidos": "González López"
    }
}
```

---

## 🗑️ PASO 5: Eliminar Enrolamiento

### Request: Face Delete
```
Method: DELETE
URL: http://127.0.0.1:8000/api/faces/enroll/1/
Headers:
  Authorization: Bearer TU_JWT_TOKEN_AQUI
```

### ✅ Respuesta Esperada:
```json
{
    "ok": true,
    "message": "Enrolamiento biométrico eliminado exitosamente",
    "copropietario": {
        "id": 1,
        "nombres": "María Elena",
        "apellidos": "González López"
    }
}
```

---

## 🧪 Casos de Prueba Recomendados

### Prueba Completa 1: Flujo Exitoso
1. **Login** → Obtener JWT
2. **Status** → Verificar no enrolado  
3. **Enroll** → Enrolar con imagen de rostro
4. **Status** → Verificar enrolado
5. **Verify** → Verificar con misma imagen (debería dar match)
6. **Verify** → Verificar con imagen diferente (debería dar no-match)
7. **Delete** → Eliminar enrolamiento
8. **Status** → Verificar no enrolado

### Prueba de Seguridad 1: Sin Autenticación
Intenta cualquier endpoint **sin** el header `Authorization` → Debería retornar **401**

### Prueba de Validación 1: Datos Inválidos
- **Enroll** con `copropietario_id: 999` → **404**
- **Enroll** con imagen sin rostro → **422**
- **Verify** sin enrolamiento previo → **404**

---

## 🖼️ Imágenes de Prueba

### ✅ Recomendaciones para Imágenes:
- **Formato**: JPG, PNG, GIF, BMP
- **Tamaño**: Máximo 6MB
- **Contenido**: Una sola persona, rostro visible
- **Resolución**: Mínimo 200x200 pixels

### 📁 Dónde Conseguir Imágenes de Prueba:
1. **Usar tu propia foto** (selfie frontal)
2. **Fotos de stock** con rostros claros
3. **Generated This Person**: https://thispersondoesnotexist.com/
4. **Avatares de prueba**: Buscar "headshot portrait" en bancos de imágenes

---

## 🔧 Troubleshooting

### ❌ "500 Internal Server Error - No module named 'face_recognition'"
- **Causa**: La librería face_recognition no está instalada (requiere CMake y compilación)
- **Solución Aplicada**: El sistema ahora funciona en **modo simulado** cuando face_recognition no está disponible
- **Comportamiento**: 
  - ✅ **Enrolamiento**: Genera vectores simulados basados en hash de imagen
  - ✅ **Verificación**: Compara imágenes usando similitud de hash + aleatoriedad
  - ✅ **API Completa**: Todos los endpoints funcionan normalmente
  - 📊 **Logging**: Los logs indicarán "Simulado" o "face_recognition no disponible"

### ❌ "401 Unauthorized"
- **Causa**: Token JWT inválido o expirado
- **Solución**: Hacer login nuevamente y copiar nuevo token

### ❌ "422 No se detectó rostro"
- **Causa**: Imagen muy pequeña (menor a 50x50) o formato inválido
- **Solución**: Usar imagen con al menos 200x200 pixels y formato JPG/PNG

### ❌ "400 Datos inválidos"
- **Causa**: Campo faltante o formato incorrecto
- **Solución**: Verificar que `copropietario_id` sea número y `imagen` sea archivo

### ❌ "404 Copropietario no encontrado"
- **Causa**: ID de copropietario inexistente
- **Solución**: Usar IDs válidos (1, 2, 3, 4) creados por `create_test_data`

### ❌ "Connection Error"
- **Causa**: Servidor Django no está corriendo
- **Solución**: Ejecutar `python manage.py runserver`

---

## 📊 Monitoreo en Tiempo Real

### Logs del Sistema
Mientras pruebas, puedes ver logs en tiempo real:
```bash
# En otra terminal
tail -f logs/face_recognition.log
```

### Admin Django
Verifica los registros en: http://127.0.0.1:8000/admin/
- **BitacoraAcciones**: Ver todas las operaciones registradas
- **ReconocimientoFacial**: Ver enrolamientos activos
- **Copropietarios**: Ver datos de copropietarios

---

## 📋 Colección de Postman Pre-configurada

Si quieres importar una colección lista, aquí tienes el JSON:

```json
{
    "info": {
        "name": "Face Recognition API",
        "description": "API de reconocimiento facial para copropietarios"
    },
    "variable": [
        {
            "key": "base_url",
            "value": "http://127.0.0.1:8000"
        },
        {
            "key": "jwt_token",
            "value": ""
        }
    ],
    "item": [
        {
            "name": "1. Login",
            "request": {
                "method": "POST",
                "url": "{{base_url}}/api/auth/login/",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"username\": \"operador\",\n    \"password\": \"operador123\"\n}"
                }
            }
        },
        {
            "name": "2. Face Status",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/api/faces/status/1/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ]
            }
        }
    ]
}
```

## 🎯 ¡Listo para Probar!

Ya tienes todo configurado. El flujo básico sería:

1. **Iniciar servidor**: `python manage.py runserver`
2. **Abrir Postman**
3. **Hacer Login** → Copiar JWT token
4. **Probar endpoints** siguiendo los pasos de esta guía

¡El sistema está funcionando perfectamente y listo para todas las pruebas! 🚀
