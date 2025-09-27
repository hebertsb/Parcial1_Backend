# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Usuario, Rol, Persona
from datetime import date


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ["id", "nombre", "descripcion", "activo", "created_at", "updated_at"]


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer para manejar datos de persona"""
    edad = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Persona
        fields = [
            "id", "nombre", "apellido", "documento_identidad", "telefono", 
            "email", "fecha_nacimiento", "genero", "pais", "tipo_persona",
            "direccion", "edad", "nombre_completo", "activo", "created_at", "updated_at"
        ]
        
    def get_edad(self, obj):
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return None
    
    def get_nombre_completo(self, obj):
        return obj.nombre_completo


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para mostrar datos completos del usuario incluyendo persona"""
    persona = PersonaSerializer(read_only=True)
    roles = RolSerializer(many=True, read_only=True)
    
    # Propiedades de la persona para compatibilidad
    nombres = serializers.CharField(read_only=True)
    apellidos = serializers.CharField(read_only=True)
    telefono = serializers.CharField(read_only=True)
    fecha_nacimiento = serializers.DateField(read_only=True)
    genero = serializers.CharField(read_only=True)
    documento_identidad = serializers.CharField(read_only=True)
    pais = serializers.CharField(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            "id", "email", "estado", "is_staff", "is_superuser", 
            "last_login", "date_joined", "persona", "roles",
            # Campos de compatibilidad
            "nombres", "apellidos", "telefono", "fecha_nacimiento", 
            "genero", "documento_identidad", "pais"
        ]


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer completo para actualizar usuarios, roles y datos personales"""
    # Campo para roles (gestión de administradores)
    roles = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Rol.objects.all(),
        required=False
    )
    
    # Campos de persona opcionales para actualización
    nombres = serializers.CharField(required=False)
    apellidos = serializers.CharField(required=False)
    telefono = serializers.CharField(required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    genero = serializers.CharField(required=False, allow_blank=True)
    pais = serializers.CharField(required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Usuario  
        fields = [
            "id", "email", "estado", "roles",
            # Campos de persona para compatibilidad
            "nombres", "apellidos", "telefono", "fecha_nacimiento", 
            "genero", "pais", "direccion"
        ]
    
    def update(self, instance, validated_data):
        """Método completo para manejar roles Y datos personales"""
        import os
        log_path = os.path.join(os.path.dirname(__file__), '..', 'debug_update_completo.log')
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n🔄 UPDATE COMPLETO llamado!\n")
            f.write(f"   Instance: {instance.email}\n")
            f.write(f"   Validated data: {validated_data}\n")
        
        print(f"🔄 UPDATE COMPLETO llamado para {instance.email}")
        print(f"   Validated data: {validated_data}")
        
        # 1. MANEJAR ROLES (para admin panel)
        roles = validated_data.pop('roles', None)
        if roles is not None:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"   🔧 Asignando roles: {[r.id for r in roles]}\n")
            print(f"   🔧 Asignando roles: {[r.id for r in roles]}")
            instance.roles.set(roles)
        
        # 2. MANEJAR DATOS DE PERSONA (para editar-datos)
        persona_data = {}
        persona_fields = ['nombres', 'apellidos', 'telefono', 'fecha_nacimiento', 
                         'genero', 'pais', 'direccion']
        
        for field in persona_fields:
            if field in validated_data:
                if field == 'nombres':
                    persona_data['nombre'] = validated_data.pop(field)
                elif field == 'apellidos':
                    persona_data['apellido'] = validated_data.pop(field)
                else:
                    persona_data[field] = validated_data.pop(field)
        
        # Actualizar persona si hay datos
        if persona_data and instance.persona:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"   👤 Actualizando persona: {persona_data}\n")
            print(f"   👤 Actualizando persona: {persona_data}")
            
            for key, value in persona_data.items():
                setattr(instance.persona, key, value)
            instance.persona.save()
        
        # 3. ACTUALIZAR CAMPOS BÁSICOS DEL USUARIO
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 4. RECARGAR Y VERIFICAR
        instance.refresh_from_db()
        roles_finales = [r.nombre for r in instance.roles.all()]
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"   ✅ Roles finales: {roles_finales}\n")
            f.write(f"   ✅ Usuario actualizado completamente\n")
            f.write("-" * 50 + "\n")
        
        print(f"   ✅ Roles finales: {roles_finales}")
        print(f"   ✅ Usuario actualizado completamente")
        
        return instance


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios con sus datos personales"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    # Campos de persona
    nombres = serializers.CharField(write_only=True)
    apellidos = serializers.CharField(write_only=True)
    documento_identidad = serializers.CharField(write_only=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    genero = serializers.CharField(required=False, allow_blank=True)
    pais = serializers.CharField(required=False, allow_blank=True)
    tipo_persona = serializers.CharField(required=False, default='cliente')
    direccion = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Usuario
        fields = [
            "email", "password", "password_confirm",
            # Campos de persona
            "nombres", "apellidos", "documento_identidad", "telefono", 
            "fecha_nacimiento", "genero", "pais", "tipo_persona", "direccion"
        ]
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        # Validar que el documento no esté en uso
        documento = attrs.get('documento_identidad')
        if documento and Persona.objects.filter(documento_identidad=documento).exists():
            raise serializers.ValidationError("Ya existe una persona con este documento de identidad.")
        
        return attrs
    
    def create(self, validated_data):
        # Extraer datos de contraseña
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Extraer datos de persona
        persona_data = {
            'nombre': validated_data.pop('nombres'),
            'apellido': validated_data.pop('apellidos'), 
            'documento_identidad': validated_data.pop('documento_identidad'),
            'telefono': validated_data.pop('telefono', ''),
            'email': validated_data.get('email'),  # El email se mantiene en ambos
            'fecha_nacimiento': validated_data.pop('fecha_nacimiento', None),
            'genero': validated_data.pop('genero', ''),
            'pais': validated_data.pop('pais', ''),
            'tipo_persona': validated_data.pop('tipo_persona', 'cliente'),
            'direccion': validated_data.pop('direccion', ''),
        }
        
        # Crear persona
        persona = Persona.objects.create(**persona_data)
        
        # Crear usuario
        usuario = Usuario.objects.create(
            persona=persona,
            **validated_data
        )
        usuario.set_password(password)
        usuario.save()
        
        # Asignar rol por defecto
        from .models import Rol
        rol_cliente, _ = Rol.objects.get_or_create(
            nombre="Inquilino",  # Cambiado de CLIENTE a Inquilino para consistencia
            defaults={'descripcion': 'Rol de inquilino del sistema', 'activo': True}
        )
        usuario.roles.add(rol_cliente)
        
        return usuario


# La clase UsuarioUpdateSerializer ya está definida arriba con soporte para roles


class UsuarioRegistroSerializer(UsuarioCreateSerializer):
    """Serializer específico para registro público de usuarios"""
    pass


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para el login de usuarios"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                user = Usuario.objects.get(email=email, estado='ACTIVO')
                if not user.check_password(password):
                    raise serializers.ValidationError('Credenciales inválidas.')
            except Usuario.DoesNotExist:
                raise serializers.ValidationError('Credenciales inválidas.')
        else:
            raise serializers.ValidationError('Email y contraseña son requeridos.')
        
        attrs['user'] = user
        return attrs