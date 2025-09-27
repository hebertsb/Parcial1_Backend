from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from core.models.administracion import ReglamentoCondominio
from .serializers import ReglamentoCondominioSerializer

class ReglamentoCondominioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los reglamentos del condominio.
    """
    queryset = ReglamentoCondominio.objects.all()
    serializer_class = ReglamentoCondominioSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Solo el admin puede crear, actualizar o eliminar reglamentos
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        # Los usuarios normales solo pueden ver los reglamentos vigentes
        user = self.request.user
        if user.is_staff:
            return ReglamentoCondominio.objects.all()
        return ReglamentoCondominio.objects.filter(vigente=True)
