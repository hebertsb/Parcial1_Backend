# 🏠 GUÍA COMPLETA POSTMAN - CU05 GESTIONAR UNIDADES HABITACIONALES
*Versión actualizada con modelos authz consolidados*

## 📋 CONFIGURACIÓN INICIAL

### 🔗 Base URL
```
http://127.0.0.1:8000
```

### 🔐 Autenticación Requerida
Todas las rutas requieren autenticación JWT. Los usuarios se gestionan desde el modelo consolidado `authz.Usuario`.

---

## 🔑 1. AUTENTICACIÓN

### 📝 Obtener Token JWT
**Método:** `POST`  
**URL:** `http://127.0.0.1:8000/api/auth/login/`  
**Headers:** 
```json
{
    "Content-Type": "application/json"
}
```
**Body (raw JSON):**
```json
{
    "email": "admin@condominio.com",
    "password": "admin123"
}
```

**Respuesta esperada:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

### ⚙️ Configurar Token en Postman
1. Copia el valor de `access` 
2. En cada petición, ve a **Authorization**
3. Selecciona **Bearer Token**
4. Pega el token en el campo **Token**

---

## 🏠 2. GESTIÓN DE VIVIENDAS

### 📋 2.1 Listar Todas las Viviendas
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/viviendas/`  
**Authorization:** Bearer Token

**Parámetros opcionales (query params):**
- `search=101` - Buscar por número de casa
- `ordering=numero_casa` - Ordenar por campo
- `estado=activa` - Filtrar por estado
- `tipo_vivienda=casa` - Filtrar por tipo

**Respuesta esperada:**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "numero_casa": "101",
            "bloque": "A",
            "tipo_vivienda": "departamento",
            "tipo_vivienda_display": "Departamento",
            "metros_cuadrados": "85.50",
            "tarifa_base_expensas": "250.00",
            "tipo_cobranza": "por_casa",
            "estado": "activa",
            "estado_display": "Activa",
            "fecha_creacion": "2025-01-15T10:30:00Z",
            "propiedades": [],
            "total_propietarios": 0,
            "total_inquilinos": 0
        }
    ]
}
```

### ➕ 2.2 Crear Nueva Vivienda
**Método:** `POST`  
**URL:** `http://127.0.0.1:8000/api/viviendas/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "numero_casa": "102B",
    "bloque": "B",
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "95.75",
    "tarifa_base_expensas": "280.00",
    "tipo_cobranza": "por_casa",
    "estado": "activa"
}
```

**Respuesta esperada (201):**
```json
{
    "id": 11,
    "numero_casa": "102B",
    "bloque": "B",
    "tipo_vivienda": "departamento",
    "tipo_vivienda_display": "Departamento",
    "metros_cuadrados": "95.75",
    "tarifa_base_expensas": "280.00",
    "tipo_cobranza": "por_casa",
    "tipo_cobranza_display": "Por Casa",
    "estado": "activa",
    "estado_display": "Activa",
    "fecha_creacion": "2025-01-15T15:45:00Z",
    "propiedades": [],
    "total_propietarios": 0,
    "total_inquilinos": 0
}
```

### 🔍 2.3 Obtener Vivienda Específica
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/viviendas/{id}/`  
**Authorization:** Bearer Token

Ejemplo: `http://127.0.0.1:8000/api/viviendas/1/`

### ✏️ 2.4 Actualizar Vivienda Completa
**Método:** `PUT`  
**URL:** `http://127.0.0.1:8000/api/viviendas/{id}/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "numero_casa": "101A",
    "bloque": "A", 
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "90.00",
    "tarifa_base_expensas": "275.00",
    "tipo_cobranza": "por_casa",
    "estado": "activa"
}
```

### 📝 2.5 Actualizar Vivienda Parcial
**Método:** `PATCH`  
**URL:** `http://127.0.0.1:8000/api/viviendas/{id}/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "tarifa_base_expensas": "300.00"
}
```

