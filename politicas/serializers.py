from rest_framework import serializers
from core.models.administracion import ReglamentoCondominio

class ReglamentoCondominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglamentoCondominio
        fields = '__all__'

    def validate_articulo_numero(self, value):
        if value <= 0:
            raise serializers.ValidationError("El número de artículo debe ser mayor a 0.")
        return value
