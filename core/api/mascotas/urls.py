from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MascotaViewSet

router = DefaultRouter()
router.register(r'mascotas', MascotaViewSet, basename='mascota')

urlpatterns = [
    path('', include(router.urls)),
]