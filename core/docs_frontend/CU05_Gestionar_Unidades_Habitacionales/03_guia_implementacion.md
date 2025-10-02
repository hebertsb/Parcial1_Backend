# 🚀 CU05 - Guía de Implementación Frontend
## Paso a Paso para Desarrolladores

### 📋 **PREREQUISITOS**

Antes de comenzar, asegúrate de tener:
- ✅ Framework frontend configurado (React/Vue/Angular)
- ✅ Cliente HTTP (axios, fetch, etc.)
- ✅ Router configurado
- ✅ Sistema de state management (opcional pero recomendado)
- ✅ UI Library (Material-UI, Bootstrap, Tailwind, etc.)

---

## 🔧 **CONFIGURACIÓN INICIAL**

### **1. Configurar Cliente HTTP**

#### **React con Axios**:
```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para agregar token automáticamente
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor para manejar errores globalmente
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expirado - limpiar storage y redirigir
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default apiClient;
```

#### **Vue con Axios**:
```javascript
// plugins/axios.js
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    timeout: 10000,
});

// Instalar como plugin
export default {
    install(app) {
        app.config.globalProperties.$api = apiClient;
        app.provide('api', apiClient);
    }
};
```

### **2. Servicio de Autenticación**

```javascript
// services/authService.js
import apiClient from './api';

export const authService = {
    async login(email, password) {
        try {
            const response = await apiClient.post('/api/auth/login/', {
                email,
                password
            });
            
            const { access, refresh } = response.data;
            
            // Guardar tokens
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            
            return { success: true, data: response.data };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.detail || 'Error de autenticación' 
            };
        }
    },
    
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    
    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },
    
    getToken() {
        return localStorage.getItem('access_token');
    }
};
```

---

## 🏠 **IMPLEMENTACIÓN DE VIVIENDAS**

### **3. Servicio de Viviendas**

```javascript
// services/viviendasService.js
import apiClient from './api';

export const viviendasService = {
    // Listar todas las viviendas
    async getViviendas(params = {}) {
        try {
            const response = await apiClient.get('/api/viviendas/', { params });
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Obtener vivienda específica
    async getVivienda(id) {
        try {
            const response = await apiClient.get(`/api/viviendas/${id}/`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Crear nueva vivienda
    async createVivienda(viviendaData) {
        try {
            const response = await apiClient.post('/api/viviendas/', viviendaData);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Actualizar vivienda
    async updateVivienda(id, viviendaData) {
        try {
            const response = await apiClient.patch(`/api/viviendas/${id}/`, viviendaData);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Eliminar vivienda (soft delete)
    async deleteVivienda(id) {
        try {
            const response = await apiClient.delete(`/api/viviendas/${id}/`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Activar vivienda
    async activarVivienda(id) {
        try {
            const response = await apiClient.post(`/api/viviendas/${id}/activar/`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Obtener estadísticas
    async getEstadisticas() {
        try {
            const response = await apiClient.get('/api/viviendas/estadisticas/');
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Obtener propiedades de una vivienda
    async getPropiedadesVivienda(id) {
        try {
            const response = await apiClient.get(`/api/viviendas/${id}/propiedades/`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: this.handleError(error) };
        }
    },
    
    // Manejar errores
    handleError(error) {
        if (error.response?.data) {
            return error.response.data;
        }
        return { message: 'Error de conexión' };
    }
};
```

### **4. Hook/Composable para Viviendas (React/Vue)**

#### **React Hook**:
```javascript
// hooks/useViviendas.js
import { useState, useEffect } from 'react';
import { viviendasService } from '../services/viviendasService';

export const useViviendas = () => {
    const [viviendas, setViviendas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const loadViviendas = async (params = {}) => {
        setLoading(true);
        setError(null);
        
        const result = await viviendasService.getViviendas(params);
        
        if (result.success) {
            setViviendas(result.data);
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    };
    
    const createVivienda = async (viviendaData) => {
        setLoading(true);
        setError(null);
        
        const result = await viviendasService.createVivienda(viviendaData);
        
        if (result.success) {
            // Recargar lista
            await loadViviendas();
            return { success: true, data: result.data };
        } else {
            setError(result.error);
            return { success: false, error: result.error };
        }
    };
    
    const updateVivienda = async (id, viviendaData) => {
        setLoading(true);
        setError(null);
        
        const result = await viviendasService.updateVivienda(id, viviendaData);
        
        if (result.success) {
            // Actualizar lista local
            setViviendas(prev => 
                prev.map(v => v.id === id ? result.data : v)
            );
            return { success: true, data: result.data };
        } else {
            setError(result.error);
            return { success: false, error: result.error };
        }
    };
    
    const deleteVivienda = async (id) => {
        setLoading(true);
        setError(null);
        
        const result = await viviendasService.deleteVivienda(id);
        
        if (result.success) {
            // Recargar lista
            await loadViviendas();
            return { success: true };
        } else {
            setError(result.error);
            return { success: false, error: result.error };
        }
    };
    
    useEffect(() => {
        loadViviendas();
    }, []);
    
    return {
        viviendas,
        loading,
        error,
        loadViviendas,
        createVivienda,
        updateVivienda,
        deleteVivienda
    };
};
```

