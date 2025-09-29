# ================================
# ENDPOINTS PARA PANEL PROPIETARIO
# ================================

class MiInformacionPropietarioView(APIView):
    """Vista para obtener información completa del propietario autenticado"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener información del propietario",
        description="Obtiene información completa del propietario autenticado incluyendo datos de reconocimiento facial",
        responses={
            200: OpenApiResponse(description="Información obtenida correctamente"),
            404: OpenApiResponse(description="Propietario no encontrado"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def get(self, request):
        """Obtener información completa del propietario autenticado"""
        try:
            from seguridad.models import Copropietarios, ReconocimientoFacial
            import json
            
            usuario = request.user
            
            # Buscar copropietario
            try:
                copropietario = Copropietarios.objects.get(persona_id=usuario.id)
            except Copropietarios.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No se encontró información de copropietario para este usuario'
                }, status=404)
            
            # Buscar reconocimiento facial
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario=copropietario).first()
            
            # Contar fotos
            total_fotos = 0
            if reconocimiento and reconocimiento.fotos_urls:
                try:
                    fotos_list = json.loads(reconocimiento.fotos_urls)
                    total_fotos = len(fotos_list) if isinstance(fotos_list, list) else 0
                except (json.JSONDecodeError, TypeError):
                    total_fotos = 0
            
            data = {
                'usuario_id': usuario.id,
                'email': usuario.email,
                'copropietario_id': copropietario.id,
                'nombre_completo': f"{copropietario.persona.nombre} {copropietario.persona.apellido}",
                'telefono': copropietario.persona.telefono or '',
                'ci': copropietario.persona.ci or '',
                'tiene_reconocimiento': reconocimiento is not None,
                'reconocimiento_id': reconocimiento.id if reconocimiento else None,
                'total_fotos': total_fotos
            }
            
            return Response({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)


class MisFotosPropietarioView(APIView):
    """Vista para obtener las fotos del propietario autenticado"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener fotos del propietario",
        description="Obtiene todas las fotos de reconocimiento facial del propietario autenticado",
        responses={
            200: OpenApiResponse(description="Fotos obtenidas correctamente"),
            404: OpenApiResponse(description="Propietario no encontrado"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def get(self, request):
        """Obtener fotos del propietario autenticado"""
        try:
            from seguridad.models import Copropietarios, ReconocimientoFacial
            import json
            
            usuario = request.user
            
            # Buscar copropietario
            try:
                copropietario = Copropietarios.objects.get(persona_id=usuario.id)
            except Copropietarios.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No se encontró información de copropietario para este usuario'
                }, status=404)
            
            # Buscar reconocimiento facial
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario=copropietario).first()
            
            if not reconocimiento:
                return Response({
                    'success': True,
                    'data': {
                        'total_fotos': 0,
                        'fotos_urls': [],
                        'usuario_email': usuario.email,
                        'tiene_reconocimiento': False
                    }
                })
            
            # Obtener URLs de fotos
            fotos_urls = []
            if reconocimiento.fotos_urls:
                try:
                    fotos_list = json.loads(reconocimiento.fotos_urls)
                    if isinstance(fotos_list, list):
                        fotos_urls = fotos_list
                except (json.JSONDecodeError, TypeError):
                    pass
            
            return Response({
                'success': True,
                'data': {
                    'total_fotos': len(fotos_urls),
                    'fotos_urls': fotos_urls,
                    'usuario_email': usuario.email,
                    'tiene_reconocimiento': True
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)


class SubirFotoPropietarioView(APIView):
    """Vista para subir foto de reconocimiento facial del propietario"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="Subir foto de reconocimiento facial",
        description="Permite al propietario subir una nueva foto para reconocimiento facial",
        responses={
            200: OpenApiResponse(description="Foto subida correctamente"),
            400: OpenApiResponse(description="Error en los datos enviados"),
            404: OpenApiResponse(description="Propietario no encontrado"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def post(self, request):
        """Subir nueva foto de reconocimiento facial"""
        try:
            from seguridad.models import Copropietarios, ReconocimientoFacial
            from core.services.dropbox_service import DropboxService
            import json
            
            usuario = request.user
            
            # Verificar que se envió una foto
            foto = request.FILES.get('foto')
            if not foto:
                return Response({
                    'success': False,
                    'error': 'No se proporcionó ninguna foto'
                }, status=400)
            
            # Validar formato de imagen
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = foto.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return Response({
                    'success': False,
                    'error': 'Formato de imagen no válido. Solo se permiten JPG, PNG, GIF.'
                }, status=400)
            
            # Validar tamaño (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:  # 5MB
                return Response({
                    'success': False,
                    'error': 'La imagen es demasiado grande. Máximo 5MB.'
                }, status=400)
            
            # Buscar copropietario
            try:
                copropietario = Copropietarios.objects.get(persona_id=usuario.id)
            except Copropietarios.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No se encontró información de copropietario para este usuario'
                }, status=404)
            
            # Obtener o crear reconocimiento facial
            reconocimiento, created = ReconocimientoFacial.objects.get_or_create(
                copropietario=copropietario,
                defaults={'activo': True}
            )
            
            # Subir foto a Dropbox
            try:
                dropbox_service = DropboxService()
                foto_url = dropbox_service.subir_foto_reconocimiento(foto, usuario.id)
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error al subir foto a Dropbox: {str(e)}'
                }, status=500)
            
            # Actualizar URLs en base de datos
            fotos_list = []
            if reconocimiento.fotos_urls:
                try:
                    fotos_list = json.loads(reconocimiento.fotos_urls)
                    if not isinstance(fotos_list, list):
                        fotos_list = []
                except (json.JSONDecodeError, TypeError):
                    fotos_list = []
            
            fotos_list.append(foto_url)
            reconocimiento.fotos_urls = json.dumps(fotos_list)
            reconocimiento.save()
            
            return Response({
                'success': True,
                'message': 'Foto subida correctamente',
                'data': {
                    'foto_url': foto_url,
                    'total_fotos': len(fotos_list),
                    'reconocimiento_id': reconocimiento.id
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)