### ❌ 2.6 Eliminar Vivienda (Marcar Inactiva)
**Método:** `DELETE`  
**URL:** `http://127.0.0.1:8000/api/viviendas/{id}/`  
**Authorization:** Bearer Token

### ✅ 2.7 Reactivar Vivienda
**Método:** `POST`  
**URL:** `http://127.0.0.1:8000/api/viviendas/{id}/activar/`  
**Authorization:** Bearer Token

### 👥 2.8 Ver Propiedades de una Vivienda
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/viviendas/{id}/propiedades/`  
**Authorization:** Bearer Token

**Respuesta esperada:**
```json
[
    {
        "id": 1,
        "persona": {
            "id": 2,
            "nombre": "Juan Carlos",
            "apellido": "Pérez López", 
            "documento_identidad": "87654321",
            "telefono": "+591 70123456",
            "email": "juan.perez@email.com"
        },
        "tipo_tenencia": "propietario",
        "tipo_tenencia_display": "Propietario",
        "porcentaje_propiedad": "100.00",
        "fecha_inicio_tenencia": "2024-01-01",
        "fecha_fin_tenencia": null,
        "estado": "activa"
    }
]
```

### 📊 2.9 Estadísticas del Condominio
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/viviendas/estadisticas/`  
**Authorization:** Bearer Token

**Respuesta esperada:**
```json
{
    "total_viviendas": 50,
    "viviendas_activas": 48,
    "viviendas_inactivas": 2,
    "total_propietarios": 45,
    "total_inquilinos": 15,
    "tipos_vivienda": {
        "departamento": 35,
        "casa": 15
    },
    "promedio_tarifa_expensas": "275.50"
}
```

---

## 👥 3. GESTIÓN DE PROPIEDADES (ASIGNACIONES)

### 📋 3.1 Listar Propiedades
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/propiedades/`  
**Authorization:** Bearer Token

**Parámetros opcionales:**
- `vivienda=1` - Filtrar por vivienda
- `persona=2` - Filtrar por persona (ID de authz.Persona)
- `tipo_tenencia=propietario` - Filtrar por tipo
- `estado=activa` - Filtrar por estado

**Respuesta esperada:**
```json
{
    "count": 25,
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
                "nombre": "María Elena",
                "apellido": "García Ruiz",
                "documento_identidad": "12345678",
                "telefono": "+591 70987654",
                "email": "maria.garcia@email.com"
            },
            "tipo_tenencia": "propietario",
            "porcentaje_propiedad": "100.00",
            "fecha_inicio_tenencia": "2024-01-01",
            "estado": "activa"
        }
    ]
}
```

### ➕ 3.2 Asignar Propietario/Inquilino
**Método:** `POST`  
**URL:** `http://127.0.0.1:8000/api/propiedades/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "vivienda": 1,
    "persona": 2,
    "tipo_tenencia": "propietario",
    "porcentaje_propiedad": "100.00",
    "fecha_inicio_tenencia": "2025-01-01"
}
```

**Para Inquilino:**
```json
{
    "vivienda": 1,
    "persona": 3,
    "tipo_tenencia": "inquilino",
    "fecha_inicio_tenencia": "2025-01-01",
    "fecha_fin_tenencia": "2025-12-31"
}
```

### 🔍 3.3 Ver Propiedad Específica
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/propiedades/{id}/`  
**Authorization:** Bearer Token

### ✏️ 3.4 Actualizar Propiedad
**Método:** `PUT`  
**URL:** `http://127.0.0.1:8000/api/propiedades/{id}/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "vivienda": 1,
    "persona": 2,
    "tipo_tenencia": "propietario",
    "porcentaje_propiedad": "50.00",
    "fecha_inicio_tenencia": "2025-01-01"
}
```

### ❌ 3.5 Desactivar Propiedad
**Método:** `DELETE`  
**URL:** `http://127.0.0.1:8000/api/propiedades/{id}/`  
**Authorization:** Bearer Token

---

## 👤 4. GESTIÓN DE PERSONAS (MODELO CONSOLIDADO AUTHZ)

