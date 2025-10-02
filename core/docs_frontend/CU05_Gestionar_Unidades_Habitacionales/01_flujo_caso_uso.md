# 🏠 CU05 - Gestionar Unidades Habitacionales
## Flujo Completo del Caso de Uso

### 📋 **INFORMACIÓN GENERAL**

**Caso de Uso**: CU05 - Gestionar Unidades Habitacionales  
**Actor Principal**: Administrador del Condominio  
**Objetivo**: Permitir al administrador gestionar las unidades habitacionales del condominio (viviendas), incluyendo crear, actualizar, consultar y asignar propietarios/inquilinos.

---

## 🔄 **FLUJO PRINCIPAL**

### **1. Pantalla Inicial - Dashboard de Viviendas**
- **Vista**: Lista de todas las viviendas del condominio
- **Información mostrada**:
  - Número de casa/departamento
  - Tipo de vivienda (casa, departamento, local)
  - Estado (activa, inactiva, mantenimiento)
  - Propietario/Inquilino actual
  - Tarifa de expensas
- **Acciones disponibles**:
  - ➕ Crear nueva vivienda
  - 🔍 Buscar/filtrar viviendas
  - 📊 Ver estadísticas del condominio
  - ⚙️ Acciones por vivienda (ver, editar, eliminar)

### **2. Crear Nueva Vivienda**
**Flujo**:
1. Usuario hace clic en "➕ Nueva Vivienda"
2. Se abre formulario modal/página con campos:
   - Número de casa/departamento (requerido)
   - Bloque (requerido)
   - Tipo de vivienda (dropdown: casa, departamento, local)
   - Metros cuadrados (número decimal)
   - Tarifa base de expensas (moneda)
   - Tipo de cobranza (dropdown: por_casa, por_metro)
   - Estado (dropdown: activa, inactiva, mantenimiento)
3. Usuario completa formulario
4. Sistema valida datos
5. Si es válido → Crea vivienda y actualiza lista
6. Si hay error → Muestra mensaje de error específico

### **3. Editar Vivienda Existente**
**Flujo**:
1. Usuario hace clic en "✏️ Editar" en una vivienda
2. Se abre formulario precargado con datos actuales
3. Usuario modifica campos necesarios
4. Sistema valida cambios
5. Si es válido → Actualiza vivienda y lista
6. Si hay error → Muestra mensaje de error

### **4. Ver Detalles de Vivienda**
**Flujo**:
1. Usuario hace clic en "👁️ Ver detalles" o en el número de vivienda
2. Se abre vista detallada con:
   - **Información básica**: todos los campos de la vivienda
   - **Propiedades**: lista de propietarios/inquilinos
   - **Historial**: cambios recientes (opcional)
3. Desde aquí puede:
   - ✏️ Editar vivienda
   - 👥 Gestionar propiedades
   - 🔄 Cambiar estado

### **5. Asignar Propietario/Inquilino**
**Flujo**:
1. Desde detalles de vivienda, hacer clic en "👥 Gestionar Propiedades"
2. Se muestra lista actual de propiedades
3. Usuario hace clic en "➕ Nueva Asignación"
4. Formulario con campos:
   - Persona (dropdown con búsqueda)
   - Tipo de tenencia (dropdown: propietario, inquilino)
   - Porcentaje de propiedad (número, default 100%)
   - Fecha de inicio (date picker)
   - Fecha de fin (date picker, opcional)
5. Sistema valida que no se exceda 100% de propiedad
6. Crea asignación y actualiza lista

### **6. Búsqueda y Filtros**
**Opciones de filtrado**:
- 🔍 **Búsqueda por texto**: número de casa, bloque
- 📊 **Filtro por estado**: activa, inactiva, mantenimiento
- 🏠 **Filtro por tipo**: casa, departamento, local
- 🏢 **Filtro por bloque**: A, B, C, etc.
- 👤 **Filtro por ocupación**: ocupada, libre

