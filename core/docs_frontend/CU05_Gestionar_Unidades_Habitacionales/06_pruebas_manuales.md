# 🏠 GUÍA DE PRUEBAS MANUALES - API CU05
# Gestionar Unidades Habitacionales
*Actualizada con modelo authz consolidado*

## 🔧 HERRAMIENTAS RECOMENDADAS:
- **Postman** (Recomendado - usa `GUIA_POSTMAN_CU05_ACTUALIZADA.md`)
- **Insomnia**
- **VS Code REST Client**
- **Navegador web** (solo para GET)

## 📋 CONFIGURACIÓN INICIAL:
- **Base URL**: `http://127.0.0.1:8000`
- **Usuario Admin**: `admin@condominio.com`
- **Contraseña**: `admin123`

## 🔄 MODELO CONSOLIDADO AUTHZ:
- **Personas**: Gestionadas en `authz.Persona` (nombre, apellido, documento_identidad)
- **Usuarios**: Gestionados en `authz.Usuario` (vinculados a Persona)
- **Viviendas**: Gestionadas en `core.Vivienda`
- **Propiedades**: Gestionadas en `core.Propiedad` (vincula Persona-Vivienda)

---

## 🔐 PASO 1: AUTENTICACIÓN

### Obtener Token JWT
```http
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
    "email": "admin@condominio.com",
    "password": "admin123"
}
```

**Respuesta esperada:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "admin@condominio.com",
        "persona": {
            "id": 1,
            "nombre": "Administrador",
            "apellido": "Sistema",
            "documento_identidad": "12345678"
        }
    }
}
```

**⚠️ IMPORTANTE**: Copia el valor de `access` y úsalo en todas las siguientes peticiones como:
```
Authorization: Bearer tu_token_aquí
```

---

## 👤 PASO 2: PRUEBAS DE PERSONAS (MODELO AUTHZ.PERSONA)

### 1. 📋 Listar Personas
```http
GET http://127.0.0.1:8000/api/personas/
Authorization: Bearer tu_token_aquí
```

**Respuesta esperada:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "nombre": "Juan Carlos",
            "apellido": "Pérez López",
            "documento_identidad": "87654321",
            "telefono": "+591 70123456",
            "email": "juan.perez@email.com",
            "propiedades_activas": 1,
            "es_propietario": true,
            "es_inquilino": false
        }
    ]
}
```

### 2. ➕ Crear Nueva Persona
```http
POST http://127.0.0.1:8000/api/personas/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "nombre": "María Elena",
    "apellido": "García Ruiz",
    "documento_identidad": "98765432",
    "telefono": "+591 70987654",
    "email": "maria.garcia@email.com"
}
```

### 3. 🔍 Ver Persona Específica
```http
GET http://127.0.0.1:8000/api/personas/1/
Authorization: Bearer tu_token_aquí
```

### 4. ✏️ Actualizar Persona
```http
PATCH http://127.0.0.1:8000/api/personas/1/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "telefono": "+591 70555666",
    "email": "nuevo.email@email.com"
}
```

---

## 🏠 PASO 3: PRUEBAS DE VIVIENDAS

### 1. 📋 Listar Viviendas
```http
GET http://127.0.0.1:8000/api/viviendas/
Authorization: Bearer tu_token_aquí
```

**Respuesta esperada:**
```json
{
    "count": 10,
    "results": [
        {
            "id": 1,
            "numero_casa": "101",
            "bloque": "A",
            "tipo_vivienda": "departamento",
            "tipo_vivienda_display": "Departamento",
            "metros_cuadrados": "85.50",
            "tarifa_base_expensas": "250.00",
            "estado": "activa",
            "total_propietarios": 1,
            "total_inquilinos": 0
        }
    ]
}
```

### 2. ➕ Crear Nueva Vivienda
```http
POST http://127.0.0.1:8000/api/viviendas/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "numero_casa": "102B",
    "bloque": "B",
    "tipo_vivienda": "casa",
    "metros_cuadrados": "120.00",
    "tarifa_base_expensas": "350.00",
    "tipo_cobranza": "por_casa",
    "estado": "activa"
}
```

