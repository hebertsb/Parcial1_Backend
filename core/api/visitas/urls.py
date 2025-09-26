from rest_framework.routers import DefaultRouter
from .views import VisitaViewSet
from django.urls import path
from .reconocer_acceso_view import ReconocerAccesoVisitaAPIView

router = DefaultRouter()
router.register(r'visitas', VisitaViewSet, basename='visita')

urlpatterns = router.urls

urlpatterns = [
    path('visitas/reconocer_acceso/', ReconocerAccesoVisitaAPIView.as_view(), name='reconocer-acceso-visita'),
]
urlpatterns += router.urls