### **7. Estadísticas del Condominio**
**Vista de métricas**:
- 📊 Total de viviendas
- 📈 Distribución por estado
- 🏠 Distribución por tipo
- 💰 Promedio de tarifas
- 📋 Ocupación actual

---

## 🚨 **FLUJOS ALTERNATIVOS**

### **Error en Validación**
- Sistema muestra mensajes de error específicos
- Campos con error se resaltan en rojo
- Usuario puede corregir y reintentar

### **Vivienda No Encontrada**
- Si se intenta acceder a vivienda inexistente
- Mostrar mensaje "Vivienda no encontrada"
- Redirigir a lista principal

### **Sin Permisos**
- Si usuario no tiene permisos para una acción
- Mostrar mensaje "No autorizado"
- Ocultar botones de acciones no permitidas

---

## 🎯 **CRITERIOS DE ACEPTACIÓN**

### ✅ **Funcionalidades Mínimas**
1. **Listar viviendas** con información básica
2. **Crear vivienda** con validación completa
3. **Editar vivienda** parcial o completa
4. **Ver detalles** de vivienda específica
5. **Buscar y filtrar** viviendas
6. **Asignar propietarios/inquilinos**
7. **Ver estadísticas** básicas

### ✅ **Validaciones Requeridas**
- Número de casa único por bloque
- Tarifa debe ser positiva
- Metros cuadrados debe ser positivo
- Porcentaje de propiedad no puede exceder 100%
- Fechas lógicas (inicio <= fin)

### ✅ **Experiencia de Usuario**
- Interfaz intuitiva y responsive
- Mensajes de error claros
- Confirmaciones para acciones destructivas
- Loading states durante operaciones
- Feedback visual inmediato

---

## 📱 **CONSIDERACIONES TÉCNICAS**

### **Autenticación**
- Todas las operaciones requieren token JWT
- Token se obtiene del endpoint `/api/auth/login/`
- Incluir en header: `Authorization: Bearer {token}`

### **Manejo de Estados**
- Loading: Durante peticiones API
- Success: Operación completada exitosamente  
- Error: Error en operación con mensaje específico
- Empty: No hay datos para mostrar

### **Paginación** (Opcional)
- Si hay muchas viviendas, implementar paginación
- El API soporta parámetros `page` y `page_size`

### **Tiempo Real** (Opcional)
- Considerar WebSockets para actualizaciones en tiempo real
- Especialmente útil para estadísticas dinámicas

---

## 🎨 **WIREFRAMES SUGERIDOS**

### **Vista Lista (Desktop)**
```
┌─────────────────────────────────────────────────────────┐
│ 🏠 Gestión de Viviendas                    [➕ Nueva]   │
├─────────────────────────────────────────────────────────┤
│ [🔍 Buscar...] [📊Estado▼] [🏠Tipo▼] [📊Estadísticas] │
├─────────────────────────────────────────────────────────┤
│ Casa    │ Tipo        │ Estado  │ Propietario │ Acciones │
│ 101A    │ Departamento│ Activa  │ Juan Pérez  │ 👁️✏️🗑️   │
│ 102A    │ Departamento│ Activa  │ María G.    │ 👁️✏️🗑️   │
│ 201B    │ Casa        │ Activa  │ Carlos M.   │ 👁️✏️🗑️   │
└─────────────────────────────────────────────────────────┘
```

### **Vista Móvil**
```
┌───────────────────────┐
│ 🏠 Viviendas [➕]     │
├───────────────────────┤
│ [🔍 Buscar...]       │
├───────────────────────┤
│ 📋 101A - Depto      │
│    Juan Pérez        │
│    💰 $250.00        │
│    [Ver] [Editar]    │
├───────────────────────┤
│ 📋 102A - Depto      │
│    María García      │
│    💰 $250.00        │
│    [Ver] [Editar]    │
└───────────────────────┘
```

---

Este flujo proporciona una base sólida para implementar la funcionalidad completa del CU05 en cualquier framework frontend.