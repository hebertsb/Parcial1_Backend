# core/management/commands/entrenar_ia_inicial.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.services.ai_training_service import AITrainingService
import logging

logger = logging.getLogger('ai_training')

class Command(BaseCommand):
    help = 'Entrena el modelo de IA inicial usando todos los datos disponibles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza el entrenamiento aunque ya exista un modelo',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada del proceso',
        )

    def handle(self, *args, **options):
        self.stdout.write('🧠 Iniciando entrenamiento de IA...')
        
        try:
            training_service = AITrainingService()
            
            # Verificar si ya existe un modelo
            estadisticas = training_service.obtener_estadisticas_modelo()
            
            if estadisticas.get('model_exists', False) and not options['force']:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️ Ya existe un modelo entrenado. Usa --force para sobreescribir.'
                    )
                )
                return
            
            if options['verbose']:
                self.stdout.write('📊 Cargando datos de entrenamiento...')
            
            # Realizar entrenamiento
            resultado = training_service.entrenar_modelo_automatico()
            
            if resultado['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Entrenamiento completado exitosamente!'
                    )
                )
                self.stdout.write(f"📈 Precisión del modelo: {resultado['accuracy']:.2%}")
                self.stdout.write(f"👥 Personas entrenadas: {resultado['training_stats']['total_persons']}")
                self.stdout.write(f"🖼️ Imágenes procesadas: {resultado['training_stats']['total_images']}")
                
                if options['verbose']:
                    self.stdout.write('📋 Detalles del entrenamiento:')
                    for key, value in resultado['training_stats'].items():
                        self.stdout.write(f"   {key}: {value}")
                
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error en el entrenamiento: {resultado["error"]}'
                    )
                )
                
        except Exception as e:
            logger.error(f"Error en comando de entrenamiento: {e}")
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error interno: {str(e)}'
                )
            )
        
        self.stdout.write('🏁 Comando de entrenamiento finalizado.')