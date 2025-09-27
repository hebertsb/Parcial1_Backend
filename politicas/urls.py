from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReglamentoCondominioViewSet

router = DefaultRouter()
router.register(r'reglamentos', ReglamentoCondominioViewSet, basename='reglamento')

urlpatterns = router.urls
