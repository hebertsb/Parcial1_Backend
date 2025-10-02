from rest_framework import serializers
from .models import FamiliarPropietario, Persona

class ListarFamiliaresSerializer(serializers.ModelSerializer):
    persona_info = serializers.SerializerMethodField()

    class Meta:
        model = FamiliarPropietario
        fields = [
            'id', 'parentesco', 'parentesco_descripcion', 'autorizado_acceso', 'puede_autorizar_visitas', 'observaciones',
            'activo', 'created_at', 'persona_info'
        ]

    def get_persona_info(self, obj):
        return PersonaFamiliarSerializer(obj.persona).data
from rest_framework import serializers
from .models import FamiliarPropietario, Persona
from core.utils.dropbox_upload import upload_image_to_dropbox

class PersonaFamiliarSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.SerializerMethodField()
    class Meta:
        model = Persona
        fields = [
            "id", "nombre", "apellido", "documento_identidad", "telefono", 
            "email", "fecha_nacimiento", "genero", "pais", "tipo_persona",
            "direccion", "foto_perfil", "activo", "created_at", "updated_at"
        ]
    def get_foto_perfil(self, obj):
        return obj.foto_perfil if obj.foto_perfil else None

class FamiliarPropietarioRegistroSerializer(serializers.ModelSerializer):
    # Campos de persona
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    documento_identidad = serializers.CharField()
    telefono = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    genero = serializers.CharField(required=False, allow_blank=True)
    pais = serializers.CharField(required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    foto_perfil = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = FamiliarPropietario
        fields = [
            "propietario", "parentesco", "parentesco_descripcion", "autorizado_acceso", "puede_autorizar_visitas", "observaciones",
            # Persona
            "nombre", "apellido", "documento_identidad", "telefono", "email", "fecha_nacimiento", "genero", "pais", "direccion", "foto_perfil"
        ]

    def create(self, validated_data):
        # Extraer datos de persona
        foto_perfil_file = validated_data.pop('foto_perfil')
        persona_data = {
            'nombre': validated_data.pop('nombre'),
            'apellido': validated_data.pop('apellido'),
            'documento_identidad': validated_data.pop('documento_identidad'),
            'telefono': validated_data.pop('telefono', ''),
            'email': validated_data.get('email'),
            'fecha_nacimiento': validated_data.pop('fecha_nacimiento', None),
            'genero': validated_data.pop('genero', ''),
            'pais': validated_data.pop('pais', ''),
            'tipo_persona': 'familiar',
            'direccion': validated_data.pop('direccion', ''),
        }
        # Subir imagen a Dropbox y guardar URL
        filename = f"{persona_data['documento_identidad']}_perfil.jpg"
        folder = f"/Aplicaciones/ParcialSI2/Familiares/{persona_data['documento_identidad']}"
        dropbox_result = upload_image_to_dropbox(foto_perfil_file, filename, folder=folder)
        persona_data['foto_perfil'] = dropbox_result['url']
        # Crear persona
        persona = Persona.objects.create(**persona_data)
        # Crear familiar
        familiar = FamiliarPropietario.objects.create(persona=persona, **validated_data)
        return familiar

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['persona'] = PersonaFamiliarSerializer(instance.persona).data
        return data
