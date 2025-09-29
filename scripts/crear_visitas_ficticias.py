
from django.utils import timezone
from authz.models import Persona
from core.models.propiedades_residentes import Visita

# Buscar o crear persona autorizante ficticia evitando duplicados
try:
    persona = Persona.objects.get(documento_identidad="99999999")
except Persona.DoesNotExist:
    persona = Persona.objects.create(
        nombre="Guardia Ficticio",
        apellido="Prueba",
        documento_identidad="99999999",
        tipo_persona="seguridad",
        email="guardia.ficticio@prueba.com"
    )

# Crear visitas ficticias para hoy
for i in range(3):
    Visita.objects.create(
        persona_autorizante=persona,
        nombre_visitante=f"Visitante Prueba {i+1}",
        documento_visitante=f"DOC{i+1}2025",
        telefono_visitante=f"7000000{i+1}",
        motivo_visita="Prueba de acceso",
        fecha_hora_programada=timezone.now(),
        estado="programada"
    )

print("Visitas ficticias creadas para pruebas.")
