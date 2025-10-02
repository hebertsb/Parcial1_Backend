# 🚀 CU05 - Guía Mejorada para Implementación Frontend

## 📋 Resumen de Endpoints CRUD Viviendas

| Acción                | Endpoint                                 | Método   | Descripción |
|---------------------- |------------------------------------------|----------|-------------|
| Listar viviendas      | `/api/viviendas/`                        | GET      | Lista todas las viviendas |
| Crear vivienda        | `/api/viviendas/`                        | POST     | Crea una nueva vivienda |
| Ver vivienda          | `/api/viviendas/{id}/`                   | GET      | Obtiene detalles de una vivienda |
| Actualizar vivienda   | `/api/viviendas/{id}/`                   | PATCH/PUT| Actualiza datos de una vivienda |
| Eliminar vivienda     | `/api/viviendas/{id}/`                   | DELETE   | Marca como inactiva (no borra física) |
| Activar vivienda      | `/api/viviendas/{id}/activar/`           | POST     | Reactiva vivienda inactiva |
| Propiedades vivienda  | `/api/viviendas/{id}/propiedades/`       | GET      | Lista propiedades asociadas |
| Estadísticas          | `/api/viviendas/estadisticas/`           | GET      | Obtiene estadísticas generales |

---

## 🏠 Recomendaciones para Integración Frontend

- Usa el servicio `viviendasService` para consumir todos los endpoints.
- Implementa manejo de errores y mensajes claros para el usuario (ej: no se puede eliminar si hay propietarios/inquilinos activos).
- Utiliza los endpoints de activación/desactivación para soft delete y recuperación.
- Integra filtros y ordenamiento usando los parámetros de búsqueda y ordering del backend.
- Muestra badges de estado (`activa`, `inactiva`, `mantenimiento`) y tipo (`casa`, `departamento`, `local`).
- Implementa componentes reutilizables para tarjetas/listas de viviendas.
- Incluye confirmaciones antes de eliminar/desactivar viviendas.
- Sincroniza la UI tras crear/editar/eliminar para mantener la lista actualizada.

---

## ✅ Checklist de QA para Frontend

- [ ] Listar viviendas muestra todos los datos relevantes
- [ ] Crear vivienda funciona y actualiza la lista
- [ ] Editar vivienda actualiza correctamente los datos
- [ ] Eliminar vivienda marca como inactiva y muestra mensaje
- [ ] No permite eliminar si hay propietarios/inquilinos activos
- [ ] Activar vivienda reactiva correctamente
- [ ] Ver propiedades asociadas funciona
- [ ] Estadísticas se muestran correctamente
- [ ] Todos los errores se manejan y muestran al usuario
- [ ] Los estados y tipos se visualizan con colores/iconos
- [ ] Pruebas manuales y automáticas cubren todos los flujos

---

## 🛡️ Auditoría y Seguridad
- Todas las acciones requieren autenticación (token JWT)
- El backend registra intentos de eliminación y cambios de estado para auditoría
- Los endpoints de eliminación y activación están protegidos por permisos

---

**¡Listo para pasar al equipo frontend!**

Esta guía resume los endpoints, recomendaciones y checklist para implementar el caso de uso de viviendas de forma robusta y segura. Si necesitas ejemplos de payloads o componentes, revisa los archivos complementarios en la carpeta CU05.

**Fecha actualización:** 26/09/2025
**Responsable:** GitHub Copilot
