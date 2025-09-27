from django.urls import path
from .views import BitacoraAccionesListView, LogSistemaListView

urlpatterns = [
    path('acciones/', BitacoraAccionesListView.as_view(), name='bitacora-acciones-list'),
    path('logs/', LogSistemaListView.as_view(), name='bitacora-logs-list'),
]
