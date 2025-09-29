from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models.propiedades_residentes import Visita
from core.api.visitas.serializers import VisitaSerializer

class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print("[DEBUG][VisitaViewSet.perform_create] validated_data:", getattr(serializer, 'validated_data', None))
        # Asigna automáticamente la persona_autorizante si es necesario
        if not serializer.validated_data.get('persona_autorizante'):
            user = self.request.user
            print(f"[DEBUG][VisitaViewSet.perform_create] user: {user}, tiene persona: {hasattr(user, 'persona')}")
            if hasattr(user, 'persona'):
                serializer.save(persona_autorizante=user.persona)
            else:
                serializer.save()
        else:
            serializer.save()

    @action(detail=False, methods=['get'], url_path='pendientes-guardia')
    def pendientes_guardia(self, request):
        """Devuelve solo las visitas programadas (pendientes de acceso) para el guardia, con fotos de reconocimiento facial."""
        visitas = Visita.objects.filter(estado='programada').order_by('fecha_hora_programada')
        serializer = self.get_serializer(visitas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='del-dia-seguridad')
    def visitas_del_dia_seguridad(self, request):
        """
        Endpoint para listar todas las visitas del día actual.
        Solo usuarios con rol Seguridad pueden acceder.
        """
        from datetime import datetime, timedelta
        hoy = datetime.now().date()
        visitas = Visita.objects.filter(
            fecha_hora_programada__date=hoy
        ).order_by('fecha_hora_programada')

        # Validar rol Seguridad
        usuario = request.user
        tiene_rol_seguridad = hasattr(usuario, 'roles') and usuario.roles.filter(nombre='Seguridad').exists()
        if not tiene_rol_seguridad:
            return Response({'detail': 'No tiene permisos para ver las visitas del día.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(visitas, many=True)
        return Response(serializer.data)
