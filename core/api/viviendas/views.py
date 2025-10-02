# Views para CU05 - Gestionar Unidades Habitacionales
from typing import Any
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Q, Count, Avg, Sum

from core.models.propiedades_residentes import Vivienda, Propiedad
from authz.models import Persona, RelacionesPropietarioInquilino
from .serializers import (
    ViviendaSerializer, ViviendaListSerializer, PropiedadSerializer, 
    PropiedadDetailSerializer, PropiedadCreateSerializer,
    RelacionPropietarioInquilinoSerializer, PersonaBasicSerializer,
    PersonaEditSerializer
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
        """
        Personalizar eliminación - marcar como inactiva en lugar de eliminar
        Mejorado: agrega logging y comentario para auditoría/QA
        """
        import logging
        logger = logging.getLogger(__name__)
        vivienda = self.get_object()
        
        propiedades_activas = vivienda.propiedad_set.filter(activo=True).count()
        if propiedades_activas > 0:
            logger.warning(f"Intento de eliminar vivienda con propiedades activas: {vivienda.id} - {propiedades_activas} activos")
            return Response(
                {
                    'error': 'No se puede eliminar la vivienda porque tiene propietarios/inquilinos activos',
                    'propiedades_activas': propiedades_activas
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Auditoría: aquí podrías registrar el usuario que realiza la acción
        vivienda.estado = 'inactiva'
        vivienda.save()
        logger.info(f"Vivienda marcada como inactiva: {vivienda.id}")
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
    
    @action(detail=False, methods=['get'], url_path='estadisticas-frontend')
    def estadisticas_frontend(self, request):
        """
        Endpoint optimizado para el frontend que devuelve viviendas y estadísticas
        en el formato esperado por getEstadisticasViviendas()
        """
        # Obtener todas las viviendas con el serializer completo
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        viviendas_data = serializer.data
        
        # Calcular estadísticas basadas en estado_ocupacion
        total = len(viviendas_data)
        ocupadas = len([v for v in viviendas_data if v.get('estado_ocupacion') == 'ocupada'])
        alquiladas = len([v for v in viviendas_data if v.get('estado_ocupacion') == 'alquilada'])
        disponibles = len([v for v in viviendas_data if v.get('estado_ocupacion') == 'disponible'])
        
        return Response({
            'viviendas': viviendas_data,
            'estadisticas': {
                'total': total,
                'ocupadas': ocupadas,
                'alquiladas': alquiladas,
                'disponibles': disponibles
            }
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


class PersonaViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestionar personas
    
    Operaciones disponibles:
    - GET /personas/ - Listar todas las personas
    - POST /personas/ - Crear nueva persona
    - GET /personas/{id}/ - Obtener persona específica
    - PUT /personas/{id}/ - Actualizar persona completa
    - PATCH /personas/{id}/ - Actualizar persona parcial
    - DELETE /personas/{id}/ - Desactivar persona
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
    
    def get_serializer_class(self):
        """
        Usar diferentes serializers según la acción:
        - Para operaciones de escritura (POST, PUT, PATCH): PersonaEditSerializer
        - Para operaciones de lectura (GET): PersonaBasicSerializer
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PersonaEditSerializer
        return PersonaBasicSerializer
    
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
    
    def destroy(self, request, *args, **kwargs):
        """Desactivar persona en lugar de eliminar"""
        persona = self.get_object()
        
        # Verificar si tiene propiedades activas
        propiedades_activas = Propiedad.objects.filter(persona=persona, activo=True).count()
        if propiedades_activas > 0:
            return Response(
                {
                    'error': 'No se puede desactivar la persona porque tiene propiedades activas',
                    'propiedades_activas': propiedades_activas,
                    'mensaje': 'Primero debe transferir o desactivar las propiedades asociadas'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marcar como inactiva
        persona.activo = False
        persona.save()
        
        return Response(
            {'message': 'Persona desactivada exitosamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['patch'])
    def cambiar_tipo(self, request, pk=None):
        """
        Cambiar tipo de persona (ej: inquilino -> propietario)
        
        Casos de uso:
        - Inquilino compra la propiedad y se convierte en propietario
        - Propietario vende y se convierte en inquilino
        - Cambios administrativos de roles
        """
        persona = self.get_object()
        nuevo_tipo = request.data.get('tipo_persona')
        
        if not nuevo_tipo:
            return Response(
                {'error': 'El campo tipo_persona es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tipos permitidos
        tipos_validos = ['administrador', 'seguridad', 'propietario', 'inquilino', 'cliente']
        if nuevo_tipo not in tipos_validos:
            return Response(
                {'error': f'Tipo inválido. Tipos válidos: {", ".join(tipos_validos)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tipo_anterior = persona.tipo_persona
        persona.tipo_persona = nuevo_tipo
        persona.save()
        
        # 🔄 SINCRONIZAR ROLES AUTOMÁTICAMENTE
        from authz.utils_roles import sincronizar_roles_con_tipo_persona
        resultado_sync = sincronizar_roles_con_tipo_persona(persona)
        
        # Log del cambio
        from django.utils import timezone
        cambio_info = {
            'persona_id': persona.id,
            'nombre_completo': persona.nombre_completo,
            'tipo_anterior': tipo_anterior,
            'tipo_nuevo': nuevo_tipo,
            'fecha_cambio': timezone.now(),
            'usuario_admin': request.user.email if hasattr(request.user, 'email') else 'Sistema',
            'sincronizacion_roles': resultado_sync  # ⭐ NUEVA INFO
        }
        
        serializer = self.get_serializer(persona)
        return Response({
            'message': f'Tipo de persona cambiado de {tipo_anterior} a {nuevo_tipo}',
            'persona': serializer.data,
            'cambio_registrado': cambio_info
        })
    
    @action(detail=True, methods=['post'])
    def transferir_propiedad(self, request, pk=None):
        """
        Transferir propiedad específica cuando inquilino compra la casa
        
        PROCESO CORREGIDO (específico por vivienda):
        1. Validar que el inquilino sea específico de UNA vivienda
        2. Transferir ownership solo de ESA vivienda específica
        3. Manejar solo al propietario anterior de ESA vivienda
        4. NO afectar otros usuarios o propiedades
        5. Actualizar relaciones solo de esa vivienda específica
        
        IMPORTANTE: Este endpoint solo afecta UNA propiedad específica, no todas.
        """
        from django.db import transaction
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        inquilino = self.get_object()
        
        # Log del inicio de transferencia
        logger.info(f"🏠 INICIO transferencia propiedad para inquilino: {inquilino.nombre_completo} (ID: {inquilino.id})")
        accion_propietario_anterior = request.data.get('accion_propietario_anterior', 'desactivar')  # 'desactivar' o 'inquilino'
        
        # Validar que sea inquilino
        if inquilino.tipo_persona != 'inquilino':
            return Response(
                {'error': 'Solo se puede transferir propiedad a personas que son inquilinos actualmente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar propiedades donde esta persona es inquilino
        propiedades_como_inquilino = Propiedad.objects.filter(
            persona=inquilino,
            tipo_tenencia='inquilino',
            activo=True
        )
        
        if not propiedades_como_inquilino.exists():
            return Response(
                {'error': 'Esta persona no tiene propiedades activas como inquilino'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transferencias_realizadas = []
        
        try:
            with transaction.atomic():
                logger.info(f"📋 Propiedades encontradas como inquilino: {propiedades_como_inquilino.count()}")
                
                for propiedad_inquilino in propiedades_como_inquilino:
                    vivienda = propiedad_inquilino.vivienda
                    logger.info(f"🏡 Procesando vivienda: {vivienda.numero_casa}")
                    
                    # Buscar el propietario anterior de esta vivienda ESPECÍFICA
                    propiedad_propietario = Propiedad.objects.filter(
                        vivienda=vivienda,
                        tipo_tenencia='propietario',
                        activo=True
                    ).first()
                    
                    if propiedad_propietario:
                        logger.info(f"👤 Propietario anterior encontrado: {propiedad_propietario.persona.nombre_completo} (ID: {propiedad_propietario.persona.id})")
                    
                    if propiedad_propietario:
                        propietario_anterior = propiedad_propietario.persona
                        
                        # 1. Desactivar la propiedad del propietario anterior
                        propiedad_propietario.activo = False
                        propiedad_propietario.fecha_fin_tenencia = timezone.now().date()
                        propiedad_propietario.save()
                        
                        # 2. Convertir la propiedad del inquilino a propietario
                        propiedad_inquilino.tipo_tenencia = 'propietario'
                        propiedad_inquilino.porcentaje_propiedad = propiedad_propietario.porcentaje_propiedad
                        propiedad_inquilino.save()
                        
                        # 3. Manejar al propietario anterior según la acción solicitada
                        # IMPORTANTE: NO desactivar la persona completa, solo manejar esta propiedad específica
                        
                        if accion_propietario_anterior == 'desactivar':
                            # ❌ NO HACER ESTO: propietario_anterior.activo = False 
                            # ✅ SOLO desactivar la propiedad específica (ya hecho arriba)
                            
                            # Verificar si tiene otras propiedades activas
                            otras_propiedades_activas = Propiedad.objects.filter(
                                persona=propietario_anterior,
                                activo=True
                            ).exclude(id=propiedad_propietario.id).exists()
                            
                            if not otras_propiedades_activas:
                                # Solo si NO tiene otras propiedades, cambiar tipo_persona
                                # Mantener activo=True pero cambiar tipo
                                propietario_anterior.tipo_persona = 'residente'
                                propietario_anterior.save()
                                estado_anterior = 'sin propiedades activas - tipo cambiado a residente'
                            else:
                                # Mantener como propietario porque tiene otras propiedades
                                estado_anterior = 'mantiene otras propiedades - sigue como propietario'
                                
                        elif accion_propietario_anterior == 'inquilino':
                            # Crear nueva propiedad como inquilino EN ESTA VIVIENDA
                            Propiedad.objects.create(
                                vivienda=vivienda,
                                persona=propietario_anterior,
                                tipo_tenencia='inquilino',
                                porcentaje_propiedad=Decimal('100.00'),
                                fecha_inicio_tenencia=timezone.now().date(),
                                activo=True
                            )
                            
                            # Solo cambiar tipo_persona si NO tiene otras propiedades como propietario
                            otras_propiedades_propietario = Propiedad.objects.filter(
                                persona=propietario_anterior,
                                tipo_tenencia='propietario',
                                activo=True
                            ).exists()
                            
                            if not otras_propiedades_propietario:
                                propietario_anterior.tipo_persona = 'inquilino'
                                propietario_anterior.save()
                                
                                # 🔄 SINCRONIZAR ROLES AUTOMÁTICAMENTE
                                from authz.utils_roles import sincronizar_roles_con_tipo_persona
                                resultado_sync_anterior = sincronizar_roles_con_tipo_persona(propietario_anterior)
                                logger.info(f"🔄 Sincronización roles ex-propietario: {resultado_sync_anterior}")
                                
                                estado_anterior = 'convertido a inquilino de esta vivienda'
                            else:
                                estado_anterior = 'inquilino de esta vivienda - mantiene otras propiedades como propietario'
                        else:
                            # Solo desactivar la propiedad específica, mantener persona activa
                            estado_anterior = 'solo propiedad específica desactivada'
                        
                        # 4. Actualizar relaciones propietario-inquilino si existen
                        relaciones_activas = RelacionesPropietarioInquilino.objects.filter(
                            inquilino_id=inquilino.id,  # Usar _id para acceso directo
                            vivienda=vivienda,  # Usar la instancia directamente
                            activo=True
                        )
                        
                        for relacion in relaciones_activas:
                            relacion.activo = False
                            relacion.fecha_fin = timezone.now().date()
                            relacion.save()
                        
                        transferencias_realizadas.append({
                            'vivienda': vivienda.numero_casa,
                            'vivienda_id': getattr(vivienda, 'id', vivienda.pk),  # Usar pk como fallback
                            'propietario_anterior': propietario_anterior.nombre_completo,
                            'propietario_anterior_id': propietario_anterior.id,
                            'estado_propietario_anterior': estado_anterior,
                            'nuevo_propietario': inquilino.nombre_completo,
                            'porcentaje_transferido': float(propiedad_propietario.porcentaje_propiedad)
                        })
                
                # 5. Cambiar el tipo de persona del inquilino específico a propietario
                # Solo si tiene propiedades como propietario ahora
                propiedades_como_propietario = Propiedad.objects.filter(
                    persona=inquilino,
                    tipo_tenencia='propietario',
                    activo=True
                ).exists()
                
                if propiedades_como_propietario:
                    inquilino.tipo_persona = 'propietario'
                    inquilino.save()
                    
                    # 🔄 SINCRONIZAR ROLES AUTOMÁTICAMENTE
                    from authz.utils_roles import sincronizar_roles_con_tipo_persona
                    resultado_sync_inquilino = sincronizar_roles_con_tipo_persona(inquilino)
                    logger.info(f"🔄 Sincronización roles nuevo propietario: {resultado_sync_inquilino}")
                
        except Exception as e:
            return Response(
                {'error': f'Error durante la transferencia: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Preparar respuesta
        serializer = self.get_serializer(inquilino)
        return Response({
            'message': f'Transferencia de propiedad completada exitosamente',
            'nuevo_propietario': serializer.data,
            'transferencias_realizadas': transferencias_realizadas,
            'total_propiedades_transferidas': len(transferencias_realizadas),
            'fecha_transferencia': timezone.now(),
            'accion_propietarios_anteriores': accion_propietario_anterior
        })
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Reactivar una persona desactivada"""
        persona = self.get_object()
        
        if persona.activo:
            return Response(
                {'error': 'La persona ya está activa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        persona.activo = True
        persona.save()
        
        serializer = self.get_serializer(persona)
        return Response({
            'message': 'Persona reactivada exitosamente',
            'persona': serializer.data
        })