"""
URLs para el panel de propietarios
"""
from django.urls import path
from .views_propietarios_panel import (
    MenuPropietarioView, GestionarFamiliaresView, GestionarInquilinosView
)

urlpatterns = [
    # Menu principal del propietario
    path('menu/', MenuPropietarioView.as_view(), name='menu-propietario'),
    
    # Gestión de familiares (GET para listar, POST para registrar)
    path('familiares/', GestionarFamiliaresView.as_view(), name='gestionar-familiares'),
    
    # Gestión de inquilinos (GET para listar, POST para registrar)
    path('inquilinos/', GestionarInquilinosView.as_view(), name='gestionar-inquilinos'),
]