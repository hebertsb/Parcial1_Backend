from rest_framework import serializers
from core.models.propiedades_residentes import Mascota

class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['id', 'nombre', 'tipo_animal', 'raza', 'edad', 'descripcion', 'vacunas_vigentes', 'activo']
        read_only_fields = ['id']

class MascotaDetailSerializer(MascotaSerializer):
    class Meta(MascotaSerializer.Meta):
        fields = MascotaSerializer.Meta.fields + ['fecha_registro']

class MascotaListSerializer(MascotaSerializer):
    class Meta(MascotaSerializer.Meta):
        fields = ['id', 'nombre', 'tipo_animal', 'activo']