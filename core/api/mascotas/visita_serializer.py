from rest_framework import serializers
from core.models.propiedades_residentes import Visita
from core.utils.dropbox_upload import upload_image_to_dropbox

class VisitaSerializer(serializers.ModelSerializer):
    foto_ingreso = serializers.ImageField(write_only=True, required=True)
    foto_ingreso_url = serializers.CharField(read_only=True)

    class Meta:
        model = Visita
        fields = [
            'id', 'persona_autorizante', 'nombre_visitante', 'documento_visitante',
            'telefono_visitante', 'motivo_visita', 'fecha_hora_programada',
            'foto_ingreso', 'foto_ingreso_url', 'estado',
            # ...otros campos que necesites...
        ]

    def create(self, validated_data):
        foto = validated_data.pop('foto_ingreso')
        nombre_archivo = f"visita_{validated_data.get('nombre_visitante','')}_{foto.name}"
        url = upload_image_to_dropbox(foto, nombre_archivo)
        validated_data['foto_ingreso_url'] = url
        return super().create(validated_data)
