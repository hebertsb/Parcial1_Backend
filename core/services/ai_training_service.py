# core/services/ai_training_service.py - Entrenamiento automático de IA
import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
import face_recognition
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging
from datetime import datetime

logger = logging.getLogger('ai_training')

class AITrainingService:
    """
    Servicio de entrenamiento automático de IA usando los datos existentes
    """
    
    def __init__(self):
        self.model_path = 'ai_models/'
        self.face_classifier = None
        self.label_encoder = None
        self.last_training = None
        self.training_accuracy = 0.0
        
        # Crear directorio si no existe
        os.makedirs(self.model_path, exist_ok=True)
    
    def entrenar_modelo_automatico(self) -> Dict:
        """
        Entrena el modelo automáticamente usando datos de la BD
        """
        logger.info("🧠 Iniciando entrenamiento automático de IA...")
        
        try:
            # 1. Cargar datos de entrenamiento
            X_train, y_train, personas_map = self._cargar_datos_entrenamiento()
            
            if len(X_train) < 2:
                return {
                    'success': False,
                    'error': 'Necesitas al menos 2 personas con fotos para entrenar'
                }
            
            # 2. Dividir datos para entrenamiento y validación
            X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
            )
            
            # 3. Entrenar clasificador SVM
            logger.info(f"📊 Entrenando con {len(X_train_split)} muestras...")
            
            self.face_classifier = SVC(
                kernel='linear',  # Rápido y eficiente
                probability=True,  # Para obtener confianza
                C=1.0,
                random_state=42
            )
            
            # Entrenar el modelo
            self.face_classifier.fit(X_train_split, y_train_split)
            
            # 4. Validar precisión
            y_pred = self.face_classifier.predict(X_val_split)
            accuracy = accuracy_score(y_val_split, y_pred)
            
            # 5. Guardar modelo entrenado
            self._guardar_modelo(personas_map)
            
            self.training_accuracy = accuracy
            self.last_training = datetime.now()
            
            logger.info(f"✅ Entrenamiento completado - Precisión: {accuracy:.2%}")
            
            return {
                'success': True,
                'accuracy': accuracy,
                'samples_used': len(X_train),
                'people_count': len(personas_map),
                'training_time': datetime.now().isoformat(),
                'model_path': self.model_path,
                'classification_report': classification_report(y_val_split, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _cargar_datos_entrenamiento(self) -> Tuple[List, List, Dict]:
        """
        Carga datos de entrenamiento desde la BD y Dropbox
        """
        from seguridad.models import Copropietarios, ReconocimientoFacial
        import requests
        from PIL import Image
        import io
        
        X_train = []  # Encodings faciales
        y_train = []  # Labels (IDs de personas)
        personas_map = {}  # ID -> Nombre
        
        # Obtener todos los reconocimientos activos
        reconocimientos = ReconocimientoFacial.objects.filter(
            activo=True,
            copropietario__activo=True
        ).select_related('copropietario')
        
        logger.info(f"📋 Procesando {len(reconocimientos)} personas registradas...")
        
        for reconocimiento in reconocimientos:
            persona_id = reconocimiento.copropietario.id
            persona_nombre = reconocimiento.copropietario.nombre_completo
            personas_map[persona_id] = persona_nombre
            
            # Procesar múltiples fotos si existen
            fotos_urls = []
            
            # URL principal
            if reconocimiento.imagen_referencia_url:
                fotos_urls.append(reconocimiento.imagen_referencia_url)
            
            # URLs adicionales del JSON
            try:
                import json
                if reconocimiento.fotos_urls:
                    fotos_adicionales = json.loads(reconocimiento.fotos_urls)
                    fotos_urls.extend(fotos_adicionales)
            except:
                pass
            
            # Procesar cada foto
            encodings_persona = []
            for foto_url in fotos_urls[:5]:  # Máximo 5 fotos por persona
                try:
                    # Descargar imagen
                    response = requests.get(foto_url, timeout=10)
                    if response.status_code == 200:
                        imagen = Image.open(io.BytesIO(response.content))
                        imagen_rgb = np.array(imagen)
                        
                        # Extraer encoding facial
                        encodings = face_recognition.face_encodings(imagen_rgb)
                        if encodings:
                            encodings_persona.append(encodings[0])
                
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando foto de {persona_nombre}: {e}")
            
            # Agregar encodings al conjunto de entrenamiento
            for encoding in encodings_persona:
                X_train.append(encoding)
                y_train.append(persona_id)
            
            logger.info(f"✅ {persona_nombre}: {len(encodings_persona)} fotos procesadas")
        
        return X_train, y_train, personas_map
    
    def _guardar_modelo(self, personas_map: Dict):
        """
        Guarda el modelo entrenado en disco
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar clasificador
        model_file = os.path.join(self.model_path, f'face_classifier_{timestamp}.pkl')
        joblib.dump(self.face_classifier, model_file)
        
        # Guardar mapa de personas
        personas_file = os.path.join(self.model_path, f'personas_map_{timestamp}.pkl')
        with open(personas_file, 'wb') as f:
            pickle.dump(personas_map, f)
        
        # Guardar referencia al modelo actual
        current_model_file = os.path.join(self.model_path, 'current_model.pkl')
        with open(current_model_file, 'wb') as f:
            pickle.dump({
                'classifier_path': model_file,
                'personas_path': personas_file,
                'training_date': datetime.now(),
                'accuracy': self.training_accuracy
            }, f)
        
        logger.info(f"💾 Modelo guardado: {model_file}")
    
    def cargar_modelo_entrenado(self) -> bool:
        """
        Carga el modelo entrenado más reciente
        """
        try:
            current_model_file = os.path.join(self.model_path, 'current_model.pkl')
            
            if not os.path.exists(current_model_file):
                return False
            
            with open(current_model_file, 'rb') as f:
                model_info = pickle.load(f)
            
            # Cargar clasificador
            self.face_classifier = joblib.load(model_info['classifier_path'])
            
            # Cargar mapa de personas
            with open(model_info['personas_path'], 'rb') as f:
                self.personas_map = pickle.load(f)
            
            self.last_training = model_info.get('training_date')
            self.training_accuracy = model_info.get('accuracy', 0.0)
            
            logger.info(f"✅ Modelo cargado - Precisión: {self.training_accuracy:.2%}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            return False
    
    def predecir_con_modelo_entrenado(self, face_encoding: np.ndarray) -> Dict:
        """
        Usa el modelo entrenado para hacer predicciones
        """
        if self.face_classifier is None:
            if not self.cargar_modelo_entrenado():
                return {
                    'success': False,
                    'error': 'No hay modelo entrenado disponible'
                }
        
        try:
            # Verificar que el modelo esté cargado
            if self.face_classifier is None:
                return {
                    'success': False,
                    'error': 'Modelo no disponible'
                }
            
            # Convertir a formato correcto para scikit-learn
            face_encoding_array = np.array([face_encoding])
            
            # Predecir persona
            prediction = self.face_classifier.predict(face_encoding_array)[0]
            
            # Obtener probabilidades
            probabilities = self.face_classifier.predict_proba(face_encoding_array)[0]
            confidence = max(probabilities) * 100
            
            # Obtener nombre de la persona
            persona_nombre = getattr(self, 'personas_map', {}).get(prediction, 'Desconocido')
            
            return {
                'success': True,
                'persona_id': prediction,
                'persona_nombre': persona_nombre,
                'confidence': confidence,
                'recognized': confidence > 70,  # Umbral ajustable
                'model_accuracy': self.training_accuracy,
                'training_date': self.last_training.isoformat() if self.last_training else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def re_entrenar_automatico(self) -> Dict:
        """
        Re-entrena el modelo si hay nuevos datos
        """
        from seguridad.models import ReconocimientoFacial
        
        # Verificar si hay nuevas fotos desde el último entrenamiento
        if self.last_training:
            nuevos_registros = ReconocimientoFacial.objects.filter(
                fecha_modificacion__gt=self.last_training,
                activo=True
            ).count()
            
            if nuevos_registros == 0:
                return {
                    'success': True,
                    'message': 'No hay nuevos datos para re-entrenar',
                    'last_training': self.last_training.isoformat()
                }
        
        # Re-entrenar con todos los datos
        logger.info("🔄 Iniciando re-entrenamiento automático...")
        return self.entrenar_modelo_automatico()
    
    def obtener_estadisticas_modelo(self) -> Dict:
        """
        Obtiene estadísticas del modelo actual
        """
        if not self.cargar_modelo_entrenado():
            return {'error': 'No hay modelo entrenado'}
        
        from seguridad.models import ReconocimientoFacial
        
        total_personas = ReconocimientoFacial.objects.filter(activo=True).count()
        
        return {
            'model_exists': True,
            'accuracy': self.training_accuracy,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'people_in_model': len(self.personas_map) if hasattr(self, 'personas_map') else 0,
            'total_people_in_db': total_personas,
            'model_path': self.model_path,
            'needs_retraining': total_personas > len(self.personas_map) if hasattr(self, 'personas_map') else True
        }