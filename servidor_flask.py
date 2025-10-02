#!/usr/bin/env python3
# servidor_flask.py - Servidor Flask-SocketIO estable
"""
NOTA: Este archivo requiere Flask para funcionar.
Para instalar las dependencias necesarias:
    pip install flask flask-socketio

Este servidor es opcional y solo se usa si necesitas WebSocket con Flask.
Tu sistema principal Django funciona perfectamente sin este archivo.
"""

import logging
import sys
from typing import Optional, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    """Función principal que ejecuta el servidor Flask si está disponible"""
    try:
        # Importaciones condicionales dentro de la función
        from flask import Flask, request  # type: ignore
        from flask_socketio import SocketIO, emit  # type: ignore
        
        logger.info("✅ Flask disponible, iniciando servidor...")
        
        # Crear aplicación Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'

        # Crear SocketIO con CORS habilitado
        socketio = SocketIO(
            app, 
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode='threading'
        )

        @app.route('/')
        def index() -> str:
            return '''
            <h1>🚀 Servidor Flask-SocketIO Funcionando</h1>
            <p>Puerto: 8001</p>
            <p>Estado: ✅ Activo</p>
            <p>CORS: ✅ Habilitado</p>
            '''

        @socketio.on('connect')
        def on_connect() -> None:
            client_id = getattr(request, 'sid', 'ID desconocido')
            logger.info(f"🔗 Cliente conectado: {client_id}")
            emit('message', {'data': '¡Conectado exitosamente al servidor Flask-SocketIO!'})
            
        @socketio.on('disconnect')
        def on_disconnect() -> None:
            logger.info("🔌 Cliente desconectado")

        @socketio.on('test_message')
        def on_test_message(data: Any) -> None:
            logger.info(f"📨 Mensaje recibido: {data}")
            emit('response', {
                'status': 'ok', 
                'received': data,
                'server': 'Flask-SocketIO',
                'timestamp': __import__('time').time()
            })

        @socketio.on('face_frame')
        def on_face_frame(data: Any) -> None:
            """Maneja frames para reconocimiento facial"""
            logger.info("📷 Frame recibido para reconocimiento")
            # Aquí iría la lógica de reconocimiento facial
            emit('face_recognition_result', {
                'status': 'success',
                'message': 'Frame procesado correctamente',
                'recognized': False,  # Placeholder
                'confidence': 0.0,    # Placeholder
                'timestamp': __import__('time').time()
            })

        # Ejecutar servidor
        logger.info("🚀 Iniciando servidor Flask-SocketIO en puerto 8001...")
        socketio.run(
            app,
            host='0.0.0.0',
            port=8001,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except ImportError as e:
        logger.error("❌ Flask no está instalado.")
        logger.error("   Para usar este servidor ejecuta: pip install flask flask-socketio")
        logger.error(f"   Error específico: {e}")
        print("\n💡 ALTERNATIVAS:")
        print("   1. Tu sistema Django principal funciona sin Flask")
        print("   2. Para WebSocket usa Django Channels")
        print("   3. Para instalar Flask: pip install flask flask-socketio")
        return
    except Exception as e:
        logger.error(f"❌ Error ejecutando servidor Flask: {e}")
        return

if __name__ == "__main__":
    main()