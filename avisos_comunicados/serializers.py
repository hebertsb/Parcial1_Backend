
from rest_framework import serializers

from core.models.propiedades_residentes import AvisosPersonalizados, ComunicadosAdministracion
from authz.models import Persona

class AvisosPersonalizadosSerializer(serializers.ModelSerializer):
    persona_destinatario = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())  # Relacionando con la Persona de authz

    class Meta:
        model = AvisosPersonalizados
        fields = [
            'id', 'persona_destinatario', 'titulo', 'mensaje', 'tipo_aviso', 
            'fecha_creacion', 'fecha_programada_envio', 'fecha_envio', 
            'canales_envio', 'estado_envio', 'fecha_lectura', 
            'accion_requerida', 'url_accion', 'generado_automaticamente'
        ]

class ComunicadosAdministracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComunicadosAdministracion
        fields = [
            'id', 'titulo', 'contenido', 'tipo_comunicado', 'dirigido_a', 
            'fecha_publicacion', 'fecha_expiracion', 'canal_publicacion', 
            'publicado_por', 'adjuntos', 'requiere_confirmacion_lectura', 
            'leido_por', 'prioridad', 'activo'
        ]