#### **Vue Composable**:
```javascript
// composables/useViviendas.js
import { ref, onMounted } from 'vue';
import { viviendasService } from '../services/viviendasService';

export function useViviendas() {
    const viviendas = ref([]);
    const loading = ref(false);
    const error = ref(null);
    
    const loadViviendas = async (params = {}) => {
        loading.value = true;
        error.value = null;
        
        const result = await viviendasService.getViviendas(params);
        
        if (result.success) {
            viviendas.value = result.data;
        } else {
            error.value = result.error;
        }
        
        loading.value = false;
    };
    
    // Resto de métodos similar a React...
    
    onMounted(() => {
        loadViviendas();
    });
    
    return {
        viviendas,
        loading,
        error,
        loadViviendas,
        // otros métodos...
    };
}
```

---

## 🎨 **COMPONENTES DE UI**

### **5. Componente Lista de Viviendas**

#### **React Component**:
```jsx
// components/ViviendaList.jsx
import React, { useState } from 'react';
import { useViviendas } from '../hooks/useViviendas';
import ViviendaCard from './ViviendaCard';
import SearchFilter from './SearchFilter';
import LoadingSpinner from './LoadingSpinner';

const ViviendaList = () => {
    const { viviendas, loading, error, loadViviendas } = useViviendas();
    const [filters, setFilters] = useState({
        search: '',
        estado: '',
        tipo_vivienda: ''
    });
    
    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
        loadViviendas(newFilters);
    };
    
    if (loading) return <LoadingSpinner />;
    if (error) return <div className="error">Error: {error.message}</div>;
    
    return (
        <div className="vivienda-list">
            <div className="header">
                <h1>🏠 Gestión de Viviendas</h1>
                <button 
                    className="btn-primary"
                    onClick={() => {/* Abrir modal crear */}}
                >
                    ➕ Nueva Vivienda
                </button>
            </div>
            
            <SearchFilter 
                filters={filters}
                onFilterChange={handleFilterChange}
            />
            
            <div className="viviendas-grid">
                {viviendas.length === 0 ? (
                    <div className="empty-state">
                        No hay viviendas registradas
                    </div>
                ) : (
                    viviendas.map(vivienda => (
                        <ViviendaCard 
                            key={vivienda.id}
                            vivienda={vivienda}
                            onEdit={(id) => {/* Abrir modal editar */}}
                            onDelete={(id) => {/* Confirmar y eliminar */}}
                        />
                    ))
                )}
            </div>
        </div>
    );
};

export default ViviendaList;
```

### **6. Componente Tarjeta de Vivienda**

```jsx
// components/ViviendaCard.jsx
import React from 'react';

const ViviendaCard = ({ vivienda, onEdit, onDelete, onView }) => {
    const getEstadoColor = (estado) => {
        const colors = {
            'activa': 'green',
            'inactiva': 'red',
            'mantenimiento': 'orange'
        };
        return colors[estado] || 'gray';
    };
    
    const getTipoIcon = (tipo) => {
        const icons = {
            'casa': '🏠',
            'departamento': '🏢',
            'local': '🏪'
        };
        return icons[tipo] || '🏠';
    };
    
    return (
        <div className="vivienda-card">
            <div className="card-header">
                <h3>
                    {getTipoIcon(vivienda.tipo_vivienda)} 
                    {vivienda.numero_casa}
                </h3>
                <span 
                    className={`status-badge ${vivienda.estado}`}
                    style={{ color: getEstadoColor(vivienda.estado) }}
                >
                    {vivienda.estado}
                </span>
            </div>
            
            <div className="card-body">
                <div className="info-row">
                    <span className="label">Bloque:</span>
                    <span className="value">{vivienda.bloque}</span>
                </div>
                <div className="info-row">
                    <span className="label">Tipo:</span>
                    <span className="value">{vivienda.tipo_vivienda}</span>
                </div>
                <div className="info-row">
                    <span className="label">Metros²:</span>
                    <span className="value">{vivienda.metros_cuadrados} m²</span>
                </div>
                <div className="info-row">
                    <span className="label">Tarifa:</span>
                    <span className="value">${vivienda.tarifa_base_expensas}</span>
                </div>
            </div>
            
            <div className="card-actions">
                <button 
                    className="btn-secondary"
                    onClick={() => onView(vivienda.id)}
                    title="Ver detalles"
                >
                    👁️
                </button>
                <button 
                    className="btn-primary"
                    onClick={() => onEdit(vivienda.id)}
                    title="Editar"
                >
                    ✏️
                </button>
                <button 
                    className="btn-danger"
                    onClick={() => onDelete(vivienda.id)}
                    title="Eliminar"
                >
                    🗑️
                </button>
            </div>
        </div>
    );
};

export default ViviendaCard;
```

