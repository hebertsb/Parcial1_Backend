# Serializers para CU05 - Gestionar Unidades Habitacionales
from rest_framework import serializers
from django.db import models
from drf_spectacular.utils import extend_schema_field
from core.models.propiedades_residentes import Vivienda, Persona, Propiedad, RelacionesPropietarioInquilino
from decimal import Decimal


class PersonaBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información de personas"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Persona
        fields = [
            'id', 'nombre', 'apellido', 'nombre_completo', 
            'documento_identidad', 'tipo_documento', 'telefono', 
            'email', 'tipo_persona', 'activo'
        ]
        read_only_fields = ['id', 'nombre_completo']
    
    @extend_schema_field(serializers.CharField())
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"


class ViviendaSerializer(serializers.ModelSerializer):
    """Serializer principal para Vivienda - CU05"""
    propiedades = serializers.SerializerMethodField()
    total_propietarios = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_vivienda_display = serializers.CharField(source='get_tipo_vivienda_display', read_only=True)
    tipo_cobranza_display = serializers.CharField(source='get_tipo_cobranza_display', read_only=True)
    
    class Meta:
        model = Vivienda
        fields = [
            'id', 'numero_casa', 'bloque', 'tipo_vivienda', 'tipo_vivienda_display',
            'metros_cuadrados', 'tarifa_base_expensas', 'tipo_cobranza', 'tipo_cobranza_display',
            'estado', 'estado_display', 'fecha_creacion', 'fecha_actualizacion',
            'propiedades', 'total_propietarios'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'propiedades', 'total_propietarios']
    
    @extend_schema_field(serializers.ListField())
    def get_propiedades(self, obj):
        """Obtiene las propiedades activas de la vivienda"""
        propiedades = obj.propiedad_set.filter(activo=True)
        return PropiedadDetailSerializer(propiedades, many=True).data
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_propietarios(self, obj):
        """Cuenta el total de propietarios activos"""
        return obj.propiedad_set.filter(activo=True, tipo_tenencia='propietario').count()
    
    def validate_numero_casa(self, value):
        """Validación personalizada para número de casa"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("El número de casa no puede estar vacío")
        
        # Verificar unicidad solo si es un nuevo registro o se cambió el número
        if self.instance:
            if self.instance.numero_casa != value and Vivienda.objects.filter(numero_casa=value).exists():
                raise serializers.ValidationError("Ya existe una vivienda con este número")
        else:
            if Vivienda.objects.filter(numero_casa=value).exists():
                raise serializers.ValidationError("Ya existe una vivienda con este número")
        
        return value.strip().upper()
    
    def validate_metros_cuadrados(self, value):
        """Validación para metros cuadrados"""
        if value <= 0:
            raise serializers.ValidationError("Los metros cuadrados deben ser mayor a 0")
        if value > 9999.99:
            raise serializers.ValidationError("Los metros cuadrados no pueden exceder 9999.99")
        return value
    
    def validate_tarifa_base_expensas(self, value):
        """Validación para tarifa base"""
        if value < 0:
            raise serializers.ValidationError("La tarifa base no puede ser negativa")
        if value > 99999999.99:
            raise serializers.ValidationError("La tarifa base excede el límite permitido")
        return value


class ViviendaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de viviendas"""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_vivienda_display = serializers.CharField(source='get_tipo_vivienda_display', read_only=True)
    propietarios_count = serializers.SerializerMethodField()
    inquilinos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Vivienda
        fields = [
            'id', 'numero_casa', 'bloque', 'tipo_vivienda', 'tipo_vivienda_display',
            'metros_cuadrados', 'tarifa_base_expensas', 'estado', 'estado_display',
            'propietarios_count', 'inquilinos_count'
        ]
    
    @extend_schema_field(serializers.IntegerField())
    def get_propietarios_count(self, obj):
        return obj.propiedad_set.filter(activo=True, tipo_tenencia='propietario').count()
    
    @extend_schema_field(serializers.IntegerField())
    def get_inquilinos_count(self, obj):
        return obj.propiedad_set.filter(activo=True, tipo_tenencia='inquilino').count()


