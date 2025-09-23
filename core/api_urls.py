from django.urls import path

from core.views import DemoDebtsView, PendingDebtsView, RegistrarPagoView

app_name = 'pagos'

urlpatterns = [
    path('deudas/', PendingDebtsView.as_view(), name='listar-deudas'),
    path('procesar/', RegistrarPagoView.as_view(), name='registrar-pago'),
    path('demo/', DemoDebtsView.as_view(), name='generar-demo'),
]
