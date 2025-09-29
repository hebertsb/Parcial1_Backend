from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import FamiliarPropietario
from .serializers_familiares import FamiliarPropietarioRegistroSerializer

class FamiliarPropietarioViewSet(viewsets.ModelViewSet):
    queryset = FamiliarPropietario.objects.all()
    serializer_class = FamiliarPropietarioRegistroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # Opcional: filtrar por propietario autenticado
        propietario = self.request.user
        return FamiliarPropietario.objects.filter(propietario=propietario)