### 3. 🔍 Ver Vivienda Específica
```http
GET http://127.0.0.1:8000/api/viviendas/1/
Authorization: Bearer tu_token_aquí
```

### 4. ✏️ Actualizar Vivienda
```http
PATCH http://127.0.0.1:8000/api/viviendas/1/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "tarifa_base_expensas": "300.00"
}
```

### 5. 📊 Ver Estadísticas
```http
GET http://127.0.0.1:8000/api/viviendas/estadisticas/
Authorization: Bearer tu_token_aquí
```

---

## 🏘️ PASO 4: PRUEBAS DE PROPIEDADES (ASIGNACIONES)

### 1. 📋 Listar Propiedades
```http
GET http://127.0.0.1:8000/api/propiedades/
Authorization: Bearer tu_token_aquí
```

**Respuesta esperada:**
```json
{
    "count": 8,
    "results": [
        {
            "id": 1,
            "vivienda": {
                "id": 1,
                "numero_casa": "101",
                "bloque": "A"
            },
            "persona": {
                "id": 2,
                "nombre": "Carlos Eduardo",
                "apellido": "Mendoza Silva",
                "documento_identidad": "11223344"
            },
            "tipo_tenencia": "propietario",
            "porcentaje_propiedad": "100.00",
            "fecha_inicio_tenencia": "2024-01-01",
            "estado": "activa"
        }
    ]
}
```

### 2. ➕ Asignar Propietario
```http
POST http://127.0.0.1:8000/api/propiedades/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "vivienda": 2,
    "persona": 3,
    "tipo_tenencia": "propietario",
    "porcentaje_propiedad": "100.00",
    "fecha_inicio_tenencia": "2025-01-01"
}
```

### 3. ➕ Asignar Inquilino
```http
POST http://127.0.0.1:8000/api/propiedades/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "vivienda": 2,
    "persona": 4,
    "tipo_tenencia": "inquilino",
    "fecha_inicio_tenencia": "2025-01-01",
    "fecha_fin_tenencia": "2025-12-31"
}
```

### 4. 👥 Ver Propiedades de una Vivienda
```http
GET http://127.0.0.1:8000/api/viviendas/1/propiedades/
Authorization: Bearer tu_token_aquí
```

---

## 🔍 PASO 5: PRUEBAS DE FILTROS Y BÚSQUEDAS

### 1. 🔎 Buscar Personas por Nombre
```http
GET http://127.0.0.1:8000/api/personas/?search=García
Authorization: Bearer tu_token_aquí
```

### 2. 🏠 Solo Propietarios
```http
GET http://127.0.0.1:8000/api/personas/propietarios/
Authorization: Bearer tu_token_aquí
```

### 3. 🏘️ Solo Inquilinos
```http
GET http://127.0.0.1:8000/api/personas/inquilinos/
Authorization: Bearer tu_token_aquí
```

### 4. 🔎 Buscar Viviendas por Número
```http
GET http://127.0.0.1:8000/api/viviendas/?search=101
Authorization: Bearer tu_token_aquí
```

### 5. 📊 Filtrar Viviendas por Estado
```http
GET http://127.0.0.1:8000/api/viviendas/?estado=activa
Authorization: Bearer tu_token_aquí
```

### 6. 🏘️ Filtrar Propiedades por Vivienda
```http
GET http://127.0.0.1:8000/api/propiedades/?vivienda=1
Authorization: Bearer tu_token_aquí
```

---

## 🧪 PASO 6: PRUEBAS DE VALIDACIÓN

### 1. ❌ Intentar Crear Persona con Documento Duplicado
```http
POST http://127.0.0.1:8000/api/personas/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "nombre": "Test",
    "apellido": "Usuario",
    "documento_identidad": "87654321",
    "email": "test@email.com"
}
```

