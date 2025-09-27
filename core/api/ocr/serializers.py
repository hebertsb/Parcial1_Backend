from rest_framework import serializers

from authz.models import Persona
from core.models.propiedades_residentes import Vehiculo, Visita


class PlateImageUploadSerializer(serializers.Serializer):
    """Payload esperado para ejecutar el OCR de placas."""

    image = serializers.ImageField()


class PersonaOCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = [
            "id",
            "nombre",
            "apellido",
            "documento_identidad",
            "telefono",
            "email",
        ]


class VehiculoOCRSerializer(serializers.ModelSerializer):
    propietario = PersonaOCRSerializer(read_only=True)

    class Meta:
        model = Vehiculo
        fields = [
            "id",
            "placa",
            "marca",
            "modelo",
            "color",
            "tipo_vehiculo",
            "tag_numero",
            "tag_activo",
            "propietario",
        ]


class VisitaOCRSerializer(serializers.ModelSerializer):
    persona_autorizante = PersonaOCRSerializer(read_only=True)

    class Meta:
        model = Visita
        fields = [
            "id",
            "nombre_visitante",
            "motivo_visita",
            "estado",
            "vehiculo_placa",
            "fecha_hora_programada",
            "fecha_hora_llegada",
            "fecha_hora_salida",
            "persona_autorizante",
        ]