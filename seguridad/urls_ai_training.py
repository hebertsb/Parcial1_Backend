# seguridad/urls_ai_training.py - URLs para entrenamiento de IA
from django.urls import path
from . import views_ai_training

urlpatterns = [
    # Endpoints de Entrenamiento de IA
    path('ia/entrenar/', views_ai_training.entrenar_ia_automatico, name='entrenar_ia_automatico'),
    path('ia/re-entrenar/', views_ai_training.re_entrenar_ia, name='re_entrenar_ia'),
    path('ia/estadisticas/', views_ai_training.estadisticas_modelo_ia, name='estadisticas_modelo_ia'),
    path('ia/probar/', views_ai_training.probar_modelo_entrenado, name='probar_modelo_entrenado'),
    path('ia/dashboard/', views_ai_training.dashboard_entrenamiento_ia, name='dashboard_entrenamiento_ia'),
]