// components/reconocimiento/WebRTCFaceRecognition.tsx
"use client"

import React, { useRef, useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Camera, 
  Users, 
  AlertCircle, 
  CheckCircle, 
  X, 
  Activity,
  Zap,
  Eye,
  Settings,
  BarChart
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { io, Socket } from 'socket.io-client';

interface PersonaReconocida {
  id: number;
  nombre: string;
  vivienda?: string;
  tipo_residente?: string;
  documento?: string;
}

interface ReconocimientoResponse {
  reconocido: boolean;
  persona?: PersonaReconocida;
  confianza?: number;
  proveedor?: string;
  processing_time?: number;
  frame_id?: number;
  timestamp?: number;
  threshold_usado?: number;
  mensaje?: string;
  error?: string;
}

interface ServerStats {
  connected_clients: number;
  total_frames_processed: number;
  successful_recognitions: number;
  failed_recognitions: number;
  average_processing_time: number;
}

interface ServerConfig {
  provider: string;
  max_fps: number;
  supported_formats: string[];
  max_resolution: { width: number; height: number };
}

export default function WebRTCFaceRecognition() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<Socket | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [camaraActiva, setCamaraActiva] = useState(false);
  const [conectado, setConectado] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [ultimoResultado, setUltimoResultado] = useState<ReconocimientoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fps, setFps] = useState(5); // FPS configurables
  const [calidad, setCalidad] = useState(0.7); // Calidad JPEG
  const [stats, setStats] = useState<ServerStats>({
    connected_clients: 0,
    total_frames_processed: 0,
    successful_recognitions: 0,
    failed_recognitions: 0,
    average_processing_time: 0
  });
  const [config, setConfig] = useState<ServerConfig | null>(null);
  const [frameId, setFrameId] = useState(0);

  // Obtener URL del servidor WebRTC
  const getWebRTCUrl = () => {
    return process.env.NEXT_PUBLIC_WEBRTC_URL || 'http://localhost:8001';
  };

  // Conectar a servidor WebRTC
  const conectarWebRTC = useCallback(async () => {
    try {
      setError(null);
      
      const socket = io(getWebRTCUrl(), {
        transports: ['websocket', 'polling'],
        upgrade: true,
        timeout: 10000,
        forceNew: true
      });

      // Event handlers del socket
      socket.on('connect', () => {
        console.log('✅ Conectado al servidor WebRTC');
        setConectado(true);
        setProcesando(false);
      });

      socket.on('disconnect', () => {
        console.log('❌ Desconectado del servidor WebRTC');
        setConectado(false);
        setProcesando(false);
      });

      socket.on('config', (serverConfig: ServerConfig) => {
        console.log('📋 Configuración recibida:', serverConfig);
        setConfig(serverConfig);
        // Ajustar FPS según configuración del servidor
        if (serverConfig.max_fps < fps) {
          setFps(serverConfig.max_fps);
        }
      });

      socket.on('recognition_result', (resultado: ReconocimientoResponse) => {
        console.log('🎯 Resultado de reconocimiento:', resultado);
        setUltimoResultado(resultado);
        setProcesando(false);
      });

      socket.on('stats', (serverStats: ServerStats) => {
        setStats(serverStats);
      });

      socket.on('error', (errorData: { message: string; code: string }) => {
        console.error('❌ Error del servidor:', errorData);
        setError(`Error del servidor: ${errorData.message}`);
        setProcesando(false);
      });

      socket.on('connect_error', (err) => {
        console.error('❌ Error de conexión:', err);
        setError(`Error de conexión: ${err.message || 'No se pudo conectar al servidor'}`);
        setConectado(false);
      });

      socketRef.current = socket;

    } catch (error: any) {
      console.error('Error conectando WebRTC:', error);
      setError(`Error conectando: ${error.message}`);
    }
  }, [fps]);

  // Desconectar WebRTC
  const desconectarWebRTC = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    setConectado(false);
    detenerStreaming();
  }, []);

  // Iniciar cámara
  const iniciarCamara = useCallback(async () => {
    try {
      setError(null);
      
      const constraints = {
        video: {
          width: { ideal: config?.max_resolution.width || 640 },
          height: { ideal: config?.max_resolution.height || 480 },
          facingMode: 'user',
          frameRate: { ideal: fps, max: fps * 2 }
        }
      };

      const newStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(newStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = newStream;
        
        videoRef.current.addEventListener('loadedmetadata', () => {
          console.log(`📹 Video iniciado: ${videoRef.current?.videoWidth}x${videoRef.current?.videoHeight}`);
        });
      }
      
      setCamaraActiva(true);

    } catch (error: any) {
      console.error('Error iniciando cámara:', error);
      setError('Error al acceder a la cámara. Verifica los permisos.');
    }
  }, [config, fps]);

  // Detener cámara
  const detenerCamara = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setCamaraActiva(false);
    detenerStreaming();
  }, [stream]);

  // Iniciar streaming de reconocimiento
  const iniciarStreaming = useCallback(() => {
    if (!camaraActiva || !conectado || !videoRef.current || !canvasRef.current) {
      setError('Cámara no activa o no conectado al servidor');
      return;
    }

    setProcesando(true);
    setError(null);

    const interval = setInterval(() => {
      procesarFrame();
    }, 1000 / fps); // Intervalo basado en FPS

    intervalRef.current = interval;
    console.log(`🎬 Streaming iniciado a ${fps} FPS`);

  }, [camaraActiva, conectado, fps]);

  // Detener streaming
  const detenerStreaming = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setProcesando(false);
    console.log('⏹️ Streaming detenido');
  }, []);

  // Procesar frame individual
  const procesarFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !socketRef.current) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx || video.readyState !== 4) {
      return;
    }

    try {
      // Configurar canvas
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Dibujar frame
      ctx.drawImage(video, 0, 0);
      
      // Convertir a base64
      const imageData = canvas.toDataURL('image/jpeg', calidad);
      
      // Enviar al servidor
      const currentFrameId = frameId + 1;
      setFrameId(currentFrameId);

      socketRef.current.emit('process_frame', {
        image: imageData,
        frame_id: currentFrameId,
        quality: calidad,
        timestamp: Date.now()
      });

    } catch (error) {
      console.error('Error procesando frame:', error);
    }
  }, [frameId, calidad]);

  // Obtener estadísticas
  const obtenerStats = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.emit('get_stats');
    }
  }, []);

  // Resetear estadísticas
  const resetearStats = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.emit('reset_stats');
    }
  }, []);

  // Calcular tasa de éxito
  const tasaExito = stats.total_frames_processed > 0 ? 
    (stats.successful_recognitions / stats.total_frames_processed * 100) : 0;

  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      detenerStreaming();
      desconectarWebRTC();
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream, detenerStreaming, desconectarWebRTC]);

  return (
    <div className="space-y-6">
      {/* Header Profesional */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Zap className="h-7 w-7 text-blue-600" />
            🚀 WebRTC Reconocimiento Facial Profesional
          </CardTitle>
          <CardDescription className="text-lg">
            Sistema de reconocimiento facial en tiempo real con Socket.IO + WebRTC
            <br />
            <span className="text-sm font-mono bg-blue-100 px-2 py-1 rounded">
              {config?.provider || 'Cargando configuración...'}
            </span>
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Panel de Control */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Centro de Control
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Controles de Conexión */}
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Conexión WebRTC
              </h4>
              <div className="flex gap-2">
                <Button
                  onClick={conectarWebRTC}
                  disabled={conectado}
                  size="sm"
                  className="flex-1"
                >
                  {conectado ? '🟢 Conectado' : '🔴 Conectar'}
                </Button>
                <Button
                  onClick={desconectarWebRTC}
                  disabled={!conectado}
                  variant="outline"
                  size="sm"
                >
                  Desconectar
                </Button>
              </div>
            </div>

            {/* Controles de Cámara */}
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center gap-2">
                <Camera className="h-4 w-4" />
                Cámara
              </h4>
              <div className="flex gap-2">
                <Button
                  onClick={iniciarCamara}
                  disabled={camaraActiva || !conectado}
                  size="sm"
                  className="flex-1"
                >
                  {camaraActiva ? '📹 Activa' : 'Iniciar'}
                </Button>
                <Button
                  onClick={detenerCamara}
                  disabled={!camaraActiva}
                  variant="outline"
                  size="sm"
                >
                  Detener
                </Button>
              </div>
            </div>

            {/* Controles de Streaming */}
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Reconocimiento
              </h4>
              <div className="flex gap-2">
                <Button
                  onClick={procesando ? detenerStreaming : iniciarStreaming}
                  disabled={!camaraActiva || !conectado}
                  variant={procesando ? "destructive" : "default"}
                  size="sm"
                  className="flex-1"
                >
                  {procesando ? '⏹️ Detener' : '▶️ Iniciar'}
                </Button>
              </div>
            </div>
          </div>

          {/* Configuración Avanzada */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                FPS: {fps}
              </label>
              <input
                type="range"
                min="1"
                max={config?.max_fps || 10}
                value={fps}
                onChange={(e) => setFps(Number(e.target.value))}
                disabled={procesando}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Calidad: {Math.round(calidad * 100)}%
              </label>
              <input
                type="range"
                min="0.3"
                max="1"
                step="0.1"
                value={calidad}
                onChange={(e) => setCalidad(Number(e.target.value))}
                disabled={procesando}
                className="w-full"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Panel de Estado */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className={`text-2xl mb-2 ${conectado ? 'text-green-600' : 'text-red-600'}`}>
              {conectado ? '🟢' : '🔴'}
            </div>
            <p className="text-sm font-medium">Conexión</p>
            <p className="text-xs text-gray-600">
              {conectado ? 'En línea' : 'Desconectado'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl mb-2">📹</div>
            <p className="text-sm font-medium">Cámara</p>
            <p className="text-xs text-gray-600">
              {camaraActiva ? 'Activa' : 'Inactiva'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl mb-2">⚡</div>
            <p className="text-sm font-medium">Streaming</p>
            <p className="text-xs text-gray-600">
              {procesando ? `${fps} FPS` : 'Detenido'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl mb-2">👥</div>
            <p className="text-sm font-medium">Clientes</p>
            <p className="text-xs text-gray-600">
              {stats.connected_clients} conectados
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Video y Canvas */}
      <Card>
        <CardHeader>
          <CardTitle>Vista de Cámara</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="w-full max-w-2xl h-96 bg-black border-2 border-gray-300 rounded-lg"
              style={{ objectFit: 'cover' }}
            />
            <canvas
              ref={canvasRef}
              className="hidden"
            />
            
            {/* Overlay de procesamiento */}
            {procesando && (
              <div className="absolute top-4 left-4 bg-blue-600 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                Procesando {fps} FPS
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Estadísticas en Tiempo Real */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart className="h-5 w-5" />
            Estadísticas en Tiempo Real
            <Button onClick={obtenerStats} size="sm" variant="outline" className="ml-auto">
              Actualizar
            </Button>
            <Button onClick={resetearStats} size="sm" variant="outline">
              Resetear
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.total_frames_processed}</div>
              <p className="text-sm text-gray-600">Frames Procesados</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{stats.successful_recognitions}</div>
              <p className="text-sm text-gray-600">Reconocimientos Exitosos</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">{stats.failed_recognitions}</div>
              <p className="text-sm text-gray-600">Reconocimientos Fallidos</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {Math.round(stats.average_processing_time * 1000)}ms
              </div>
              <p className="text-sm text-gray-600">Tiempo Promedio</p>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span>Tasa de Éxito</span>
              <span>{tasaExito.toFixed(1)}%</span>
            </div>
            <Progress value={tasaExito} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Último Resultado */}
      {ultimoResultado && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {ultimoResultado.reconocido ? (
                <>
                  <CheckCircle className="h-6 w-6 text-green-600" />
                  <span className="text-green-600">✅ ACCESO AUTORIZADO</span>
                </>
              ) : (
                <>
                  <AlertCircle className="h-6 w-6 text-red-600" />
                  <span className="text-red-600">❌ ACCESO DENEGADO</span>
                </>
              )}
              <Badge variant="outline" className="ml-auto">
                Frame #{ultimoResultado.frame_id}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {ultimoResultado.reconocido && ultimoResultado.persona ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-lg px-3 py-1">
                    👤 {ultimoResultado.persona.nombre}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium">📊 Confianza:</span>
                    <Badge variant="secondary" className="ml-2">
                      {Math.round((ultimoResultado.confianza || 0) * 100)}%
                    </Badge>
                  </div>
                  
                  {ultimoResultado.persona.vivienda && (
                    <div>
                      <span className="font-medium">🏠 Vivienda:</span>
                      <Badge variant="outline" className="ml-2">
                        {ultimoResultado.persona.vivienda}
                      </Badge>
                    </div>
                  )}
                  
                  <div>
                    <span className="font-medium">⚡ Tiempo:</span>
                    <Badge variant="secondary" className="ml-2">
                      {ultimoResultado.processing_time?.toFixed(1)}ms
                    </Badge>
                  </div>
                  
                  <div>
                    <span className="font-medium">🤖 Proveedor:</span>
                    <Badge variant="outline" className="ml-2">
                      {ultimoResultado.proveedor}
                    </Badge>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-lg font-medium text-red-600">
                  Persona no reconocida en el sistema
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  {ultimoResultado.mensaje || ultimoResultado.error || 'Acceso denegado por seguridad'}
                </p>
                {ultimoResultado.processing_time && (
                  <Badge variant="secondary" className="mt-2">
                    Procesado en {ultimoResultado.processing_time.toFixed(1)}ms
                  </Badge>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}