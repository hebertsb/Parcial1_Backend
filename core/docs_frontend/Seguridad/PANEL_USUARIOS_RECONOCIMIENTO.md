# GUÍA COMPLETA: PANEL DE SEGURIDAD - USUARIOS CON RECONOCIMIENTO FACIAL

## 🛡️ ENDPOINT PARA LISTAR USUARIOS CON RECONOCIMIENTO FACIAL

### OBTENER USUARIOS CON FOTOS REGISTRADAS
```
GET /seguridad/api/usuarios-reconocimiento/
Authorization: Bearer {seguridad_token}
```

**RESPONSE PAYLOAD:**
```json
{
  "success": true,
  "data": [
    {
      "copropietario_id": 8,
      "usuario_id": 6,
      "nombres_completos": "Laura Segundo González Segundo",
      "documento_identidad": "12345010",
      "unidad_residencial": "V010",
      "tipo_residente": "Propietario",
      "email": "laura.gonzález10@test.com",
      "telefono": "77777777",
      "foto_perfil_url": "https://dl.dropboxusercontent.com/scl/fi/...",
      "reconocimiento_facial": {
        "total_fotos": 10,
        "fecha_ultimo_enrolamiento": "2025-09-28T16:45:00Z",
        "ultima_verificacion": "2025-09-28T18:30:00Z",
        "fotos_urls": [
          "https://dl.dropboxusercontent.com/scl/fi/foto1.jpg",
          "https://dl.dropboxusercontent.com/scl/fi/foto2.jpg",
          "https://dl.dropboxusercontent.com/scl/fi/foto3.jpg"
        ]
      },
      "activo": true,
      "fecha_creacion": "2025-09-21T09:15:00Z"
    }
  ],
  "total": 3,
  "estadisticas": {
    "total_usuarios": 9,
    "con_fotos": 3,
    "propietarios": 2,
    "inquilinos": 1,
    "familiares": 0
  }
}
```

## 📋 IMPLEMENTACIÓN FRONTEND - PANEL SEGURIDAD

