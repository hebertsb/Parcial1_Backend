# 🏘️ DOCUMENTACIÓN PARA INQUILINOS

## 📁 **Contenido de esta Carpeta**

Esta carpeta contiene toda la documentación específica para usuarios con **rol de Inquilino** en el sistema de condominio.

---

## 📚 **Archivos Disponibles:**

### **🏘️ GUIA_INQUILINO.md**
- **Descripción:** Guía completa para inquilinos del condominio
- **Contenido:** 
  - Funciones específicas de inquilinos
  - Cómo ver información de tu vivienda actual
  - Gestión de perfil personal limitada
  - Comunicación con propietario y administración
  - Normas y reglas del condominio

---

## 🎯 **Información Clave para Inquilinos:**

### **🔐 Nivel de Acceso: BÁSICO**
- ✅ Ver **solo TU vivienda** donde resides
- ✅ Consultar expensas de tu vivienda
- ✅ Actualizar datos de contacto personal
- ✅ Contactar a tu propietario específico
- ✅ Ver información general del condominio
- ❌ **NO** puedes ver otras viviendas
- ❌ **NO** tienes acceso administrativo
- ❌ **NO** puedes editar propiedades

### **👤 Credenciales de Ejemplo:**
- **Email:** `inquilino@condominio.com`
- **Password:** `inquilino123`
- ⚠️ **Nota:** Credenciales asignadas por administrador o propietario

---

## 🏠 **Tus Derechos como Inquilino:**

### **✅ Lo que PUEDES hacer:**
1. **🏠 Ver tu vivienda:** Información completa de donde resides
2. **📋 Ver tu contrato:** Detalles de fechas y condiciones
3. **💰 Consultar expensas:** Ver montos y fechas de pago
4. **👤 Actualizar contacto:** Cambiar teléfono y email
5. **📞 Contactar propietario:** Comunicarte directamente
6. **📝 Reportar problemas:** Mantenimiento y emergencias

### **❌ Lo que NO puedes hacer:**
1. **🚫 Ver otras viviendas:** Solo la que habitas
2. **🚫 Editar la propiedad:** Cambios estructurales
3. **🚫 Gestionar contratos:** Solo visualización
4. **🚫 Acceder a datos** de otros inquilinos o propietarios
5. **🚫 Crear solicitudes** de propietario

---

## 🏠 **Tu Vivienda y Contrato:**

### **📊 Información Disponible:**
- **Número de casa/departamento**
- **Bloque y ubicación**
- **Metros cuadrados**
- **Tipo de vivienda** (casa/departamento)
- **Fechas del contrato** (inicio y fin)
- **Datos del propietario** (nombre y contacto)
- **Expensas mensuales**

### **📋 Detalles del Contrato:**
- Estado actual del contrato
- Tipo de tenencia (inquilino)
- Fechas de vigencia
- Observaciones especiales

---

## 🔗 **Endpoints Principales para Inquilinos:**

### **🏠 Tu Vivienda:**
```http
GET /api/inquilinos/mi-vivienda/     # Ver tu vivienda actual
GET /api/inquilinos/mi-contrato/     # Detalles del contrato
GET /api/inquilinos/mis-expensas/    # Ver expensas
```

### **👤 Perfil Personal:**
```http
GET /api/inquilinos/mi-perfil/       # Ver tu información
PUT /api/inquilinos/mi-perfil/       # Actualizar contacto
```

### **📞 Comunicación:**
```http
POST /api/inquilinos/contactar-propietario/  # Contactar propietario
POST /api/inquilinos/contactar-admin/        # Contactar administración
POST /api/inquilinos/reportar-problema/      # Reportar problemas
```

---

## 📋 **Responsabilidades como Inquilino:**

### **✅ Obligaciones Básicas:**
1. **💰 Pagar expensas** puntualmente
2. **📞 Reportar problemas** oportunamente
3. **🏠 Cuidar la vivienda** que habitas
4. **👥 Respetar** a otros residentes
5. **📋 Seguir normas** del condominio
6. **📧 Mantener actualizada** tu información de contacto

### **⚠️ Prohibiciones Importantes:**
1. **🚫 NO hacer** modificaciones estructurales
2. **🚫 NO subir** música a alto volumen
3. **🚫 NO usar** áreas comunes para fiestas privadas
4. **🚫 NO permitir** ingreso de personas no autorizadas
5. **🚫 NO bloquear** pasillos o áreas de evacuación

---

## 📞 **Comunicación Efectiva:**

### **🏠 Con tu Propietario:**
```http
POST /api/inquilinos/contactar-propietario/
{
    "asunto": "Consulta sobre reparaciones",
    "mensaje": "Descripción del problema",
    "urgencia": "alta",
    "categoria": "mantenimiento"
}
```

### **🏢 Con Administración:**
```http
POST /api/inquilinos/contactar-admin/
{
    "asunto": "Consulta sobre expensas",
    "mensaje": "Descripción de la consulta",
    "tipo_consulta": "expensas"
}
```

### **🚨 Reportar Problemas:**
```http
POST /api/inquilinos/reportar-problema/
{
    "tipo_problema": "mantenimiento",
    "descripcion": "Descripción detallada",
    "ubicacion": "Ubicación específica",
    "urgencia": "media"
}
```

