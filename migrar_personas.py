"""
PLAN DE MIGRACIÓN - CONSOLIDACIÓN DE MODELOS
============================================

PROBLEMA IDENTIFICADO:
- Hay duplicación de modelos entre core y authz
- core.models.Persona vs authz.models.Persona 
- core.models.FamiliarResidente vs authz.models.FamiliarPropietario
- Referencias cruzadas que causan conflictos

SOLUCIÓN PROPUESTA:
1. Usar authz.models.Persona como modelo principal (más completo)
2. Migrar datos de core.Persona a authz.Persona
3. Actualizar todas las ForeignKey que apuntan a core.Persona
4. Eliminar core.Persona
5. Consolidar modelos de familiares

MODELOS A MODIFICAR:
- core.models.Propiedad -> usar authz.Persona
- core.models.FamiliarResidente -> migrar a authz.FamiliarPropietario
- Cualquier otro modelo que referencie core.Persona

PASOS A SEGUIR:
1. Crear migración de datos
2. Actualizar ForeignKeys
3. Ejecutar migración
4. Eliminar modelos obsoletos
"""

# Paso 1: Crear script de migración de datos
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction
from authz.models import Persona as PersonaAuthz
from core.models import Persona as PersonaCore, Propiedad

def migrar_personas():
    """Migrar personas de core a authz"""
    print("=== INICIANDO MIGRACIÓN DE PERSONAS ===")
    
    personas_core = PersonaCore.objects.all()
    migraciones_exitosas = 0
    
    for persona_core in personas_core:
        try:
            # Verificar si ya existe en authz
            persona_authz, created = PersonaAuthz.objects.get_or_create(
                documento_identidad=persona_core.documento_identidad,
                defaults={
                    'nombre': persona_core.nombre,
                    'apellido': persona_core.apellido,
                    'telefono': persona_core.telefono or '',
                    'email': persona_core.email,
                    'fecha_nacimiento': persona_core.fecha_nacimiento,
                    'tipo_persona': persona_core.tipo_persona,
                    'activo': persona_core.activo,
                }
            )
            
            if created:
                print(f"✅ Migrada: {persona_core.nombre} {persona_core.apellido}")
                migraciones_exitosas += 1
            else:
                print(f"⚠️ Ya existe: {persona_core.nombre} {persona_core.apellido}")
                
        except Exception as e:
            print(f"❌ Error migrando {persona_core.nombre}: {e}")
    
    print(f"=== MIGRACIÓN COMPLETADA: {migraciones_exitosas} personas migradas ===")

if __name__ == "__main__":
    with transaction.atomic():
        migrar_personas()