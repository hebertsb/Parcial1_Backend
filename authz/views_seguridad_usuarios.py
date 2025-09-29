#!/usr/bin/env python3
"""
VIEW PARA ENDPOINT SEGURIDAD - USUARIOS CON RECONOCIMIENTO
==========================================================
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from authz.models import Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuarios_con_reconocimiento(request):
    """
    Endpoint para seguridad - Lista usuarios que tienen fotos de reconocimiento facial
    URL: /api/authz/seguridad/usuarios-reconocimiento/
    """
    try:
        # Obtener todos los usuarios que tienen reconocimiento facial con fotos
        usuarios_con_fotos = []
        
        # Buscar todos los reconocimientos que tienen fotos
        reconocimientos = ReconocimientoFacial.objects.filter(
            vector_facial__isnull=False
        ).exclude(vector_facial='').select_related('copropietario__usuario_sistema')
        
        for reconocimiento in reconocimientos:
            try:
                copropietario = reconocimiento.copropietario
                usuario = copropietario.usuario_sistema
                
                # Contar fotos
                fotos_urls = reconocimiento.vector_facial.split(',') if reconocimiento.vector_facial else []
                fotos_urls = [url.strip() for url in fotos_urls if url.strip()]
                
                usuario_data = {
                    'id': usuario.id,
                    'email': usuario.email,
                    'nombre_completo': f"{usuario.first_name or ''} {usuario.last_name or ''}".strip() or usuario.email,
                    'reconocimiento_id': reconocimiento.id,
                    'copropietario_id': copropietario.id,
                    'total_fotos': len(fotos_urls),
                    'tiene_fotos': len(fotos_urls) > 0,
                    'unidad_residencial': copropietario.unidad_residencial or 'No asignada',
                    'activo': copropietario.activo,
                    'fecha_registro': copropietario.fecha_creacion.isoformat() if copropietario.fecha_creacion else None
                }
                
                usuarios_con_fotos.append(usuario_data)
                
            except Exception as e:
                # Si hay error con un usuario específico, continuar con los demás
                continue
        
        return Response({
            'success': True,
            'data': usuarios_con_fotos,
            'total': len(usuarios_con_fotos),
            'message': f'Se encontraron {len(usuarios_con_fotos)} usuarios con reconocimiento facial'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error al obtener usuarios con reconocimiento: {str(e)}',
            'data': []
        }, status=500)