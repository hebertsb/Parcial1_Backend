# URLs para CU05 - Gestionar Unidades Habitacionales
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'viviendas', views.ViviendaViewSet, basename='vivienda')
router.register(r'propiedades', views.PropiedadViewSet, basename='propiedad')
router.register(r'personas', views.PersonaViewSet, basename='persona')

app_name = 'viviendas_api'

urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]

# Las URLs generadas automáticamente serán:
# 
# VIVIENDAS:
# GET    /viviendas/                     - Listar viviendas
# POST   /viviendas/                     - Crear vivienda
# GET    /viviendas/{id}/                - Obtener vivienda específica
# PUT    /viviendas/{id}/                - Actualizar vivienda completa
# PATCH  /viviendas/{id}/                - Actualizar vivienda parcial
# DELETE /viviendas/{id}/                - Eliminar vivienda (marcar inactiva)
# POST   /viviendas/{id}/activar/        - Activar vivienda
# GET    /viviendas/{id}/propiedades/    - Propiedades de una vivienda
# GET    /viviendas/estadisticas/        - Estadísticas generales
#
# PROPIEDADES:
# GET    /propiedades/                   - Listar propiedades
# POST   /propiedades/                   - Crear propiedad
# GET    /propiedades/{id}/              - Obtener propiedad específica
# PUT    /propiedades/{id}/              - Actualizar propiedad completa
# PATCH  /propiedades/{id}/              - Actualizar propiedad parcial
# DELETE /propiedades/{id}/              - Eliminar propiedad (desactivar)
#
# PERSONAS:
# GET    /personas/                      - Listar personas
# GET    /personas/{id}/                 - Obtener persona específica
# GET    /personas/propietarios/         - Solo propietarios
# GET    /personas/inquilinos/           - Solo inquilinos