#!/usr/bin/env python3
# servidor_simple.py - Servidor Socket.IO básico para pruebas
"""
NOTA: Este archivo requiere Starlette y python-socketio para funcionar.
Para instalar las dependencias necesarias:
    pip install starlette uvicorn python-socketio

Este servidor es opcional y solo se usa si necesitas WebSocket independiente.
Tu sistema principal Django funciona perfectamente sin este archivo.
"""

import logging
import sys
from typing import Any, Dict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    """Función principal que ejecuta el servidor Starlette si está disponible"""
    try:
        # Importaciones condicionales
        import socketio  # type: ignore
        import uvicorn  # type: ignore
        from starlette.applications import Starlette  # type: ignore
        from starlette.staticfiles import StaticFiles  # type: ignore
        
        logger.info("✅ Starlette disponible, iniciando servidor...")

        # Crear servidor Socket.IO
        sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )

        # Crear aplicación Starlette
        app = Starlette()

        # Montar Socket.IO
        socket_app = socketio.ASGIApp(sio, app)

        @sio.event
        async def connect(sid: str, environ: Dict[str, Any]) -> None:
            logger.info(f"🔗 Cliente conectado: {sid}")
            await sio.emit('message', {'data': '¡Conectado exitosamente!'}, room=sid)

        @sio.event  
        async def disconnect(sid: str) -> None:
            logger.info(f"🔌 Cliente desconectado: {sid}")

        @sio.event
        async def test_message(sid: str, data: Any) -> None:
            logger.info(f"📨 Mensaje recibido de {sid}: {data}")
            await sio.emit('response', {
                'status': 'ok',
                'received': data,
                'server': 'Starlette-SocketIO',
                'timestamp': __import__('time').time()
            }, room=sid)

        @sio.event
        async def face_frame(sid: str, data: Any) -> None:
            """Maneja frames para reconocimiento facial"""
            logger.info(f"📷 Frame recibido de {sid} para reconocimiento")
            # Aquí iría la lógica de reconocimiento facial
            await sio.emit('face_recognition_result', {
                'status': 'success',
                'message': 'Frame procesado correctamente',
                'recognized': False,  # Placeholder
                'confidence': 0.0,    # Placeholder
                'timestamp': __import__('time').time()
            }, room=sid)

        # Ejecutar servidor
        logger.info("🚀 Iniciando servidor Starlette-SocketIO en puerto 8002...")
        uvicorn.run(
            socket_app,
            host="0.0.0.0",
            port=8002,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error("❌ Starlette o dependencias no están instaladas.")
        logger.error("   Para usar este servidor ejecuta:")
        logger.error("   pip install starlette uvicorn python-socketio")
        logger.error(f"   Error específico: {e}")
        print("\n💡 ALTERNATIVAS:")
        print("   1. Tu sistema Django principal funciona sin Starlette")
        print("   2. Para WebSocket usa Django Channels")
        print("   3. Para instalar: pip install starlette uvicorn python-socketio")
        return
    except Exception as e:
        logger.error(f"❌ Error ejecutando servidor Starlette: {e}")
        return

if __name__ == "__main__":
    main()