# � DOCUMENTACIÓN FRONTEND - SISTEMA DE CONDOMINIO

## 🎯 **ORGANIZACIÓN POR CASOS DE USO Y TIPOS DE USUARIO**

Esta carpeta contiene toda la documentación del sistema de condominio organizada por **casos de uso específicos** y **tipos de usuario**, tal como debe ser para un sistema bien estructurado.

---

## 📂 **ESTRUCTURA DE CARPETAS**

```
docs_frontend/
├── 📁 CU05_Gestionar_Unidades_Habitacionales/     # Caso de Uso 05
│   ├── 01_readme_principal.md                     # Documentación principal del CU
│   ├── 02_descripcion_modelos.md                  # Modelos Django y base de datos
│   ├── 03_endpoints_api.md                        # APIs y endpoints disponibles
│   ├── 04_implementacion_tecnica.md               # Detalles técnicos de implementación
│   ├── 05_guia_postman.md                         # Guía de pruebas con Postman
│   ├── 06_pruebas_manuales.md                     # Scripts de pruebas manuales
│   └── 07_consolidacion_modelos.md                # Consolidación final de modelos
│
├── 📁 Administradores/                            # Documentación para ADMINISTRADORES
│   ├── README.md                                  # Índice de documentación admin
│   ├── GUIA_ADMINISTRADOR.md                      # Guía completa para administradores
│   └── INFORME_SEGURIDAD_ROLES.md                 # Análisis de seguridad del sistema
│
├── 📁 Propietarios/                               # Documentación para PROPIETARIOS
│   ├── README.md                                  # Índice de documentación propietarios
│   └── GUIA_PROPIETARIO.md                        # Guía completa para propietarios
│
├── 📁 Inquilinos/                                 # Documentación para INQUILINOS
│   ├── README.md                                  # Índice de documentación inquilinos
│   └── GUIA_INQUILINO.md                          # Guía completa para inquilinos
│
├── 📁 Seguridad/                                  # Documentación de SEGURIDAD
│   ├── README.md                                  # Índice de documentación seguridad
│   └── ANALISIS_SEGURIDAD_COMPLETO.md            # Análisis completo de seguridad
│
└── README.md                                      # Este archivo (índice general)
```

## 🔄 MODELO CONSOLIDADO AUTHZ

**IMPORTANTE**: Toda la documentación ha sido actualizada para reflejar el modelo consolidado:

### 📊 Modelos Principales:
- **`authz.Persona`**: Datos personales (nombre, apellido, documento_identidad)
- **`authz.Usuario`**: Autenticación (email, password) → vinculado a Persona
- **`core.Vivienda`**: Unidades habitacionales 
- **`core.Propiedad`**: Relación Persona-Vivienda (propietario/inquilino)

### 🔧 Campos Actualizados:
- ✅ `nombre` / `apellido` (NO nombres/apellidos)
- ✅ `documento_identidad` (NO numero_documento)
- ✅ Referencias a `authz.Persona` en lugar de `core.Persona`

## 🔐 Configuración de Git

Esta carpeta está configurada para **NO subirse al repositorio Git** mediante `.gitignore`.

**Motivo**: Contiene documentación específica para desarrolladores frontend que puede incluir:
- Información sensible de configuración
- Notas internas del proyecto
- Documentación que cambia frecuentemente durante desarrollo

## 🚀 Cómo Usar Esta Documentación

### Para Desarrolladores Frontend:

1. **Lee el flujo completo** en `01_flujo_caso_uso.md`
2. **Revisa los payloads** en `02_payloads_api.md`  
3. **Sigue la guía de implementación** en `03_guia_implementacion.md`
4. **Usa los componentes sugeridos** en `04_componentes_sugeridos.md`
5. **Adapta los ejemplos de código** en `05_ejemplos_codigo.md`

### Para Agregar Nuevos Casos de Uso:

1. Crea una nueva subcarpeta con el nombre del caso de uso
2. Copia la estructura de archivos de CU05
3. Adapta el contenido para el nuevo caso de uso
4. Actualiza este README.md

## 📋 Casos de Uso Documentados

- ✅ **CU05 - Gestionar Unidades Habitacionales** (Completado)
- 🔄 **[Próximo Caso de Uso]** (Pendiente)

## 🛠️ Tecnologías Soportadas

La documentación incluye ejemplos para:
- **React** (JavaScript/TypeScript)
- **Vue.js** (JavaScript/TypeScript)
- **Angular** (TypeScript)
- **Vanilla JavaScript**
- **HTML/CSS/Bootstrap**

## 📞 Contacto

Si tienes dudas sobre la implementación, revisa primero la documentación específica del caso de uso que necesitas implementar.

---

**⚠️ Nota**: Esta documentación está sincronizada con el backend. Siempre verifica que estés usando la versión más reciente de la API.