### COMPONENTE: PanelSeguridadReconocimiento.jsx
```jsx
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Avatar, 
  Badge, 
  Button, 
  Row, 
  Col, 
  Statistic, 
  Image, 
  Modal, 
  message,
  Input,
  Select,
  Space,
  Typography
} from 'antd';
import { 
  UserOutlined, 
  CameraOutlined, 
  SearchOutlined,
  EyeOutlined,
  HomeOutlined,
  PhoneOutlined,
  IdcardOutlined
} from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

const PanelSeguridadReconocimiento = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [usuariosFiltrados, setUsuariosFiltrados] = useState([]);
  const [estadisticas, setEstadisticas] = useState({});
  const [loading, setLoading] = useState(false);
  const [modalFotos, setModalFotos] = useState({ visible: false, usuario: null });
  const [filtros, setFiltros] = useState({
    busqueda: '',
    tipo_residente: 'todos'
  });

  // Cargar usuarios con reconocimiento facial
  const cargarUsuarios = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('seguridad_token');
      const response = await fetch('/seguridad/api/usuarios-reconocimiento/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setUsuarios(data.data);
        setUsuariosFiltrados(data.data);
        setEstadisticas(data.estadisticas);
      } else {
        message.error('Error cargando usuarios');
      }
    } catch (error) {
      message.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar usuarios
  const filtrarUsuarios = () => {
    let resultado = usuarios;

    if (filtros.busqueda) {
      const busqueda = filtros.busqueda.toLowerCase();
      resultado = resultado.filter(usuario => 
        usuario.nombres_completos.toLowerCase().includes(busqueda) ||
        usuario.documento_identidad.includes(busqueda) ||
        usuario.unidad_residencial.toLowerCase().includes(busqueda)
      );
    }

    if (filtros.tipo_residente !== 'todos') {
      resultado = resultado.filter(usuario => 
        usuario.tipo_residente === filtros.tipo_residente
      );
    }

    setUsuariosFiltrados(resultado);
  };

  // Mostrar fotos del usuario
  const mostrarFotos = (usuario) => {
    setModalFotos({ visible: true, usuario });
  };

  useEffect(() => {
    cargarUsuarios();
  }, []);

  useEffect(() => {
    filtrarUsuarios();
  }, [filtros, usuarios]);

  return (
    <div className="panel-seguridad-container">
      {/* Header con estadísticas */}
      <div className="estadisticas-header">
        <Title level={2}>
          <CameraOutlined style={{ marginRight: 8 }} />
          Usuarios con Reconocimiento Facial
        </Title>
        
        <Row gutter={16} className="estadisticas-cards">
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Total Usuarios"
                value={estadisticas.total_usuarios || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Con Fotos"
                value={estadisticas.con_fotos || 0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Propietarios"
                value={estadisticas.propietarios || 0}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Inquilinos"
                value={estadisticas.inquilinos || 0}
                valueStyle={{ color: '#eb2f96' }}
              />
            </Card>
          </Col>
        </Row>
      </div>

      {/* Filtros */}
      <Card className="filtros-card">
        <Row gutter={16} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="Buscar por nombre, documento o unidad"
              allowClear
              enterButton={<SearchOutlined />}
              value={filtros.busqueda}
              onChange={(e) => setFiltros(prev => ({ ...prev, busqueda: e.target.value }))}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              style={{ width: '100%' }}
              placeholder="Tipo de residente"
              value={filtros.tipo_residente}
              onChange={(value) => setFiltros(prev => ({ ...prev, tipo_residente: value }))}
            >
              <Option value="todos">Todos</Option>
              <Option value="Propietario">Propietarios</Option>
              <Option value="Inquilino">Inquilinos</Option>
              <Option value="Familiar">Familiares</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Button 
              type="primary" 
              onClick={cargarUsuarios} 
              loading={loading}
              block
            >
              Actualizar
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Lista de usuarios */}
      <Card title={`Usuarios encontrados: ${usuariosFiltrados.length}`}>
        <List
          loading={loading}
          dataSource={usuariosFiltrados}
          renderItem={(usuario) => (
            <List.Item
              className="usuario-item"
              actions={[
                <Button 
                  icon={<EyeOutlined />}
                  onClick={() => mostrarFotos(usuario)}
                >
                  Ver Fotos ({usuario.reconocimiento_facial.total_fotos})
                </Button>
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Avatar 
                    size={64}
                    icon={<UserOutlined />}
                    src={usuario.foto_perfil_url}
                  />
                }
                title={
                  <div className="usuario-title">
                    <span className="nombre">{usuario.nombres_completos}</span>
                    <Badge 
                      color={usuario.tipo_residente === 'Propietario' ? 'blue' : 
                             usuario.tipo_residente === 'Inquilino' ? 'green' : 'purple'}
                      text={usuario.tipo_residente}
                      style={{ marginLeft: 8 }}
                    />
                  </div>
                }
                description={
                  <div className="usuario-details">
                    <div className="detail-row">
                      <IdcardOutlined style={{ color: '#666' }} />
                      <Text>{usuario.documento_identidad}</Text>
                    </div>
                    <div className="detail-row">
                      <HomeOutlined style={{ color: '#666' }} />
                      <Text strong>{usuario.unidad_residencial}</Text>
                    </div>
                    <div className="detail-row">
                      <PhoneOutlined style={{ color: '#666' }} />
                      <Text>{usuario.telefono || 'Sin teléfono'}</Text>
                    </div>
                    <div className="detail-row">
                      <CameraOutlined style={{ color: '#52c41a' }} />
                      <Text>
                        {usuario.reconocimiento_facial.total_fotos} fotos registradas
                        {usuario.reconocimiento_facial.ultima_verificacion && (
                          <span style={{ color: '#666', marginLeft: 8 }}>
                            (Última verificación: {new Date(usuario.reconocimiento_facial.ultima_verificacion).toLocaleDateString()})
                          </span>
                        )}
                      </Text>
                    </div>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {/* Modal para mostrar fotos */}
      <Modal
        title={`Fotos de Reconocimiento - ${modalFotos.usuario?.nombres_completos}`}
        open={modalFotos.visible}
        onCancel={() => setModalFotos({ visible: false, usuario: null })}
        footer={null}
        width={800}
      >
        {modalFotos.usuario && (
          <div className="fotos-modal-content">
            <div className="usuario-info-modal">
              <Row gutter={16}>
                <Col span={12}>
                  <Text strong>Unidad: </Text>
                  <Text>{modalFotos.usuario.unidad_residencial}</Text>
                </Col>
                <Col span={12}>
                  <Text strong>Total fotos: </Text>
                  <Text>{modalFotos.usuario.reconocimiento_facial.total_fotos}</Text>
                </Col>
              </Row>
            </div>
            
            <div className="fotos-grid">
              <Row gutter={[16, 16]}>
                {modalFotos.usuario.reconocimiento_facial.fotos_urls.map((url, index) => (
                  <Col xs={24} sm={12} md={8} key={index}>
                    <div className="foto-preview">
                      <Image
                        src={url}
                        alt={`Foto ${index + 1}`}
                        style={{ 
                          width: '100%', 
                          height: '200px', 
                          objectFit: 'cover',
                          borderRadius: '8px'
                        }}
                        fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAKJFjYGASSSwoyGFhYGDIzSspCnJ3UoiIjFJgf8LAwSDCIMogwMCcmFxc4BgQ4ANUwgCjUcG3awyMIPqyLsis7PPOq3QdDFcvjV3jOD1boQVTPQrgSkktTgbSf4A4LbmgqISBgTEFyFYuLykAsTuAbJEioKOA7DkgdjqEvQHEToKwj4DVhAQ5A9k3gGyB5IxEoBmML4BsnSQk8XQkNtReEOBxcfXxUQg1Mjc0dyHgXNJBSWpFCYh2zi+oLMpMzyhRcASGUqqCZ16yno6CkYGRAQMDKMwhqj/fAIcloxgHQqxAjIHBEugw5sUIsSQpBobtQPdLciLEVJYzMPBHMDBsayhILEqEO4DxG0txmrERhM29nYGBddr//5/DGRjYNRkY/l7////39v///y4Dmn+LgeHANwDrkl1AuO+pmgAAADhlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAAqACAAQAAAABAAAAwqADAAQAAAABAAAAwwAAAAD9b/HnAAAHlklEQVR4Ae3dP3Ik1RUG8A+b3dvBSwwxbMFGhKW2sEMrWMbAyGwDM8sYu9gJbIGZADLNmzWmJWA0p4m0vJ6Z7umZ6u6b7rv3/39pNBLVdt+q73zvd97tN7dvbW9vb6cHBwf/1n69+OKL6aWXXkqvvfZaeuONN9LNmzfTs2fP0nfffZeePn2afvzxx4Jc/vHHH9P333+ffvnll/TSSy+lZ8+epSdPnqSbN2+mGzdu5N+7efNmevPNN9PVq1fTK6+8kl555ZV069atxQUCgUdHR+m9995Lv/rVr9KdO3fSBx98kL777rtdxrRnzTdv3kx37txJH374YfrNb36T3n777fTtt9+mH374If3444/5e0+fPk3fffdd+uKLLwo3jIgz5o8//vjjj3frKzg6OspJ/vvf/3b/8Ic/dH/+85+7L7/8snvy5En34Ycfdn/9618L8uabbxZu3LiR3n333fT++++n3/3ud+nOnTvpypUr6dVXX83V4OQk/8knn6RPP/00ffLJJ+lf//pX+ve//51+/vnnCiJc+vLly+nq1avprbfeSr/97W/T3bt302effZb+8Y9/pE8//TT985//TP/+97/T48eP07/+9a/8/c8//zz96le/Sr/85S/T7du388/t7e3tH89OOjw8TFeuXEnvvPNO+sMf/pB+/etfp9u3b6eXX345/eY3v0mvvfZaevXVV9Orr76abty4kW7evJlu3bqVn9fNmzfzf+/cuZPee++99MYbb6TXX389v86NG/"}'
                      />
                      <div className="foto-overlay">
                        <Text>Foto {index + 1}</Text>
                      </div>
                    </div>
                  </Col>
                ))}
              </Row>
            </div>

            {modalFotos.usuario.reconocimiento_facial.fotos_urls.length === 0 && (
              <div className="no-fotos">
                <Text type="secondary">No hay fotos disponibles para mostrar</Text>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PanelSeguridadReconocimiento;
```