### **7. Componente Formulario de Vivienda**

```jsx
// components/ViviendaForm.jsx
import React, { useState, useEffect } from 'react';
import { viviendasService } from '../services/viviendasService';

const ViviendaForm = ({ vivienda = null, onSave, onCancel }) => {
    const [formData, setFormData] = useState({
        numero_casa: '',
        bloque: '',
        tipo_vivienda: 'departamento',
        metros_cuadrados: '',
        tarifa_base_expensas: '',
        tipo_cobranza: 'por_casa',
        estado: 'activa'
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    
    // Si es edición, cargar datos
    useEffect(() => {
        if (vivienda) {
            setFormData({
                numero_casa: vivienda.numero_casa,
                bloque: vivienda.bloque,
                tipo_vivienda: vivienda.tipo_vivienda,
                metros_cuadrados: vivienda.metros_cuadrados,
                tarifa_base_expensas: vivienda.tarifa_base_expensas,
                tipo_cobranza: vivienda.tipo_cobranza,
                estado: vivienda.estado
            });
        }
    }, [vivienda]);
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Limpiar error del campo
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: null
            }));
        }
    };
    
    const validateForm = () => {
        const newErrors = {};
        
        if (!formData.numero_casa.trim()) {
            newErrors.numero_casa = 'Número de casa es requerido';
        }
        
        if (!formData.bloque.trim()) {
            newErrors.bloque = 'Bloque es requerido';
        }
        
        if (!formData.metros_cuadrados || parseFloat(formData.metros_cuadrados) <= 0) {
            newErrors.metros_cuadrados = 'Metros cuadrados debe ser mayor a 0';
        }
        
        if (!formData.tarifa_base_expensas || parseFloat(formData.tarifa_base_expensas) <= 0) {
            newErrors.tarifa_base_expensas = 'Tarifa debe ser mayor a 0';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        setLoading(true);
        
        try {
            let result;
            if (vivienda) {
                // Editar
                result = await viviendasService.updateVivienda(vivienda.id, formData);
            } else {
                // Crear
                result = await viviendasService.createVivienda(formData);
            }
            
            if (result.success) {
                onSave(result.data);
            } else {
                // Mostrar errores del servidor
                if (result.error && typeof result.error === 'object') {
                    setErrors(result.error);
                }
            }
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <form onSubmit={handleSubmit} className="vivienda-form">
            <h2>{vivienda ? 'Editar Vivienda' : 'Nueva Vivienda'}</h2>
            
            <div className="form-group">
                <label htmlFor="numero_casa">Número de Casa *</label>
                <input
                    type="text"
                    id="numero_casa"
                    name="numero_casa"
                    value={formData.numero_casa}
                    onChange={handleChange}
                    className={errors.numero_casa ? 'error' : ''}
                    placeholder="Ej: 101A"
                />
                {errors.numero_casa && (
                    <span className="error-message">{errors.numero_casa}</span>
                )}
            </div>
            
            <div className="form-group">
                <label htmlFor="bloque">Bloque *</label>
                <input
                    type="text"
                    id="bloque"
                    name="bloque"
                    value={formData.bloque}
                    onChange={handleChange}
                    className={errors.bloque ? 'error' : ''}
                    placeholder="Ej: A"
                />
                {errors.bloque && (
                    <span className="error-message">{errors.bloque}</span>
                )}
            </div>
            
            <div className="form-group">
                <label htmlFor="tipo_vivienda">Tipo de Vivienda *</label>
                <select
                    id="tipo_vivienda"
                    name="tipo_vivienda"
                    value={formData.tipo_vivienda}
                    onChange={handleChange}
                >
                    <option value="departamento">Departamento</option>
                    <option value="casa">Casa</option>
                    <option value="local">Local</option>
                </select>
            </div>
            
            <div className="form-group">
                <label htmlFor="metros_cuadrados">Metros Cuadrados *</label>
                <input
                    type="number"
                    step="0.01"
                    id="metros_cuadrados"
                    name="metros_cuadrados"
                    value={formData.metros_cuadrados}
                    onChange={handleChange}
                    className={errors.metros_cuadrados ? 'error' : ''}
                    placeholder="65.50"
                />
                {errors.metros_cuadrados && (
                    <span className="error-message">{errors.metros_cuadrados}</span>
                )}
            </div>
            
            <div className="form-group">
                <label htmlFor="tarifa_base_expensas">Tarifa Base Expensas *</label>
                <input
                    type="number"
                    step="0.01"
                    id="tarifa_base_expensas"
                    name="tarifa_base_expensas"
                    value={formData.tarifa_base_expensas}
                    onChange={handleChange}
                    className={errors.tarifa_base_expensas ? 'error' : ''}
                    placeholder="250.00"
                />
                {errors.tarifa_base_expensas && (
                    <span className="error-message">{errors.tarifa_base_expensas}</span>
                )}
            </div>
            
            <div className="form-group">
                <label htmlFor="tipo_cobranza">Tipo de Cobranza</label>
                <select
                    id="tipo_cobranza"
                    name="tipo_cobranza"
                    value={formData.tipo_cobranza}
                    onChange={handleChange}
                >
                    <option value="por_casa">Por Casa</option>
                    <option value="por_metro">Por Metro Cuadrado</option>
                </select>
            </div>
            
            <div className="form-group">
                <label htmlFor="estado">Estado</label>
                <select
                    id="estado"
                    name="estado"
                    value={formData.estado}
                    onChange={handleChange}
                >
                    <option value="activa">Activa</option>
                    <option value="inactiva">Inactiva</option>
                    <option value="mantenimiento">Mantenimiento</option>
                </select>
            </div>
            
            <div className="form-actions">
                <button 
                    type="button" 
                    onClick={onCancel}
                    className="btn-secondary"
                    disabled={loading}
                >
                    Cancelar
                </button>
                <button 
                    type="submit" 
                    className="btn-primary"
                    disabled={loading}
                >
                    {loading ? 'Guardando...' : (vivienda ? 'Actualizar' : 'Crear')}
                </button>
            </div>
        </form>
    );
};

export default ViviendaForm;
```