### 📋 4.1 Listar Todas las Personas
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/personas/`  
**Authorization:** Bearer Token

**Parámetros opcionales:**
- `search=García` - Buscar por nombre/apellido/documento
- `documento_identidad=12345678` - Filtrar por documento
- `ordering=apellido` - Ordenar por campo

**Respuesta esperada:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 1,
            "nombre": "Ana María",
            "apellido": "Rodríguez Silva",
            "documento_identidad": "87654321",
            "telefono": "+591 70123456",
            "email": "ana.rodriguez@email.com",
            "fecha_creacion": "2024-01-01T10:00:00Z",
            "propiedades_activas": 1,
            "es_propietario": true,
            "es_inquilino": false
        }
    ]
}
```

### ➕ 4.2 Crear Nueva Persona
**Método:** `POST`  
**URL:** `http://127.0.0.1:8000/api/personas/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "nombre": "Roberto Carlos",
    "apellido": "Mendoza Torres",
    "documento_identidad": "98765432",
    "telefono": "+591 70555666",
    "email": "roberto.mendoza@email.com"
}
```

**Respuesta esperada (201):**
```json
{
    "id": 26,
    "nombre": "Roberto Carlos",
    "apellido": "Mendoza Torres",
    "documento_identidad": "98765432",
    "telefono": "+591 70555666",
    "email": "roberto.mendoza@email.com",
    "fecha_creacion": "2025-01-15T16:30:00Z",
    "propiedades_activas": 0,
    "es_propietario": false,
    "es_inquilino": false
}
```

### 🏠 4.3 Solo Propietarios
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/personas/propietarios/`  
**Authorization:** Bearer Token

### 🏘️ 4.4 Solo Inquilinos
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/personas/inquilinos/`  
**Authorization:** Bearer Token

### 🔍 4.5 Ver Persona Específica
**Método:** `GET`  
**URL:** `http://127.0.0.1:8000/api/personas/{id}/`  
**Authorization:** Bearer Token

### ✏️ 4.6 Actualizar Persona
**Método:** `PUT` / `PATCH`  
**URL:** `http://127.0.0.1:8000/api/personas/{id}/`  
**Authorization:** Bearer Token  
**Body (raw JSON):**
```json
{
    "telefono": "+591 70999888",
    "email": "nuevo.email@email.com"
}
```

---

## 🧪 5. CASOS DE PRUEBA RECOMENDADOS

### ✅ Test 1: Flujo Completo Nueva Vivienda con Propietario
1. **Crear persona** → POST `/api/personas/`
2. **Crear vivienda** → POST `/api/viviendas/`
3. **Asignar propietario** → POST `/api/propiedades/`
4. **Verificar asignación** → GET `/api/viviendas/{id}/propiedades/`
5. **Ver estadísticas actualizadas** → GET `/api/viviendas/estadisticas/`

### ✅ Test 2: Validaciones de Modelo Consolidado
1. **Crear persona con documento duplicado** (debe fallar)
2. **Asignar propietario con porcentaje > 100%** (debe fallar)
3. **Crear vivienda con número duplicado** (debe fallar)
4. **Eliminar persona con propiedades activas** (debe fallar)

### ✅ Test 3: Búsquedas y Filtros Avanzados
1. **Buscar personas** → GET `/api/personas/?search=García`
2. **Filtrar viviendas por estado** → GET `/api/viviendas/?estado=activa`
3. **Solo propietarios** → GET `/api/personas/propietarios/`
4. **Propiedades por vivienda** → GET `/api/propiedades/?vivienda=1`

### ✅ Test 4: Actualizaciones Parciales
1. **Actualizar tarifa de vivienda** → PATCH `/api/viviendas/{id}/`
2. **Actualizar teléfono de persona** → PATCH `/api/personas/{id}/`
3. **Cambiar porcentaje de propiedad** → PUT `/api/propiedades/{id}/`

---

## 📝 6. RESPUESTAS Y CÓDIGOS DE ERROR