### CSS ASOCIADO: panel-seguridad.css
```css
.panel-seguridad-container {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.estadisticas-header {
  margin-bottom: 24px;
}

.estadisticas-cards {
  margin-top: 16px;
}

.estadisticas-cards .ant-card {
  text-align: center;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filtros-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.usuario-item {
  background: white;
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.usuario-title {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.usuario-title .nombre {
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
}

.usuario-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-row .anticon {
  font-size: 14px;
}

.fotos-modal-content {
  padding: 16px 0;
}

.usuario-info-modal {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.fotos-grid {
  max-height: 400px;
  overflow-y: auto;
}

.foto-preview {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.foto-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 8px;
  text-align: center;
}

.no-fotos {
  text-align: center;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .panel-seguridad-container {
    padding: 16px;
  }
  
  .usuario-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filtros-card .ant-row {
    gap: 16px;
  }
  
  .estadisticas-cards .ant-col {
    margin-bottom: 16px;
  }
}

@media (max-width: 576px) {
  .fotos-grid .ant-col {
    padding: 8px;
  }
  
  .foto-preview img {
    height: 150px !important;
  }
}
```

## 🔧 INTEGRACIÓN CON VERIFICACIÓN FACIAL

### Agregar botón de verificación en tiempo real:
```jsx
// En el componente anterior, agregar en las acciones:
<Button 
  type="primary"
  icon={<CameraOutlined />}
  onClick={() => iniciarVerificacion(usuario)}
>
  Verificar Acceso
</Button>

// Función para verificar acceso
const iniciarVerificacion = (usuario) => {
  // Redirigir al sistema de verificación facial
  // O abrir modal con cámara para verificación en tiempo real
  window.location.href = `/seguridad/verificar/${usuario.copropietario_id}`;
};
```

