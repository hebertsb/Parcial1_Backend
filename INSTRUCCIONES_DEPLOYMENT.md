# INSTRUCCIONES_DEPLOYMENT.md

## 🎯 **ARQUITECTURA CORRECTA DEL SISTEMA**

### 📊 **SEPARACIÓN FRONTEND vs BACKEND**

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                      │
│  📁 Carpeta separada: /mi-frontend-reconocimiento          │
│  🌐 Puerto: 3000                                           │
│  📦 Dependencias: React, Next.js, Socket.IO-client        │
│  📄 Archivos: package.json, tsconfig.json, components/    │
└─────────────────────────────────────────────────────────────┘
                              ↕️ Socket.IO
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Django)                         │
│  📁 Carpeta actual: /Parcial_1                            │
│  🌐 Puerto: 8000 (Django) + 8001 (WebRTC)                │
│  🐍 Dependencias: Django, Socket.IO, OpenCV, Uvicorn      │
│  📄 Archivos: manage.py, models.py, webrtc_server.py      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **PASO 1: INICIAR BACKEND WEBRTC**

### En tu carpeta actual del backend:

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Iniciar servidor WebRTC (puerto 8001)
python start_enhanced_webrtc.py
```

### ✅ **Deberías ver:**
```
🚀 Iniciando Enhanced WebRTC Server para React...
📡 CORS habilitado para: ['http://localhost:3000', ...]
✅ Django configurado correctamente
✅ Proveedor OpenCV disponible
🎯 Todo listo. Iniciando servidor...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

## 🎯 **PASO 2: CREAR FRONTEND SEPARADO**

### Crear nueva carpeta para el frontend:

```bash
# Salir de la carpeta del backend
cd ..

# Crear carpeta del frontend
mkdir frontend-reconocimiento
cd frontend-reconocimiento

# Inicializar proyecto Next.js
npx create-next-app@latest . --typescript --tailwind --eslint --app

# Instalar dependencias adicionales
npm install socket.io-client lucide-react
npm install @radix-ui/react-progress @radix-ui/react-alert-dialog
npm install class-variance-authority clsx tailwind-merge
```

## 📁 **PASO 3: ESTRUCTURA FINAL**

```
📁 UNIVERSIDAD_AUTONOMA_GABRIEL_RENE_MORENO/
├── 📁 Parcial_1/                    ← BACKEND DJANGO
│   ├── 🐍 manage.py
│   ├── 🐍 start_enhanced_webrtc.py
│   ├── 🐍 webrtc_enhanced_server.py
│   ├── 📁 seguridad/
│   ├── 📁 core/
│   └── 🐍 requirements_webrtc.txt
│
└── 📁 frontend-reconocimiento/       ← FRONTEND NEXT.JS
    ├── 📦 package.json
    ├── 📄 tsconfig.json
    ├── 📄 next.config.js
    ├── 📁 components/
    │   └── 📁 ui/
    └── 📁 app/
```

## 🔧 **PASO 4: CONFIGURACIÓN FRONTEND**

### En tu nuevo frontend, crear archivos:

#### `next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/socket.io/:path*',
        destination: 'http://localhost:8001/socket.io/:path*'
      }
    ]
  }
}
module.exports = nextConfig
```

#### `.env.local`:
```
NEXT_PUBLIC_WEBRTC_URL=http://localhost:8001
```

## 🎬 **PASO 5: USO DEL COMPONENTE REACT**

### Mover tu `WebRTCFaceRecognition.tsx` al frontend:
```bash
# En el frontend
mkdir -p components/reconocimiento
# Copiar el archivo TSX aquí
```

### Crear página principal:
```typescript
// app/page.tsx
import WebRTCFaceRecognition from '@/components/reconocimiento/WebRTCFaceRecognition'

export default function Home() {
  return (
    <main className="container mx-auto py-8">
      <WebRTCFaceRecognition />
    </main>
  )
}
```

## 🚦 **FLUJO DE INICIO COMPLETO**

### Terminal 1 - Backend:
```bash
cd Parcial_1
.venv\Scripts\activate
python start_enhanced_webrtc.py
# ✅ WebRTC Server en puerto 8001
```

### Terminal 2 - Frontend:
```bash
cd frontend-reconocimiento
npm run dev
# ✅ Next.js en puerto 3000
```

### Terminal 3 - Django API (opcional):
```bash
cd Parcial_1
python manage.py runserver
# ✅ Django API en puerto 8000
```

## 🎯 **RESULTADO FINAL**

1. **Backend**: Puerto 8001 - WebRTC + Socket.IO
2. **Frontend**: Puerto 3000 - React + Socket.IO-client  
3. **API Django**: Puerto 8000 - REST API (opcional para otros endpoints)

### 🌐 **URLs de acceso:**
- Frontend: http://localhost:3000
- WebRTC Server: http://localhost:8001
- Django Admin: http://localhost:8000/admin

## ❓ **¿QUIERES QUE ELIMINE LOS ARCHIVOS FRONTEND DEL BACKEND?**

Los archivos que creé por error en tu backend son:
- `package.json` ❌ (para frontend)
- `tsconfig.json` ❌ (para frontend) 
- `next.config.js` ❌ (para frontend)
- `components/ui/` ❌ (para frontend)
- `globals.css` ❌ (para frontend)

¿Los elimino del backend? Solo necesitas los archivos Python.