from rest_framework import serializers
from core.models.propiedades_residentes import Visita
from core.utils.dropbox_upload import upload_image_to_dropbox

class VisitaSerializer(serializers.ModelSerializer):

    fotos_reconocimiento_base64 = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Lista de imágenes en base64 para reconocimiento facial (mínimo 1, recomendado 3-5)"
    )
    fotos_reconocimiento_files = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Lista de archivos de imagen para reconocimiento facial (alternativa a base64)"
    )
    foto_ingreso = serializers.ImageField(write_only=True, required=True)
    foto_ingreso_url = serializers.CharField(read_only=True)
    persona_autorizante = serializers.PrimaryKeyRelatedField(read_only=True)
    fotos_reconocimiento = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )

    class Meta:
        model = Visita
        fields = [
            'id', 'persona_autorizante', 'nombre_visitante', 'documento_visitante',
            'telefono_visitante', 'motivo_visita', 'fecha_hora_programada',
            'foto_ingreso', 'foto_ingreso_url', 'estado',
            'fotos_reconocimiento_base64',
            'fotos_reconocimiento_files',
            'fotos_reconocimiento',
            # ...otros campos que necesites...
        ]

    def create(self, validated_data):
        print("[DEBUG][VisitaSerializer.create] validated_data inicial:", validated_data)
        # Procesar foto de ingreso
        foto = validated_data.pop('foto_ingreso')
        print(f"[DEBUG][VisitaSerializer.create] Procesando foto_ingreso: {foto}")
        nombre_archivo = f"visita_{validated_data.get('nombre_visitante','')}_{foto.name}"
        url_dict = upload_image_to_dropbox(foto, nombre_archivo)
        print(f"[DEBUG][VisitaSerializer.create] Foto ingreso subida a Dropbox: {url_dict}")
        validated_data['foto_ingreso_url'] = url_dict["url"]

        # Procesar fotos de reconocimiento facial (base64 y/o archivos)
        fotos_base64 = validated_data.pop('fotos_reconocimiento_base64', [])
        fotos_files = validated_data.pop('fotos_reconocimiento_files', [])
        print(f"[DEBUG][VisitaSerializer.create] fotos_reconocimiento_base64 recibidas: {len(fotos_base64)}")
        print(f"[DEBUG][VisitaSerializer.create] fotos_reconocimiento_files recibidas: {len(fotos_files)}")
        fotos_info = []
        # Procesar imágenes en base64
        for idx, foto_b64 in enumerate(fotos_base64):
            import base64
            from django.core.files.base import ContentFile
            from uuid import uuid4
            img_data = base64.b64decode(foto_b64)
            file_name = f"visita_reconocimiento_{validated_data.get('nombre_visitante','')}_{uuid4().hex[:8]}_{idx}.jpg"
            file = ContentFile(img_data, name=file_name)
            print(f"[DEBUG][VisitaSerializer.create] Subiendo foto_reconocimiento_base64 {idx+1}: {file_name}")
            info_foto = upload_image_to_dropbox(file, file_name)
            print(f"[DEBUG][VisitaSerializer.create] Foto_reconocimiento subida: {info_foto}")
            fotos_info.append(info_foto)
        # Procesar imágenes como archivos
        for idx, file in enumerate(fotos_files):
            from uuid import uuid4
            file_name = f"visita_reconocimiento_{validated_data.get('nombre_visitante','')}_{uuid4().hex[:8]}_{idx}.jpg"
            print(f"[DEBUG][VisitaSerializer.create] Subiendo foto_reconocimiento_file {idx+1}: {file_name}")
            info_foto = upload_image_to_dropbox(file, file_name)
            print(f"[DEBUG][VisitaSerializer.create] Foto_reconocimiento subida: {info_foto}")
            fotos_info.append(info_foto)
        validated_data['fotos_reconocimiento'] = fotos_info
        print(f"[DEBUG][VisitaSerializer.create] validated_data final antes de crear: {validated_data}")
        return super().create(validated_data)