---

## 🎯 **MEJORES PRÁCTICAS**

### **8. Manejo de Estados de Loading**

```javascript
// Componente con estados de loading
const ComponentWithLoading = () => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    
    // Estados de loading específicos
    const [loadingCreate, setLoadingCreate] = useState(false);
    const [loadingDelete, setLoadingDelete] = useState(false);
    
    return (
        <div>
            {loading && <LoadingSpinner />}
            {error && <ErrorAlert error={error} />}
            {data && <DataComponent data={data} />}
            
            <button 
                disabled={loadingCreate}
                onClick={handleCreate}
            >
                {loadingCreate ? 'Creando...' : 'Crear'}
            </button>
        </div>
    );
};
```

### **9. Validación y Feedback**

```javascript
// Hook para notificaciones
const useNotifications = () => {
    const showSuccess = (message) => {
        // Implementar notificación success
        toast.success(message);
    };
    
    const showError = (message) => {
        // Implementar notificación error
        toast.error(message);
    };
    
    const showWarning = (message) => {
        // Implementar notificación warning
        toast.warning(message);
    };
    
    return { showSuccess, showError, showWarning };
};
```

### **10. Persistencia de Filtros**

```javascript
// Hook para persistir filtros en URL o localStorage
const usePersistedFilters = (key) => {
    const [filters, setFilters] = useState(() => {
        const saved = localStorage.getItem(key);
        return saved ? JSON.parse(saved) : {};
    });
    
    const updateFilters = (newFilters) => {
        setFilters(newFilters);
        localStorage.setItem(key, JSON.stringify(newFilters));
    };
    
    return [filters, updateFilters];
};
```

---

## 📱 **RESPONSIVE DESIGN**

### **11. CSS Responsive Sugerido**

```css
/* styles/viviendas.css */
.vivienda-list {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.viviendas-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.vivienda-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.vivienda-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Responsive para móviles */
@media (max-width: 768px) {
    .header {
        flex-direction: column;
        gap: 10px;
    }
    
    .viviendas-grid {
        grid-template-columns: 1fr;
    }
    
    .card-actions {
        display: flex;
        justify-content: space-around;
    }
}
```

---

Esta guía proporciona una base sólida para implementar el frontend del CU05. Adapta los ejemplos según tu framework y librerías específicas.