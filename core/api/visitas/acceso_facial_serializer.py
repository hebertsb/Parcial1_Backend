from rest_framework import serializers

class AccesoFacialSerializer(serializers.Serializer):
    imagen_acceso = serializers.ImageField(required=True)
