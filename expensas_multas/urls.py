from django.urls import path, include
from .views import ExpensasMensualesViewSet  # Asegúrate de que las vistas estén importadas correctamente

app_name = 'expensasMultas'

urlpatterns = [
    # Rutas para el CRUD de ExpensasMensuales
    path('expensas/', ExpensasMensualesViewSet.as_view({'get': 'list', 'post': 'create'}), name='expensas-list-create'),  # Listar y crear
    path('expensas/<int:pk>/', ExpensasMensualesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='expensas-detail'),  # Detalles, actualizar y eliminar
]