## 📱 MENÚ DE NAVEGACIÓN SEGURIDAD

### Agregar al menú del panel de seguridad:
```jsx
const menuItemsSeguridad = [
  {
    key: 'usuarios-reconocimiento',
    icon: <CameraOutlined />,
    label: 'Usuarios con Fotos',
    path: '/seguridad/usuarios-reconocimiento'
  },
  {
    key: 'verificar-acceso',
    icon: <ScanOutlined />,
    label: 'Verificar Acceso',
    path: '/seguridad/verificar-acceso'
  },
  // ... otros items
];
```

## 🔒 AUTENTICACIÓN Y PERMISOS

### Verificar permisos de seguridad:
```jsx
const verificarPermisoSeguridad = () => {
  const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');
  return usuario.roles?.includes('Seguridad') || usuario.roles?.includes('Administrador');
};

// Usar en componente:
useEffect(() => {
  if (!verificarPermisoSeguridad()) {
    message.error('No tienes permisos para acceder a esta sección');
    navigate('/login');
  }
}, []);
```

## 📊 FUNCIONALIDADES ADICIONALES

### 1. Búsqueda avanzada con filtros:
```jsx
const filtrosAvanzados = {
  fecha_registro: null,
  ultima_verificacion: null,
  numero_fotos_min: 1,
  estado_activo: true
};
```

### 2. Exportar lista de usuarios:
```jsx
const exportarUsuarios = () => {
  const csvContent = usuariosFiltrados.map(u => 
    `${u.nombres_completos},${u.documento_identidad},${u.unidad_residencial},${u.reconocimiento_facial.total_fotos}`
  ).join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'usuarios_reconocimiento_facial.csv';
  a.click();
};
```

### 3. Notificaciones en tiempo real:
```jsx
// Usar WebSocket o polling para actualizaciones
useEffect(() => {
  const interval = setInterval(() => {
    cargarUsuarios(); // Actualizar cada 30 segundos
  }, 30000);
  
  return () => clearInterval(interval);
}, []);
```

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear componente PanelSeguridadReconocimiento.jsx
- [ ] Implementar endpoint backend
- [ ] Agregar estilos CSS responsivos
- [ ] Configurar rutas de seguridad
- [ ] Integrar con sistema de verificación
- [ ] Probar con diferentes roles de usuario
- [ ] Validar permisos de acceso
- [ ] Implementar filtros y búsqueda
- [ ] Agregar funcionalidad de exportación
- [ ] Probar en dispositivos móviles

## 🚀 PRÓXIMOS PASOS

1. **Integrar con cámara web** para verificación en tiempo real
2. **Agregar sistema de alertas** cuando se detecta acceso no autorizado
3. **Implementar historial** de verificaciones por usuario
4. **Agregar reportes** de actividad de reconocimiento facial
5. **Integrar con sistema de notificaciones** push