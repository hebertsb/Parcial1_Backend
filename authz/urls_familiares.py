from rest_framework.routers import DefaultRouter
from .views_familiares import FamiliarPropietarioViewSet

router = DefaultRouter()
router.register(r'familiares', FamiliarPropietarioViewSet, basename='familiarpropietario')

urlpatterns = router.urls
