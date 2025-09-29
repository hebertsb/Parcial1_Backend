
# from django.urls import path, include
# from .views import ExpensasMensualesViewSet  # Asegúrate de que las vistas estén importadas correctamente

# app_name = 'expensasMultas'

# urlpatterns = [
#     # Rutas para el CRUD de ExpensasMensuales
#     path('expensas/', ExpensasMensualesViewSet.as_view({'get': 'list', 'post': 'create'}), name='expensas-list-create'),  # Listar y crear
    
#     path('expensas/<int:pk>/', ExpensasMensualesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='expensas-detail'),  # Detalles, actualizar y eliminar
#      path('expensas/<int:pk>/pagar/', ExpensasMensualesViewSet.as_view({'post': 'pagar'}), name='expensas-pagar'),

# ]


# expensas_multas/urls.py
from rest_framework.routers import DefaultRouter
from .views import ExpensasMensualesViewSet, enviar_alerta_expensa_vencida

app_name = 'expensas_multas'

router = DefaultRouter()
router.register(r'expensas', ExpensasMensualesViewSet, basename='expensas')

from django.urls import path

urlpatterns = [
	path('enviar-alerta-expensa-vencida/', enviar_alerta_expensa_vencida, name='enviar_alerta_expensa_vencida'),
] + router.urls
