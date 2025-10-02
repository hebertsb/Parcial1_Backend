# probar_entrenamiento_ia.py - Script para probar el sistema de entrenamiento
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.services.ai_training_service import AITrainingService
from seguridad.models import ReconocimientoFacial, Copropietarios
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🧠 Iniciando prueba del sistema de entrenamiento de IA...")
    
    try:
        # Verificar datos disponibles
        print("\n📊 Verificando datos disponibles:")
        total_copropietarios = Copropietarios.objects.filter(activo=True).count()
        total_reconocimientos = ReconocimientoFacial.objects.filter(activo=True).count()
        
        print(f"   • Copropietarios activos: {total_copropietarios}")
        print(f"   • Reconocimientos faciales: {total_reconocimientos}")
        
        if total_reconocimientos == 0:
            print("❌ No hay datos de reconocimiento facial disponibles.")
            print("   Ejecuta primero el script de crear datos de prueba.")
            return
        
        # Inicializar servicio de entrenamiento
        print("\n🤖 Inicializando servicio de entrenamiento...")
        training_service = AITrainingService()
        
        # Obtener estadísticas actuales
        print("\n📈 Estadísticas del modelo actual:")
        estadisticas = training_service.obtener_estadisticas_modelo()
        
        for key, value in estadisticas.items():
            print(f"   • {key}: {value}")
        
        # Realizar entrenamiento si no existe modelo
        if not estadisticas.get('model_exists', False):
            print("\n🏋️ Entrenando modelo inicial...")
            resultado = training_service.entrenar_modelo_automatico()
            
            if resultado['success']:
                print(f"✅ Entrenamiento exitoso!")
                print(f"   • Precisión: {resultado['accuracy']:.2%}")
                
                # Mostrar estadísticas si están disponibles
                if 'training_stats' in resultado:
                    stats = resultado['training_stats']
                    print(f"   • Personas: {stats.get('total_persons', 'N/A')}")
                    print(f"   • Imágenes: {stats.get('total_images', 'N/A')}")
                
                # Mostrar detalles adicionales
                for key, value in resultado.items():
                    if key not in ['success', 'accuracy', 'training_stats']:
                        print(f"   • {key}: {value}")
            else:
                print(f"❌ Error en entrenamiento: {resultado['error']}")
                return
        else:
            print("ℹ️ Ya existe un modelo entrenado.")
            
            # Probar re-entrenamiento
            print("\n🔄 Probando re-entrenamiento...")
            resultado_retrain = training_service.re_entrenar_automatico()
            if resultado_retrain.get('success'):
                mensaje = resultado_retrain.get('message', 'Re-entrenamiento completado')
                print(f"   • Re-entrenamiento: ✅ {mensaje}")
            else:
                print(f"   • Re-entrenamiento: ❌ {resultado_retrain.get('error', 'Error desconocido')}")
            
        # Mostrar estadísticas finales
        print("\n📊 Estadísticas finales:")
        estadisticas_finales = training_service.obtener_estadisticas_modelo()
        
        for key, value in estadisticas_finales.items():
            print(f"   • {key}: {value}")
        
        print("\n🎉 Prueba completada exitosamente!")
        
        # Ejemplos de endpoints que estarían disponibles
        print("\n🌐 Endpoints disponibles:")
        print("   • POST /api/seguridad/ia/entrenar/ - Entrenar modelo")
        print("   • POST /api/seguridad/ia/re-entrenar/ - Re-entrenar modelo")
        print("   • GET  /api/seguridad/ia/estadisticas/ - Ver estadísticas")
        print("   • POST /api/seguridad/ia/probar/ - Probar con imagen")
        print("   • GET  /api/seguridad/ia/dashboard/ - Dashboard completo")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()