---

## 🔒 **Privacidad y Seguridad:**

### **🛡️ Tu Información Protegida:**
- ✅ **Solo TÚ** puedes ver tus datos completos de contrato
- ✅ **Solo TÚ** puedes actualizar tu información de contacto
- ✅ **Solo TÚ** puedes contactar a tu propietario específico
- ✅ Los demás inquilinos **NO pueden** ver tu información

### **👁️ Información Privada (NO visible para otros):**
- ❌ Tu número de documento
- ❌ Tu historial de pagos
- ❌ Tu información de contrato
- ❌ Tus comunicaciones con el propietario
- ❌ Tu dirección personal

---

## 🚨 **Problemas Comunes y Soluciones:**

### **🔑 "No puedo acceder al sistema"**
**Posibles causas:**
- Contraseña incorrecta
- Usuario desactivado
- Contrato vencido

**Soluciones:**
1. Verifica email y contraseña
2. Contacta al administrador
3. Revisa el estado de tu contrato

### **🏠 "No veo información de mi vivienda"**
**Posibles causas:**
- Contrato no registrado en el sistema
- Rol de usuario incorrecto
- Asignación pendiente

**Soluciones:**
1. Contacta al propietario
2. Solicita al administrador verificar tu registro
3. Confirma que tu contrato esté vigente

### **💰 "Las expensas no coinciden"**
**Posibles causas:**
- Cambio en tarifas
- Metros cuadrados actualizados
- Servicios adicionales

**Soluciones:**
1. Contacta al administrador para aclaración
2. Revisa comunicados del condominio
3. Solicita desglose detallado

---

## 📊 **Información del Condominio:**

### **🏘️ Datos Generales Disponibles:**
```http
GET /api/inquilinos/info-condominio/
```

**Información que puedes ver:**
- Total de bloques
- Total de viviendas (número general)
- Servicios disponibles (ascensor, portería, etc.)
- Horarios de portería
- Contacto de emergencia
- Normas generales del condominio

---

## 💡 **Tips para Inquilinos:**

### **🤝 Convivencia Armoniosa:**
1. **Saluda** a tus vecinos
2. **Respeta** los horarios de silencio
3. **Usa** adecuadamente las áreas comunes
4. **Reporta** problemas constructivamente
5. **Participa** positivamente en la comunidad

### **💻 Uso Eficiente del Sistema:**
1. **Revisa** regularmente el estado de tus expensas
2. **Actualiza** tu información cuando cambies datos
3. **Usa** los canales oficiales para comunicarte
4. **Guarda** evidencia de tus reportes

### **🔒 Seguridad Personal:**
1. **No compartas** tu contraseña del sistema
2. **Cierra sesión** después de usar el sistema
3. **Reporta** accesos sospechosos
4. **Mantén** privada tu información personal

---

## 📞 **Contactos Importantes:**

### **🚨 Emergencias:**
- **Bomberos:** 911
- **Policía:** 110
- **Ambulancia:** 118
- **Portería del Condominio:** [número local]

### **🏢 Condominio:**
- **Administrador:** `admin@condominio.com`
- **Portería:** Disponible 24 horas
- **Mantenimiento:** Horario de oficina
- **Emergencias Técnicas:** [disponible 24/7]

---

## 🗓️ **Rutina Recomendada:**

### **📅 Mensual:**
- **Primera semana:** Revisar expensas del mes
- **Segunda semana:** Verificar estado de tu vivienda y contrato
- **Tercera semana:** Reportar cualquier problema detectado
- **Cuarta semana:** Revisar comunicados del condominio

### **📅 Según Necesidad:**
- Actualizar datos de contacto si cambian
- Contactar propietario para consultas urgentes
- Reportar problemas de mantenimiento inmediatamente

---

## 🔗 **Enlaces a Documentación Relacionada:**

- **[CU05 - Gestión de Unidades](../CU05_Gestionar_Unidades_Habitacionales/)** - Información técnica del sistema
- **[Guía de Propietarios](../Propietarios/)** - Para entender el rol de tu propietario
- **[Guía de Administradores](../Administradores/)** - Para entender procesos administrativos
- **[Análisis de Seguridad](../Seguridad/)** - Información sobre protección de datos

---

## ⚡ **Acceso Rápido a Funciones:**

### **🏠 Mi Vivienda:**
- Ver detalles de mi departamento/casa
- Consultar información del contrato
- Revisar expensas mensuales

### **📞 Comunicación:**
- Contactar a mi propietario
- Reportar problemas de mantenimiento
- Consultar con administración

### **👤 Mi Perfil:**
- Actualizar teléfono y email
- Ver mi información personal
- Cambiar contraseña

---

**🏘️ ¡BIENVENIDO A TU NUEVO HOGAR!**

Como inquilino, tienes acceso a la información esencial para una buena convivencia en el condominio. Esta documentación te ayudará a usar efectivamente el sistema y mantener una relación armoniosa con todos los residentes.

---

*Documentación actualizada: 24 de septiembre de 2025*