### ✅ Respuesta Exitosa (200/201)
```json
{
    "id": 1,
    "numero_casa": "101A",
    "bloque": "A",
    "tipo_vivienda": "departamento",
    "tipo_vivienda_display": "Departamento",
    "metros_cuadrados": "85.50",
    "tarifa_base_expensas": "250.00",
    "estado": "activa",
    "estado_display": "Activa",
    "propiedades": [],
    "total_propietarios": 0
}
```

### ❌ Error de Validación (400)
```json
{
    "numero_casa": ["Ya existe una vivienda con este número"],
    "documento_identidad": ["Ya existe una persona con este documento"]
}
```

### 🔐 Error de Autenticación (401)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 🚫 Error de Permisos (403)
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 🔍 Recurso No Encontrado (404)
```json
{
    "detail": "Not found."
}
```

---

## 🎯 7. CONFIGURACIÓN POSTMAN OPTIMIZADA

### 📁 Estructura de Collection Recomendada
```
CU05 - Gestión Unidades Habitacionales/
├── 🔑 Autenticación/
│   └── Login JWT
├── 🏠 Viviendas/
│   ├── Listar Viviendas
│   ├── Crear Vivienda
│   ├── Ver Vivienda
│   ├── Actualizar Vivienda
│   ├── Eliminar Vivienda
│   └── Estadísticas
├── 👥 Personas/
│   ├── Listar Personas
│   ├── Crear Persona
│   ├── Solo Propietarios
│   └── Solo Inquilinos
└── 🏘️ Propiedades/
    ├── Listar Propiedades
    ├── Asignar Propiedad
    ├── Ver Propiedad
    └── Actualizar Propiedad
```

### 🔄 Variables de Entorno
```json
{
    "base_url": "http://127.0.0.1:8000",
    "token": "{{jwt_token}}",
    "persona_id": "1",
    "vivienda_id": "1",
    "propiedad_id": "1"
}
```

### 🧪 Scripts de Prueba Automática
```javascript
// Pre-request Script (para login)
pm.sendRequest({
    url: pm.environment.get("base_url") + "/api/auth/login/",
    method: 'POST',
    header: {
        'Content-Type': 'application/json'
    },
    body: {
        mode: 'raw',
        raw: JSON.stringify({
            "email": "admin@condominio.com",
            "password": "admin123"
        })
    }
}, function (err, response) {
    if (response.code === 200) {
        const jsonData = response.json();
        pm.environment.set("jwt_token", jsonData.access);
    }
});

// Test Script (validaciones)
pm.test("Status code is successful", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
});

// Guardar IDs para siguientes requests
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    if (jsonData.numero_casa) {
        pm.environment.set("vivienda_id", jsonData.id);
    }
    if (jsonData.documento_identidad) {
        pm.environment.set("persona_id", jsonData.id);
    }
}
```

---

## 🔄 8. INTEGRACIÓN CON MODELO CONSOLIDADO

### 📊 Campos Actualizados
- **Personas**: Usa `authz.Persona` con campos `nombre`, `apellido`, `documento_identidad`
- **Usuarios**: Usa `authz.Usuario` vinculado a `Persona`
- **Relaciones**: Usa `authz.RelacionesPropietarioInquilino` para vínculos
- **Viviendas**: Mantiene estructura en `core.Vivienda`
- **Propiedades**: Usa `core.Propiedad` referenciando `authz.Persona`

### 🔗 Endpoints Principales
- `/api/auth/` - Autenticación con modelos authz
- `/api/personas/` - CRUD personas (authz.Persona)
- `/api/viviendas/` - CRUD viviendas (core.Vivienda)
- `/api/propiedades/` - CRUD asignaciones (core.Propiedad)

---

## 🚀 ¡LISTO PARA PROBAR CON MODELO CONSOLIDADO!

Esta guía está actualizada para trabajar con:
- ✅ Modelos authz consolidados
- ✅ Campos correctos (nombre/apellido, documento_identidad)
- ✅ Relaciones actualizadas
- ✅ Validaciones integradas
- ✅ Scripts Postman optimizados

**¿Necesitas ayuda con alguna prueba específica del modelo consolidado?** 🤔