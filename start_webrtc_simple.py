#!/usr/bin/env python3
# start_webrtc_simple.py - Inicio directo del servidor WebRTC
import uvicorn
import socketio
from webrtc_enhanced_server import app

if __name__ == "__main__":
    print("🚀 Iniciando WebRTC Server...")
    print("📡 Puerto: 8001")
    print("🔗 URL: http://localhost:8001")
    print("⚡ Socket.IO habilitado")
    print("-" * 40)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True,
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")