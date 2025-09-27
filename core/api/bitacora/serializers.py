from rest_framework import serializers
from core.models.administracion import BitacoraAcciones, LogSistema

class BitacoraAccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraAcciones
        fields = '__all__'

class LogSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSistema
        fields = '__all__'