class PropiedadSerializer(serializers.ModelSerializer):
    """Serializer para gestionar propiedades (asignaciones de personas a viviendas)"""
    persona_nombre = serializers.CharField(source='persona.nombre', read_only=True)
    persona_apellido = serializers.CharField(source='persona.apellido', read_only=True)
    vivienda_numero = serializers.CharField(source='vivienda.numero_casa', read_only=True)
    tipo_tenencia_display = serializers.CharField(source='get_tipo_tenencia_display', read_only=True)
    
    class Meta:
        model = Propiedad
        fields = [
            'id', 'vivienda', 'persona', 'tipo_tenencia', 'tipo_tenencia_display',
            'porcentaje_propiedad', 'fecha_inicio_tenencia', 'fecha_fin_tenencia', 
            'activo', 'persona_nombre', 'persona_apellido', 'vivienda_numero'
        ]
        read_only_fields = ['id']
    
    def validate_porcentaje_propiedad(self, value):
        """Validación del porcentaje de propiedad"""
        if value <= 0 or value > 100:
            raise serializers.ValidationError("El porcentaje debe estar entre 0.01 y 100")
        return value
    
    def validate(self, attrs):
        """Validaciones cruzadas"""
        vivienda = attrs.get('vivienda')
        persona = attrs.get('persona')
        tipo_tenencia = attrs.get('tipo_tenencia')
        porcentaje = attrs.get('porcentaje_propiedad', Decimal('0'))
        
        # Verificar que la persona no esté ya asignada a esta vivienda con el mismo tipo
        if self.instance:
            existing = Propiedad.objects.filter(
                vivienda=vivienda, 
                persona=persona, 
                tipo_tenencia=tipo_tenencia, 
                activo=True
            ).exclude(id=self.instance.id)
        else:
            existing = Propiedad.objects.filter(
                vivienda=vivienda, 
                persona=persona, 
                tipo_tenencia=tipo_tenencia, 
                activo=True
            )
        
        if existing.exists():
            raise serializers.ValidationError(
                f"La persona ya está asignada como {tipo_tenencia} a esta vivienda"
            )
        
        # Para propietarios, verificar que el porcentaje total no exceda 100%
        if tipo_tenencia == 'propietario':
            total_porcentaje = Propiedad.objects.filter(
                vivienda=vivienda, 
                tipo_tenencia='propietario', 
                activo=True
            ).aggregate(total=models.Sum('porcentaje_propiedad'))['total'] or Decimal('0')
            
            if self.instance:
                total_porcentaje -= self.instance.porcentaje_propiedad
            
            if total_porcentaje + porcentaje > 100:
                raise serializers.ValidationError(
                    f"El porcentaje total de propietarios no puede exceder 100%. "
                    f"Actual: {total_porcentaje}%, Intentando agregar: {porcentaje}%"
                )
        
        return attrs


class PropiedadDetailSerializer(PropiedadSerializer):
    """Serializer detallado para propiedades con información completa de persona"""
    persona_info = PersonaBasicSerializer(source='persona', read_only=True)
    
    class Meta(PropiedadSerializer.Meta):
        fields = PropiedadSerializer.Meta.fields + ['persona_info']


class PropiedadCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear propiedades"""
    class Meta:
        model = Propiedad
        fields = [
            'vivienda', 'persona', 'tipo_tenencia', 'porcentaje_propiedad',
            'fecha_inicio_tenencia', 'fecha_fin_tenencia'
        ]
    
    def validate(self, attrs):
        # Reutilizar validaciones del serializer principal
        serializer = PropiedadSerializer()
        return serializer.validate(attrs)


class RelacionPropietarioInquilinoSerializer(serializers.ModelSerializer):
    """Serializer para relaciones propietario-inquilino"""
    propietario_nombre = serializers.CharField(source='propietario.nombre', read_only=True)
    inquilino_nombre = serializers.CharField(source='inquilino.nombre', read_only=True)
    
    class Meta:
        model = RelacionesPropietarioInquilino
        fields = [
            'id', 'propietario', 'inquilino', 'fecha_inicio', 'fecha_fin',
            'contrato_alquiler', 'monto_alquiler', 'activo',
            'propietario_nombre', 'inquilino_nombre'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validaciones para relaciones propietario-inquilino"""
        propietario = attrs.get('propietario')
        inquilino = attrs.get('inquilino')
        
        if propietario == inquilino:
            raise serializers.ValidationError("El propietario y el inquilino no pueden ser la misma persona")
        
        # Verificar que el propietario sea realmente propietario
        if not Propiedad.objects.filter(
            persona=propietario, 
            tipo_tenencia='propietario', 
            activo=True
        ).exists():
            raise serializers.ValidationError("La persona seleccionada no es propietaria de ninguna vivienda")
        
        return attrs