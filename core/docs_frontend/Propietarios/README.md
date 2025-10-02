# 🏠 DOCUMENTACIÓN PARA PROPIETARIOS

## 📁 **Contenido de esta Carpeta**

Esta carpeta contiene toda la documentación específica para usuarios con **rol de Propietario** en el sistema de condominio.

---

## 📚 **Archivos Disponibles:**

### **🏠 GUIA_PROPIETARIO.md**
- **Descripción:** Guía completa para propietarios del condominio
- **Contenido:** 
  - Funciones específicas de propietarios
  - Cómo ver y gestionar sus propiedades
  - Proceso de solicitudes de registro
  - Gestión de perfil personal
  - Comunicación con administración

---

## 🎯 **Información Clave para Propietarios:**

### **🔐 Nivel de Acceso: MEDIO**
- ✅ Ver y gestionar **solo SUS propiedades**
- ✅ Actualizar su información personal
- ✅ Solicitar registro como propietario oficial
- ✅ Ver expensas de sus viviendas
- ✅ Contactar administración
- ❌ **NO** puede gestionar propiedades de otros
- ❌ **NO** tiene acceso administrativo

### **👤 Credenciales de Ejemplo:**
- **Email:** `propietario@condominio.com`
- **Password:** `propietario123`
- ⚠️ **Nota:** Credenciales específicas asignadas por administrador

---

## 🏠 **Tus Derechos como Propietario:**

### **✅ Lo que PUEDES hacer:**
1. **📊 Ver tus propiedades:** Acceso completo a información de tus viviendas
2. **💰 Consultar expensas:** Ver tarifas y cálculos de tus propiedades
3. **📝 Enviar solicitudes:** Registrarte oficialmente como propietario
4. **👤 Actualizar perfil:** Cambiar datos de contacto
5. **📞 Comunicarte:** Contactar administración para dudas
6. **👥 Ver comunidad:** Lista básica de otros propietarios

### **❌ Lo que NO puedes hacer:**
1. **🚫 Crear viviendas:** Solo administradores pueden crear propiedades
2. **🚫 Editar otros propietarios:** Solo tus propios datos
3. **🚫 Eliminar propiedades:** No tienes permisos de eliminación
4. **🚫 Gestionar usuarios:** No puedes crear/desactivar usuarios

---

## 📝 **Proceso de Registro como Propietario:**

### **🚀 Pasos para nuevos propietarios:**

1. **📋 Obtener cuenta:**
   - Contactar al administrador del condominio
   - Proporcionar documento de identidad
   - Recibir credenciales de acceso

2. **📄 Enviar solicitud:**
   - Iniciar sesión en el sistema
   - Ir a "Solicitudes de Propietario"
   - Subir documentación de propiedad (escritura pública, etc.)

3. **⏳ Esperar aprobación:**
   - El administrador revisará documentos
   - Tiempo promedio: 24-48 horas
   - Recibirás notificación del resultado

4. **✅ Acceso completo:**
   - Una vez aprobado, verás todas tus propiedades
   - Podrás gestionar información completa
   - Tendrás acceso a servicios de propietario

---

## 🔗 **Endpoints Principales para Propietarios:**

### **🏠 Gestión de Propiedades:**
```http
GET /api/propietarios/mis-viviendas/     # Ver tus viviendas
GET /api/propietarios/mis-expensas/      # Ver tus expensas
```

### **📝 Solicitudes:**
```http
POST /api/solicitudes-propietarios/      # Enviar nueva solicitud
GET /api/propietarios/mis-solicitudes/   # Ver estado de solicitudes
```

### **👤 Perfil Personal:**
```http
GET /api/propietarios/mi-perfil/         # Ver tu información
PUT /api/propietarios/mi-perfil/         # Actualizar datos
```

---

## 💡 **Tips para Propietarios:**

### **🚀 Uso Eficiente del Sistema:**
1. **Mantén actualizada** tu información de contacto
2. **Revisa regularmente** el estado de tus solicitudes
3. **Guarda** tu token de acceso de forma segura
4. **Documenta** cualquier cambio en tu propiedad

### **📞 Comunicación Efectiva:**
1. **Sé específico** en tus consultas a administración
2. **Incluye** números de vivienda en tus reportes
3. **Usa** los canales oficiales del sistema
4. **Mantén** un tono profesional y respetuoso

---

## 🔒 **Privacidad y Seguridad:**

### **🛡️ Tu Información Protegida:**
- ✅ **Solo TÚ** puedes ver tus propiedades completas
- ✅ **Solo TÚ** puedes editar tus datos personales
- ✅ **Solo TÚ** puedes enviar solicitudes a tu nombre
- ✅ Los demás **NO ven** tu información privada

### **👁️ Información Visible para Otros:**
- ✅ Nombre y apellido
- ✅ Email de contacto (opcional)
- ✅ Teléfono (opcional)
- ✅ Números de vivienda que posees
- ❌ **NO ven** documentos ni solicitudes privadas

---

## 🚨 **Problemas Comunes y Soluciones:**

### **🔑 "No puedo iniciar sesión"**
- **Verifica** tu email y contraseña
- **Contacta** al administrador si olvidaste datos
- **Usa** la función "Recuperar contraseña"

### **🏠 "No veo mis viviendas"**
- **Verifica** que tu solicitud esté aprobada
- **Contacta** administración para confirmar asignación
- **Revisa** el estado de tus solicitudes pendientes

### **📝 "Mi solicitud fue rechazada"**
- **Lee** los comentarios del administrador
- **Corrige** la documentación solicitada
- **Reenvía** con la información correcta

---

## 📞 **Contacto con Administración:**

### **🆘 Para Consultas:**
```http
POST /api/propietarios/contactar-admin/
{
    "asunto": "Tu consulta aquí",
    "mensaje": "Descripción detallada",
    "urgencia": "media"
}
```

### **📧 Para Reportes:**
```http
POST /api/propietarios/reportar-problema/
{
    "tipo_problema": "Tipo de problema",
    "descripcion": "Descripción detallada",
    "vivienda_relacionada": 1
}
```

---

## 🔗 **Enlaces a Documentación Relacionada:**

- **[CU05 - Gestión de Unidades](../CU05_Gestionar_Unidades_Habitacionales/)** - Documentación técnica del sistema
- **[Guía de Administradores](../Administradores/)** - Para entender procesos administrativos
- **[Guía de Inquilinos](../Inquilinos/)** - Si también eres inquilino de otra propiedad
- **[Análisis de Seguridad](../Seguridad/)** - Información sobre protección de datos

---

## ⚡ **Rutina Recomendada:**

### **🗓️ Semanal:**
- **Lunes:** Revisar estado de solicitudes pendientes
- **Miércoles:** Verificar información de propiedades
- **Viernes:** Consultar expensas y tarifas actuales

### **🗓️ Mensual:**
- Actualizar información de contacto si cambió
- Revisar comunicados del condominio
- Verificar que todas tus propiedades estén correctamente registradas

---

**🏠 ¡BIENVENIDO A TU HOGAR DIGITAL!**

Como propietario, tienes acceso a toda la información relevante sobre tus propiedades. Esta documentación te ayudará a aprovechar al máximo el sistema del condominio.

---

*Documentación actualizada: 24 de septiembre de 2025*