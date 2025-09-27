from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from .models import Usuario
from .serializers import UsuarioSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import hashlib
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers as drf_serializers

def verify_password(plain, stored_hash):
    # Primero intenta usar el verificador de Django (para contraseñas nuevas)
    try:
        if check_password(plain, stored_hash):
            return True
    except Exception:
        pass
    # Fallback legacy: comparar SHA256
    return hashlib.sha256(plain.encode()).hexdigest() == stored_hash

@api_view(["POST"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Iniciar sesión",
    description="Autenticación por email y password. Devuelve tokens JWT.",
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "email": drf_serializers.EmailField(),
            "password": drf_serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="LoginResponse",
            fields={
                "access": drf_serializers.CharField(),
                "refresh": drf_serializers.CharField(),
                "user": UsuarioSerializer(),
                "roles": drf_serializers.ListField(child=drf_serializers.DictField()),
                "primary_role": drf_serializers.CharField(),
            },
        ),
        401: OpenApiResponse(description="Credenciales inválidas"),
    },
)
def login_view(request):
    print("LOGIN BODY RECIBIDO:", request.data)
    email = request.data.get("email")
    password = request.data.get("password")
    try:
        u = Usuario.objects.get(email=email, estado="ACTIVO")
        roles_list = list(u.roles.values_list('nombre', flat=True))
        print("USUARIO ENCONTRADO:", u.email, "ROLES:", roles_list)
    except Usuario.DoesNotExist:
        print("NO SE ENCONTRÓ USUARIO:", email)
        return Response({"detail":"Credenciales inválidas"}, status=401)
    if not u.check_password(password):
        print("CONTRASEÑA INCORRECTA para:", email)
        return Response({"detail":"Credenciales inválidas"}, status=401)
    
    # CRÍTICO: Validar que el usuario tenga al menos un rol
    if not u.roles.exists():
        print(f"⚠️  WARNING: Usuario {u.email} no tiene roles asignados - asignando rol por defecto")
        from .models import Rol
        if u.is_superuser or u.is_staff:
            default_role, _ = Rol.objects.get_or_create(
                nombre="Administrador",
                defaults={'descripcion': 'Rol de administrador del sistema', 'activo': True}
            )
        else:
            default_role, _ = Rol.objects.get_or_create(
                nombre="Inquilino",
                defaults={'descripcion': 'Rol de inquilino del sistema', 'activo': True}
            )
        u.roles.add(default_role)
        print(f"✅ Rol por defecto '{default_role.nombre}' asignado a {u.email}")
    
    print("LOGIN EXITOSO:", email)
    refresh = RefreshToken.for_user(u)
    user_data = UsuarioSerializer(u).data
    
    # Obtener roles actualizados
    roles_data = [{'id': role.id, 'nombre': role.nombre} for role in u.roles.all()]
    primary_role = roles_data[0]['nombre'] if roles_data else 'Inquilino'
    
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": user_data,
        "roles": roles_data,
        "primary_role": primary_role  # Nuevo campo para ayudar al frontend
    })

@api_view(["POST"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Renovar token de acceso",
    description="Intercambia un refresh token válido por un nuevo access token.",
    request=inline_serializer(
        name="RefreshRequest",
        fields={
            "refresh": drf_serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name="RefreshResponse",
            fields={
                "access": drf_serializers.CharField(),
            },
        ),
        400: OpenApiResponse(description="Falta refresh"),
        401: OpenApiResponse(description="Refresh inválido"),
    },
)
def refresh_view(request):
    token = request.data.get("refresh")
    if not token:
        return Response({"detail":"Falta refresh"}, status=400)
    try:
        r = RefreshToken(token)
        new_access = r.access_token
        return Response({"access": str(new_access) })
    except Exception:
        return Response({"detail":"Refresh inválido"}, status=401)
