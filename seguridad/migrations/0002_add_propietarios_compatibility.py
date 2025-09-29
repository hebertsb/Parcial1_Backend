# 🔧 MIGRACIÓN PARA AGREGAR CAMPOS NECESARIOS AL MODELO ReconocimientoFacial

"""
Migración para añadir compatibilidad con el sistema corregido de propietarios
Añade campos: persona_id, fotos_urls para soportar múltiples fotos por usuario
"""

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('seguridad', '0001_initial'),  # Ajustar según la última migración
        ('authz', '0001_initial'),  # Para referencia a authz_persona
    ]

    operations = [
        # Añadir campo persona_id para compatibilidad con sistema authz
        migrations.AddField(
            model_name='reconocimientofacial',
            name='persona_id',
            field=models.IntegerField(blank=True, null=True, help_text='ID de persona en sistema authz'),
        ),
        
        # Añadir campo fotos_urls para almacenar múltiples URLs de Dropbox
        migrations.AddField(
            model_name='reconocimientofacial',
            name='fotos_urls',
            field=models.TextField(blank=True, null=True, help_text='URLs de fotos en Dropbox (JSON)'),
        ),
        
        # Añadir campo fecha_actualizacion para tracking
        migrations.AddField(
            model_name='reconocimientofacial',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True, help_text='Última actualización de fotos'),
        ),
        
        # Añadir índices para optimizar consultas
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_reconocimiento_persona ON reconocimiento_facial(persona_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_reconocimiento_persona;"
        ),
    ]