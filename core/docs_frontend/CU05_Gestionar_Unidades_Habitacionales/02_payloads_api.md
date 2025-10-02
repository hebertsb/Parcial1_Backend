# 📡 CU05 - Payloads y Respuestas de API
## Ejemplos Completos para Frontend

### 🔐 **AUTENTICACIÓN**

#### **Login - Obtener Token JWT**
```http
POST /api/auth/login/
Content-Type: application/json
```

**Payload de Entrada**:
```json
{
    "email": "admin@condominio.com",
    "password": "admin123"
}
```

**Respuesta Exitosa (200)**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk1NDQ4NTIxLCJpYXQiOjE2OTU0NDQ5MjEsImp0aSI6IjFmYjI1ZGZlYjI5NDRhMmZhMTIyNjNmMGZiYzQxY2JhIiwidXNlcl9pZCI6MX0.X8RQ1QZ5X2DT8K7K4V5_5k3J8h1FqY2",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5NTUzMTMyMSwiaWF0IjoxNjk1NDQ0OTIxLCJqdGkiOiI4YjQ1MmRkYWYzNGY0M2Y3YWI4OTU0YjQ1NGI0ZjEyNCIsInVzZXJfaWQiOjF9.P9YQ7W3K8M5N6L2J3F4_8v2T9s6C7rH1"
}
```

**Respuesta Error (401)**:
```json
{
    "detail": "No active account found with the given credentials"
}
```

---

## 🏠 **GESTIÓN DE VIVIENDAS**

### **1. Listar Todas las Viviendas**

```http
GET /api/viviendas/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
[
    {
        "id": 1,
        "numero_casa": "101A",
        "bloque": "A",
        "tipo_vivienda": "departamento",
        "metros_cuadrados": "65.50",
        "tarifa_base_expensas": "250.00",
        "tipo_cobranza": "por_casa",
        "estado": "activa",
        "fecha_creacion": "2025-09-23T00:00:00Z",
        "fecha_modificacion": "2025-09-23T00:00:00Z"
    },
    {
        "id": 2,
        "numero_casa": "102A",
        "bloque": "A",
        "tipo_vivienda": "departamento",
        "metros_cuadrados": "65.50",
        "tarifa_base_expensas": "250.00",
        "tipo_cobranza": "por_casa",
        "estado": "activa",
        "fecha_creacion": "2025-09-23T00:00:00Z",
        "fecha_modificacion": "2025-09-23T00:00:00Z"
    }
]
```

### **2. Crear Nueva Vivienda**

```http
POST /api/viviendas/
Authorization: Bearer {token}
Content-Type: application/json
```

**Payload de Entrada**:
```json
{
    "numero_casa": "301C",
    "bloque": "C",
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "75.50",
    "tarifa_base_expensas": "225.00",
    "tipo_cobranza": "por_casa",
    "estado": "activa"
}
```

**Respuesta Exitosa (201)**:
```json
{
    "id": 6,
    "numero_casa": "301C",
    "bloque": "C",
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "75.50",
    "tarifa_base_expensas": "225.00",
    "tipo_cobranza": "por_casa",
    "estado": "activa",
    "fecha_creacion": "2025-09-23T02:15:30Z",
    "fecha_modificacion": "2025-09-23T02:15:30Z"
}
```

**Respuesta Error de Validación (400)**:
```json
{
    "numero_casa": ["Este campo es requerido."],
    "metros_cuadrados": ["Asegúrese de que este valor sea mayor que 0."],
    "tarifa_base_expensas": ["Asegúrese de que este valor sea mayor que 0."]
}
```

**Respuesta Error Duplicado (400)**:
```json
{
    "non_field_errors": ["Ya existe una vivienda con este número en el bloque C"]
}
```

### **3. Obtener Vivienda Específica**

```http
GET /api/viviendas/1/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
{
    "id": 1,
    "numero_casa": "101A",
    "bloque": "A",
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "65.50",
    "tarifa_base_expensas": "250.00",
    "tipo_cobranza": "por_casa",
    "estado": "activa",
    "fecha_creacion": "2025-09-23T00:00:00Z",
    "fecha_modificacion": "2025-09-23T00:00:00Z"
}
```

**Respuesta Error (404)**:
```json
{
    "detail": "No encontrado."
}
```

### **4. Actualizar Vivienda (Parcial)**

```http
PATCH /api/viviendas/1/
Authorization: Bearer {token}
Content-Type: application/json
```

**Payload de Entrada** (solo campos a cambiar):
```json
{
    "tarifa_base_expensas": "280.00",
    "estado": "mantenimiento"
}
```

**Respuesta Exitosa (200)**:
```json
{
    "id": 1,
    "numero_casa": "101A",
    "bloque": "A",
    "tipo_vivienda": "departamento",
    "metros_cuadrados": "65.50",
    "tarifa_base_expensas": "280.00",
    "tipo_cobranza": "por_casa",
    "estado": "mantenimiento",
    "fecha_creacion": "2025-09-23T00:00:00Z",
    "fecha_modificacion": "2025-09-23T02:20:45Z"
}
```

### **5. Actualizar Vivienda (Completa)**

```http
PUT /api/viviendas/1/
Authorization: Bearer {token}
Content-Type: application/json
```

**Payload de Entrada** (todos los campos):
```json
{
    "numero_casa": "101A",
    "bloque": "A",
    "tipo_vivienda": "casa",
    "metros_cuadrados": "120.00",
    "tarifa_base_expensas": "300.00",
    "tipo_cobranza": "por_metro",
    "estado": "activa"
}
```

### **6. Eliminar Vivienda (Soft Delete)**

```http
DELETE /api/viviendas/1/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
{
    "message": "Vivienda marcada como inactiva exitosamente",
    "vivienda_id": 1,
    "nuevo_estado": "inactiva"
}
```

### **7. Activar Vivienda**

```http
POST /api/viviendas/1/activar/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
{
    "message": "Vivienda activada exitosamente",
    "vivienda_id": 1,
    "estado": "activa"
}
```

### **8. Estadísticas del Condominio**

```http
GET /api/viviendas/estadisticas/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
{
    "total_viviendas": 5,
    "por_estado": {
        "activa": 4,
        "inactiva": 1,
        "mantenimiento": 0
    },
    "por_tipo": {
        "departamento": 2,
        "casa": 2,
        "local": 1
    },
    "promedio_tarifa": "260.00",
    "total_metros_cuadrados": "406.50"
}
```

### **9. Buscar con Filtros**

```http
GET /api/viviendas/?estado=activa&tipo_vivienda=casa&search=201
Authorization: Bearer {token}
```

**Parámetros de Query Disponibles**:
- `search`: Buscar por número de casa o bloque
- `estado`: activa, inactiva, mantenimiento
- `tipo_vivienda`: casa, departamento, local
- `bloque`: A, B, C, etc.
- `ordering`: numero_casa, -fecha_creacion, tarifa_base_expensas

---

## 👥 **GESTIÓN DE PROPIEDADES**

### **10. Listar Propiedades**

```http
GET /api/propiedades/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
[
    {
        "id": 1,
        "vivienda": 1,
        "vivienda_numero": "101A",
        "persona": 1,
        "persona_nombre": "Juan Carlos Pérez López",
        "tipo_tenencia": "propietario",
        "porcentaje_propiedad": "100.00",
        "fecha_inicio_tenencia": "2025-01-01",
        "fecha_fin_tenencia": null,
        "activo": true,
        "fecha_creacion": "2025-09-23T00:00:00Z"
    }
]
```

### **11. Asignar Propietario/Inquilino**

```http
POST /api/propiedades/
Authorization: Bearer {token}
Content-Type: application/json
```

**Payload de Entrada**:
```json
{
    "vivienda": 3,
    "persona": 2,
    "tipo_tenencia": "inquilino",
    "porcentaje_propiedad": "100.00",
    "fecha_inicio_tenencia": "2025-10-01",
    "fecha_fin_tenencia": "2026-09-30"
}
```

**Respuesta Exitosa (201)**:
```json
{
    "id": 5,
    "vivienda": 3,
    "vivienda_numero": "201B",
    "persona": 2,
    "persona_nombre": "María Elena García Rodríguez",
    "tipo_tenencia": "inquilino",
    "porcentaje_propiedad": "100.00",
    "fecha_inicio_tenencia": "2025-10-01",
    "fecha_fin_tenencia": "2026-09-30",
    "activo": true,
    "fecha_creacion": "2025-09-23T02:30:15Z"
}
```

**Respuesta Error Porcentaje Excedido (400)**:
```json
{
    "non_field_errors": ["El total de porcentajes de propiedad para esta vivienda no puede exceder 100%"]
}
```

### **12. Propiedades de una Vivienda**

```http
GET /api/viviendas/1/propiedades/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
[
    {
        "id": 1,
        "persona_id": 1,
        "persona_nombre": "Juan Carlos Pérez López",
        "tipo_tenencia": "propietario",
        "porcentaje_propiedad": "100.00",
        "fecha_inicio_tenencia": "2025-01-01",
        "fecha_fin_tenencia": null,
        "activo": true
    }
]
```

---

## 👤 **GESTIÓN DE PERSONAS**

### **13. Listar Personas**

```http
GET /api/personas/
Authorization: Bearer {token}
```

**Respuesta Exitosa (200)**:
```json
[
    {
        "id": 1,
        "nombre": "Juan Carlos",
        "apellido": "Pérez López",
        "nombre_completo": "Juan Carlos Pérez López",
        "documento_identidad": "12345678",
        "telefono": "+57 300 123 4567",
        "email": "juan.perez@email.com",
        "tipo_persona": "propietario",
        "activo": true
    },
    {
        "id": 2,
        "nombre": "María Elena",
        "apellido": "García Rodríguez",
        "nombre_completo": "María Elena García Rodríguez",
        "documento_identidad": "87654321",
        "telefono": "+57 311 987 6543",
        "email": "maria.garcia@email.com",
        "tipo_persona": "inquilino",
        "activo": true
    }
]
```

### **14. Solo Propietarios**

```http
GET /api/personas/propietarios/
Authorization: Bearer {token}
```

**Respuesta**: Lista filtrada solo con personas que son propietarios.

### **15. Crear Nueva Persona**

```http
POST /api/personas/
Authorization: Bearer {token}
Content-Type: application/json
```

**Payload de Entrada**:
```json
{
    "nombre": "Carlos Eduardo",
    "apellido": "Méndez Silva",
    "documento_identidad": "55667788",
    "telefono": "+57 320 456 7890",
    "email": "carlos.mendez@email.com",
    "fecha_nacimiento": "1985-05-15",
    "genero": "M",
    "tipo_persona": "propietario",
    "direccion": "Calle 123 #45-67"
}
```

**Campos Obligatorios**:
- `nombre`, `apellido`, `documento_identidad`, `email`

**Campos Opcionales**:
- `telefono`, `fecha_nacimiento`, `genero`, `tipo_persona`, `direccion`

**Respuesta Exitosa (201)**:
```json
{
    "id": 15,
    "nombre": "Carlos Eduardo",
    "apellido": "Méndez Silva",
    "nombre_completo": "Carlos Eduardo Méndez Silva",
    "documento_identidad": "55667788",
    "telefono": "+57 320 456 7890",
    "email": "carlos.mendez@email.com",
    "fecha_nacimiento": "1985-05-15",
    "genero": "M",
    "tipo_persona": "propietario",
    "direccion": "Calle 123 #45-67",
    "activo": true,
    "created_at": "2025-09-24T15:30:00Z"
}

