# 👑 DOCUMENTACIÓN PARA ADMINISTRADORES

## 📁 **Contenido de esta Carpeta**

Esta carpeta contiene toda la documentación específica para usuarios con **rol de Administrador** en el sistema de condominio.

---

## 📚 **Archivos Disponibles:**

### **🏢 GUIA_ADMINISTRADOR.md**
- **Descripción:** Guía completa para administradores del sistema
- **Contenido:** 
  - Funciones y permisos de administrador
  - Endpoints disponibles para gestión total
  - Ejemplos de uso de todas las APIs
  - Gestión de usuarios, viviendas y propiedades
  - Protocolos de seguridad y emergencia

### **🛡️ INFORME_SEGURIDAD_ROLES.md**
- **Descripción:** Análisis detallado de la seguridad del sistema
- **Contenido:**
  - Verificación de protección de roles
  - Resultados de pruebas de seguridad
  - Matriz de permisos por rol
  - Vulnerabilidades encontradas y mitigadas

---

## 🎯 **Información Clave para Administradores:**

### **🔐 Nivel de Acceso: MÁXIMO**
- ✅ Control total del sistema
- ✅ Gestión de todos los usuarios
- ✅ CRUD completo de viviendas y propiedades
- ✅ Aprobación de solicitudes de propietarios
- ✅ Acceso a estadísticas completas
- ✅ Configuración del sistema

### **👤 Credenciales por Defecto:**
- **Email:** `admin@condominio.com`
- **Password:** `admin123`
- ⚠️ **IMPORTANTE:** Cambiar inmediatamente en producción

---

## 🚨 **Responsabilidades Críticas:**

1. **👥 Gestión de Usuarios:**
   - Crear y activar cuentas de propietarios e inquilinos
   - Asignar roles apropiados
   - Mantener la seguridad del sistema

2. **🏠 Gestión de Propiedades:**
   - Aprobar solicitudes de propietarios
   - Asignar viviendas correctamente
   - Mantener datos actualizados

3. **🔒 Seguridad del Sistema:**
   - Monitorear intentos de acceso no autorizados
   - Revisar logs de seguridad regularmente
   - Mantener backups actualizados

---

## 🛠️ **Herramientas Administrativas:**

### **🔧 Comandos Django Útiles:**
```bash
# Verificar seguridad del sistema
python manage.py test_security_roles

# Crear usuario administrador de emergencia
python manage.py createsuperuser

# Verificar migraciones
python manage.py showmigrations
```

### **🌐 Interfaces de Administración:**
- **Django Admin:** `/admin/` - Panel completo de administración
- **API REST:** `/api/` - Endpoints programáticos
- **Documentación API:** `/api/docs/` - Si está configurada

---

## 📊 **Monitoreo y Métricas:**

### **📈 KPIs Importantes:**
- Total de usuarios activos
- Solicitudes pendientes de aprobación
- Viviendas ocupadas vs disponibles
- Intentos de acceso fallidos
- Tiempo de respuesta del sistema

### **🚨 Alertas Críticas:**
- Múltiples intentos de login fallidos
- Accesos no autorizados
- Errores en el sistema
- Caídas de servicios

---

## 🔗 **Enlaces a Documentación Relacionada:**

- **[CU05 - Gestión de Unidades](../CU05_Gestionar_Unidades_Habitacionales/)** - Documentación técnica completa
- **[Guía de Propietarios](../Propietarios/)** - Para entender el rol de propietarios
- **[Guía de Inquilinos](../Inquilinos/)** - Para entender el rol de inquilinos
- **[Análisis de Seguridad](../Seguridad/)** - Información detallada de seguridad

---

## ⚡ **Acceso Rápido:**

### **🏠 Gestión de Viviendas:**
- `GET /api/viviendas/` - Listar todas las viviendas
- `POST /api/viviendas/` - Crear nueva vivienda
- `GET /api/viviendas/estadisticas/` - Ver estadísticas del condominio

### **👥 Gestión de Usuarios:**
- `GET /api/usuarios/` - Listar todos los usuarios
- `POST /api/usuarios/{id}/inhabilitar/` - Desactivar usuario
- `GET /api/usuarios/clientes/` - Ver solo inquilinos

### **📝 Gestión de Solicitudes:**
- `GET /api/solicitudes-propietarios/?estado=PENDIENTE` - Solicitudes pendientes
- `PATCH /api/solicitudes-propietarios/{id}/` - Aprobar/rechazar solicitud

---

**🎯 COMO ADMINISTRADOR, TIENES LA RESPONSABILIDAD TOTAL DEL SISTEMA**

Usa esta documentación para gestionar eficientemente el condominio digital y mantener la seguridad y funcionalidad del sistema.

---

*Documentación actualizada: 24 de septiembre de 2025*