**Respuesta esperada (400):**
```json
{
    "documento_identidad": ["Ya existe una persona con este documento de identidad."]
}
```

### 2. ❌ Intentar Crear Vivienda con Número Duplicado
```http
POST http://127.0.0.1:8000/api/viviendas/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "numero_casa": "101",
    "bloque": "A",
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "85.00",
    "tarifa_base_expensas": "250.00"
}
```

**Respuesta esperada (400):**
```json
{
    "numero_casa": ["Ya existe una vivienda con este número en este bloque."]
}
```

### 3. ❌ Intentar Asignar Porcentaje > 100%
```http
POST http://127.0.0.1:8000/api/propiedades/
Authorization: Bearer tu_token_aquí
Content-Type: application/json

{
    "vivienda": 1,
    "persona": 2,
    "tipo_tenencia": "propietario",
    "porcentaje_propiedad": "150.00",
    "fecha_inicio_tenencia": "2025-01-01"
}
```

**Respuesta esperada (400):**
```json
{
    "non_field_errors": ["El porcentaje total de propiedad no puede exceder 100%"]
}
```

---

## 📊 PASO 7: PRUEBAS DE CASOS COMPLETOS

### Caso 1: Nueva Vivienda con Propietario
1. **Crear persona** (paso 2.2)
2. **Crear vivienda** (paso 3.2)
3. **Asignar como propietario** (paso 4.2)
4. **Verificar en estadísticas** (paso 3.5)

### Caso 2: Vivienda con Propietario e Inquilino
1. **Usar vivienda existente**
2. **Crear segunda persona**
3. **Asignar como inquilino** (paso 4.3)
4. **Ver propiedades de la vivienda** (paso 4.4)

### Caso 3: Búsquedas y Filtros
1. **Buscar personas por apellido**
2. **Filtrar solo propietarios**
3. **Filtrar propiedades por vivienda**
4. **Ver estadísticas generales**

---

## ✅ RESULTADOS ESPERADOS:

- ✅ **Autenticación JWT funcionando**
- ✅ **CRUD completo de Personas (authz.Persona)**
- ✅ **CRUD completo de Viviendas (core.Vivienda)** 
- ✅ **CRUD completo de Propiedades (core.Propiedad)**
- ✅ **Validaciones de campos únicos**
- ✅ **Filtros y búsquedas funcionando**
- ✅ **Relaciones entre modelos correctas**
- ✅ **Estadísticas actualizadas dinámicamente**

---

## 🚀 PARA USAR EN POSTMAN:

Importa estos archivos en Postman:
   - `CU05_Viviendas_Postman_Collection.json`
   - `CU05_Environment.postman_environment.json`

O usa la guía detallada: `docs_frontend/GUIA_POSTMAN_CU05_ACTUALIZADA.md`

---

## 🔧 TROUBLESHOOTING:

### Error 401 - Unauthorized
- Verifica que el token JWT esté incluido
- Verifica que el token no haya expirado
- Usa el formato: `Bearer tu_token_aquí`

### Error 400 - Bad Request
- Verifica la estructura JSON
- Verifica que todos los campos requeridos estén incluidos
- Verifica los tipos de datos (números como string con decimales)

### Error 404 - Not Found
- Verifica que la URL sea correcta
- Verifica que el ID del recurso exista
- Verifica que el servidor esté corriendo

### Error 500 - Internal Server Error
- Revisa los logs del servidor Django
- Verifica que la base de datos esté accesible
- Verifica que las migraciones estén aplicadas

---

## 🎯 ¡PRUEBAS LISTAS CON MODELO CONSOLIDADO!

Esta guía está actualizada para el modelo authz consolidado con:
- ✅ Campos correctos (nombre/apellido, documento_identidad)
- ✅ Relaciones authz.Persona ↔ core.Propiedad ↔ core.Vivienda
- ✅ Validaciones integradas
- ✅ Casos de prueba completos