---

## 🔄 **CÓDIGOS DE ESTADO HTTP**

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| **200** | OK | Operación exitosa (GET, PUT, PATCH, DELETE) |
| **201** | Created | Recurso creado exitosamente (POST) |
| **400** | Bad Request | Error de validación o datos incorrectos |
| **401** | Unauthorized | Token JWT inválido o ausente |
| **403** | Forbidden | Sin permisos para realizar la acción |
| **404** | Not Found | Recurso no encontrado |
| **409** | Conflict | Conflicto (ej: número de casa duplicado) |
| **500** | Server Error | Error interno del servidor |

---

## 🎯 **HEADERS REQUERIDOS**

### **Para todas las peticiones autenticadas**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### **Para peticiones con datos (POST, PUT, PATCH)**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

---

## 💡 **TIPS PARA FRONTEND**

### **Manejo de Errores**:
```javascript
// Ejemplo de estructura para manejar errores
const handleAPIError = (error) => {
    if (error.response?.status === 400) {
        // Errores de validación - mostrar en formulario
        return error.response.data;
    } else if (error.response?.status === 401) {
        // Token expirado - redirigir a login
        redirectToLogin();
    } else if (error.response?.status === 404) {
        // Recurso no encontrado
        showNotFound();
    } else {
        // Error genérico
        showGenericError();
    }
};
```

### **Validación Frontend**:
```javascript
// Validaciones antes de enviar al API
const validateVivienda = (data) => {
    const errors = {};
    
    if (!data.numero_casa?.trim()) {
        errors.numero_casa = "Número de casa es requerido";
    }
    
    if (!data.metros_cuadrados || data.metros_cuadrados <= 0) {
        errors.metros_cuadrados = "Metros cuadrados debe ser mayor a 0";
    }
    
    if (!data.tarifa_base_expensas || data.tarifa_base_expensas <= 0) {
        errors.tarifa_base_expensas = "Tarifa debe ser mayor a 0";
    }
    
    return errors;
};
```

Esta documentación proporciona todos los payloads necesarios para implementar el frontend del CU05.