# Views para CU05 - Gestionar Unidades Habitacionales
from typing import Any
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Q, Count, Avg, Sum

from core.models.propiedades_residentes import Vivienda, Persona, Propiedad, RelacionesPropietarioInquilino
from .serializers import (
    ViviendaSerializer, ViviendaListSerializer, PropiedadSerializer, 
    PropiedadDetailSerializer, PropiedadCreateSerializer,
    RelacionPropietarioInquilinoSerializer, PersonaBasicSerializer
)


class ViviendaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Viviendas 
    
    Operaciones disponibles:
    - GET /viviendas/ - Listar todas las viviendas
    - POST /viviendas/ - Crear nueva vivienda
    - GET /viviendas/{id}/ - Obtener vivienda específica
    - PUT /viviendas/{id}/ - Actualizar vivienda completa
    - PATCH /viviendas/{id}/ - Actualizar vivienda parcial
    - DELETE /viviendas/{id}/ - Eliminar vivienda
    """
    queryset = Vivienda.objects.all().order_by('numero_casa')
    serializer_class = ViviendaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    # Búsqueda de texto
    search_fields = ['numero_casa', 'bloque']
    
    # Ordenamiento
    ordering_fields = ['numero_casa', 'tipo_vivienda', 'metros_cuadrados', 'tarifa_base_expensas', 'fecha_creacion']
    ordering = ['numero_casa']
    
    def get_serializer_class(self):  # type: ignore[override]
        """Seleccionar serializer según la acción"""
        if self.action == 'list':
            return ViviendaListSerializer
        return ViviendaSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Personalizar eliminación - marcar como inactiva en lugar de eliminar"""
        vivienda = self.get_object()
        
        # Verificar si tiene propiedades activas
        propiedades_activas = vivienda.propiedad_set.filter(activo=True).count()
        if propiedades_activas > 0:
            return Response(
                {
                    'error': 'No se puede eliminar la vivienda porque tiene propietarios/inquilinos activos',
                    'propiedades_activas': propiedades_activas
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marcar como inactiva en lugar de eliminar
        vivienda.estado = 'inactiva'
        vivienda.save()
        
        return Response(
            {'message': 'Vivienda marcada como inactiva exitosamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar una vivienda inactiva"""
        vivienda = self.get_object()
        if vivienda.estado != 'inactiva':
            return Response(
                {'error': 'La vivienda no está inactiva'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vivienda.estado = 'activa'
        vivienda.save()
        
        serializer = self.get_serializer(vivienda)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def propiedades(self, request, pk=None):
        """Obtener todas las propiedades de una vivienda"""
        vivienda = self.get_object()
        propiedades = vivienda.propiedad_set.filter(activo=True)
        serializer = PropiedadDetailSerializer(propiedades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas generales de viviendas"""
        total_viviendas = Vivienda.objects.count()
        por_estado = Vivienda.objects.values('estado').annotate(count=Count('id'))
        por_tipo = Vivienda.objects.values('tipo_vivienda').annotate(count=Count('id'))
        
        # Estadísticas de metros cuadrados
        metros_stats = Vivienda.objects.aggregate(
            promedio_metros=Avg('metros_cuadrados'),
            total_metros=Sum('metros_cuadrados')
        )
        
        # Estadísticas de tarifas
        tarifa_stats = Vivienda.objects.aggregate(
            promedio_tarifa=Avg('tarifa_base_expensas'),
            tarifa_maxima=models.Max('tarifa_base_expensas'),
            tarifa_minima=models.Min('tarifa_base_expensas')
        )
        
        return Response({
            'total_viviendas': total_viviendas,
            'por_estado': list(por_estado),
            'por_tipo': list(por_tipo),
            'metros_cuadrados': metros_stats,
            'tarifas': tarifa_stats
        })


class PropiedadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Propiedades (asignaciones de personas a viviendas)
    """
    queryset = Propiedad.objects.all().order_by('-fecha_inicio_tenencia')
    serializer_class = PropiedadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    # Búsqueda
    search_fields = [
        'vivienda__numero_casa', 
        'persona__nombre', 
        'persona__apellido',
        'persona__documento_identidad'
    ]
    
    # Ordenamiento
    ordering_fields = ['fecha_inicio_tenencia', 'porcentaje_propiedad']
    ordering = ['-fecha_inicio_tenencia']
    
    def get_serializer_class(self):  # type: ignore[override]
        """Seleccionar serializer según la acción"""
        if self.action == 'create':
            return PropiedadCreateSerializer
        elif self.action in ['list', 'retrieve']:
            return PropiedadDetailSerializer
        return PropiedadSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Desactivar propiedad en lugar de eliminar"""
        propiedad = self.get_object()
        propiedad.activo = False
        propiedad.save()
        
        return Response(
            {'message': 'Propiedad desactivada exitosamente'},
            status=status.HTTP_200_OK
        )


class PersonaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar personas
    """
    queryset = Persona.objects.filter(activo=True).order_by('nombre', 'apellido')
    serializer_class = PersonaBasicSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    # Búsqueda
    search_fields = ['nombre', 'apellido', 'documento_identidad', 'email']
    
    # Ordenamiento
    ordering_fields = ['nombre', 'apellido', 'fecha_registro']
    ordering = ['nombre', 'apellido']
    
    @action(detail=False, methods=['get'])
    def propietarios(self, request):
        """Obtener solo personas que son propietarios"""
        propietarios = self.queryset.filter(tipo_persona='propietario')
        serializer = self.get_serializer(propietarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inquilinos(self, request):
        """Obtener solo personas que son inquilinos"""
        inquilinos = self.queryset.filter(tipo_persona='inquilino')
        serializer = self.get_serializer(inquilinos, many=True)
        return Response(serializer.data)