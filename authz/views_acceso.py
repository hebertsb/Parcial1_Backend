from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Persona
from .serializers import PersonaSerializer
from .permissions import IsSeguridad

class ListarAccesosCondominioAPIView(APIView):
    """
    Endpoint para listar todas las personas con acceso al condominio (propietarios, inquilinos, familiares).
    Solo usuarios con rol de seguridad pueden acceder.
    """
    permission_classes = [IsAuthenticated, IsSeguridad]

    def get(self, request):
        personas = Persona.objects.filter(tipo_persona__in=["propietario", "inquilino", "familiar"]).order_by("nombre", "apellido")
        serializer = PersonaSerializer(personas, many=True)
        return Response({
            "success": True,
            "total": len(serializer.data),
            "data": serializer.data
        })
