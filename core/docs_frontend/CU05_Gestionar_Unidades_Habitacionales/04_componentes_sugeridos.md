# 🎨 CU05 - Componentes UI Sugeridos
## Biblioteca de Componentes Recomendados

### 📋 **COMPONENTES PRINCIPALES**

---

## 🏠 **1. COMPONENTES DE VIVIENDAS**

### **ViviendaList** - Lista Principal
```
Propósito: Mostrar lista de viviendas con filtros y búsqueda
Ubicación: Página principal del módulo
Responsabilidades:
- Mostrar grid/lista de viviendas
- Manejar filtros y búsqueda
- Paginación (opcional)
- Estados de loading/error/empty
```

**Props**:
```typescript
interface ViviendaListProps {
    initialFilters?: FilterOptions;
    onViviendaSelect?: (vivienda: Vivienda) => void;
    showActions?: boolean;
    compact?: boolean; // Para vista compacta
}
```

### **ViviendaCard** - Tarjeta Individual
```
Propósito: Mostrar información resumida de una vivienda
Ubicación: Dentro de ViviendaList
Responsabilidades:
- Mostrar datos básicos
- Estados visuales (activa/inactiva)
- Acciones rápidas (ver/editar/eliminar)
```

**Props**:
```typescript
interface ViviendaCardProps {
    vivienda: Vivienda;
    showActions?: boolean;
    onEdit?: (id: number) => void;
    onDelete?: (id: number) => void;
    onView?: (id: number) => void;
    compact?: boolean;
}
```

### **ViviendaForm** - Formulario CRUD
```
Propósito: Crear/editar viviendas
Ubicación: Modal o página separada
Responsabilidades:
- Validación en tiempo real
- Manejo de errores del servidor
- Estados de loading
- Modo crear/editar
```

**Props**:
```typescript
interface ViviendaFormProps {
    vivienda?: Vivienda | null; // null = crear, objeto = editar
    onSave: (vivienda: Vivienda) => void;
    onCancel: () => void;
    readonly?: boolean;
}
```

### **ViviendaDetail** - Vista Detallada
```
Propósito: Mostrar información completa de vivienda
Ubicación: Modal o página separada
Responsabilidades:
- Información completa
- Historial de cambios
- Propiedades asignadas
- Acciones disponibles
```

**Props**:
```typescript
interface ViviendaDetailProps {
    viviendaId: number;
    onEdit?: () => void;
    onClose?: () => void;
    showPropiedades?: boolean;
}
```

---

## 🔍 **2. COMPONENTES DE BÚSQUEDA Y FILTROS**

### **SearchFilter** - Barra de Búsqueda y Filtros
```
Propósito: Filtrar y buscar viviendas
Ubicación: Encima de ViviendaList
Responsabilidades:
- Búsqueda por texto
- Filtros por estado, tipo, bloque
- Limpiar filtros
- Aplicar filtros en tiempo real
```

**Props**:
```typescript
interface SearchFilterProps {
    filters: FilterOptions;
    onFilterChange: (filters: FilterOptions) => void;
    loading?: boolean;
    showAdvanced?: boolean;
}

interface FilterOptions {
    search?: string;
    estado?: 'activa' | 'inactiva' | 'mantenimiento' | '';
    tipo_vivienda?: 'casa' | 'departamento' | 'local' | '';
    bloque?: string;
    ordering?: string;
}
```

### **QuickFilters** - Filtros Rápidos
```
Propósito: Filtros comunes de acceso rápido
Ubicación: Debajo de búsqueda principal
Responsabilidades:
- Botones de filtros populares
- Contador de resultados
- Estado activo/inactivo
```

**Ejemplo de Implementación**:
```jsx
const QuickFilters = ({ onFilterChange, activeFilters, resultCount }) => (
    <div className="quick-filters">
        <div className="filter-buttons">
            <FilterButton 
                active={activeFilters.estado === 'activa'}
                onClick={() => onFilterChange({ estado: 'activa' })}
                count={counts.activas}
            >
                🟢 Activas
            </FilterButton>
            
            <FilterButton 
                active={activeFilters.tipo_vivienda === 'casa'}
                onClick={() => onFilterChange({ tipo_vivienda: 'casa' })}
                count={counts.casas}
            >
                🏠 Casas
            </FilterButton>
            
            <FilterButton 
                active={activeFilters.tipo_vivienda === 'departamento'}
                onClick={() => onFilterChange({ tipo_vivienda: 'departamento' })}
                count={counts.departamentos}
            >
                🏢 Departamentos
            </FilterButton>
        </div>
        
        <div className="result-count">
            {resultCount} vivienda{resultCount !== 1 ? 's' : ''} encontrada{resultCount !== 1 ? 's' : ''}
        </div>
    </div>
);
```

---

## 📊 **3. COMPONENTES DE ESTADÍSTICAS**

### **EstadisticasWidget** - Resumen Estadístico
```
Propósito: Mostrar métricas del condominio
Ubicación: Dashboard o modal
Responsabilidades:
- Números clave del condominio
- Gráficos simples
- Actualización en tiempo real
```

**Props**:
```typescript
interface EstadisticasWidgetProps {
    estadisticas: EstadisticasCondominio;
    loading?: boolean;
    showGraphics?: boolean;
    compact?: boolean;
}

interface EstadisticasCondominio {
    total_viviendas: number;
    por_estado: Record<string, number>;
    por_tipo: Record<string, number>;
    promedio_tarifa: string;
    total_metros_cuadrados: string;
}
```

**Ejemplo de Layout**:
```jsx
const EstadisticasWidget = ({ estadisticas, loading, showGraphics }) => (
    <div className="estadisticas-widget">
        <h3>📊 Estadísticas del Condominio</h3>
        
        <div className="stats-grid">
            <StatCard 
                icon="🏠"
                title="Total Viviendas"
                value={estadisticas.total_viviendas}
                color="blue"
            />
            
            <StatCard 
                icon="💰"
                title="Tarifa Promedio"
                value={`$${estadisticas.promedio_tarifa}`}
                color="green"
            />
            
            <StatCard 
                icon="📐"
                title="Metros Totales"
                value={`${estadisticas.total_metros_cuadrados} m²`}
                color="purple"
            />
        </div>
        
        {showGraphics && (
            <div className="stats-charts">
                <PieChart 
                    data={estadisticas.por_estado}
                    title="Por Estado"
                />
                <PieChart 
                    data={estadisticas.por_tipo}
                    title="Por Tipo"
                />
            </div>
        )}
    </div>
);
```

---

## 👥 **4. COMPONENTES DE PROPIEDADES**

### **PropiedadesList** - Lista de Asignaciones
```
Propósito: Mostrar propietarios/inquilinos de vivienda
Ubicación: Dentro de ViviendaDetail
Responsabilidades:
- Lista de personas asignadas
- Porcentajes de propiedad
- Fechas de tenencia
- Acciones (asignar/desasignar)
```

**Props**:
```typescript
interface PropiedadesListProps {
    viviendaId: number;
    propiedades: Propiedad[];
    onAsignar?: () => void;
    onDesasignar?: (propiedadId: number) => void;
    readonly?: boolean;
}
```

### **AsignarPropiedadForm** - Formulario de Asignación
```
Propósito: Asignar propietario/inquilino a vivienda
Ubicación: Modal
Responsabilidades:
- Seleccionar persona
- Tipo de tenencia
- Porcentajes de propiedad
- Fechas de inicio/fin
- Validar que no exceda 100%
```

**Props**:
```typescript
interface AsignarPropiedadFormProps {
    viviendaId: number;
    personas: Persona[];
    propiedadesExistentes: Propiedad[];
    onSave: (propiedad: PropiedadCreate) => void;
    onCancel: () => void;
}
```

---

## 🎯 **5. COMPONENTES DE UI GENÉRICOS**

### **Modal** - Modal Reutilizable
```jsx
const Modal = ({ 
    isOpen, 
    onClose, 
    title, 
    children, 
    size = 'medium',
    showCloseButton = true 
}) => {
    if (!isOpen) return null;
    
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div 
                className={`modal-content modal-${size}`}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="modal-header">
                    <h2>{title}</h2>
                    {showCloseButton && (
                        <button 
                            className="modal-close"
                            onClick={onClose}
                            aria-label="Cerrar"
                        >
                            ✕
                        </button>
                    )}
                </div>
                <div className="modal-body">
                    {children}
                </div>
            </div>
        </div>
    );
};
```

### **LoadingSpinner** - Indicador de Carga
```jsx
const LoadingSpinner = ({ size = 'medium', text = 'Cargando...' }) => (
    <div className={`loading-spinner loading-${size}`}>
        <div className="spinner"></div>
        {text && <span className="loading-text">{text}</span>}
    </div>
);
```

### **ErrorAlert** - Alerta de Error
```jsx
const ErrorAlert = ({ error, onDismiss, retryAction }) => (
    <div className="error-alert">
        <div className="error-content">
            <span className="error-icon">⚠️</span>
            <div className="error-message">
                <strong>Error:</strong> {error.message || 'Ha ocurrido un error'}
            </div>
        </div>
        <div className="error-actions">
            {retryAction && (
                <button 
                    className="btn-secondary"
                    onClick={retryAction}
                >
                    🔄 Reintentar
                </button>
            )}
            {onDismiss && (
                <button 
                    className="btn-text"
                    onClick={onDismiss}
                >
                    ✕ Cerrar
                </button>
            )}
        </div>
    </div>
);
```

### **EmptyState** - Estado Vacío
```jsx
const EmptyState = ({ 
    icon = '📭', 
    title = 'No hay datos', 
    description, 
    action 
}) => (
    <div className="empty-state">
        <div className="empty-icon">{icon}</div>
        <h3 className="empty-title">{title}</h3>
        {description && (
            <p className="empty-description">{description}</p>
        )}
        {action && (
            <div className="empty-action">
                {action}
            </div>
        )}
    </div>
);
```

### **ConfirmDialog** - Diálogo de Confirmación
```jsx
const ConfirmDialog = ({ 
    isOpen, 
    title, 
    message, 
    onConfirm, 
    onCancel,
    confirmText = 'Confirmar',
    cancelText = 'Cancelar',
    type = 'warning' // 'warning', 'danger', 'info'
}) => (
    <Modal isOpen={isOpen} onClose={onCancel} title={title} size="small">
        <div className={`confirm-dialog confirm-${type}`}>
            <div className="confirm-message">
                {message}
            </div>
            <div className="confirm-actions">
                <button 
                    className="btn-secondary"
                    onClick={onCancel}
                >
                    {cancelText}
                </button>
                <button 
                    className={`btn-${type === 'danger' ? 'danger' : 'primary'}`}
                    onClick={onConfirm}
                >
                    {confirmText}
                </button>
            </div>
        </div>
    </Modal>
);
```

---

## 📱 **6. COMPONENTES RESPONSIVE**

### **ResponsiveTable** - Tabla Adaptable
```jsx
const ResponsiveTable = ({ 
    columns, 
    data, 
    loading, 
    onRowClick,
    mobileCardRenderer 
}) => {
    const isMobile = useMediaQuery('(max-width: 768px)');
    
    if (isMobile && mobileCardRenderer) {
        return (
            <div className="mobile-cards">
                {data.map((item, index) => (
                    <div key={index} className="mobile-card">
                        {mobileCardRenderer(item)}
                    </div>
                ))}
            </div>
        );
    }
    
    return (
        <table className="responsive-table">
            <thead>
                <tr>
                    {columns.map(col => (
                        <th key={col.key}>{col.title}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {data.map((item, index) => (
                    <tr 
                        key={index}
                        onClick={() => onRowClick?.(item)}
                        className={onRowClick ? 'clickable' : ''}
                    >
                        {columns.map(col => (
                            <td key={col.key}>
                                {col.render ? col.render(item[col.key], item) : item[col.key]}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};
```

---

## 🎨 **7. TOKENS DE DISEÑO SUGERIDOS**

### **Colores**
```css
:root {
    /* Colores primarios */
    --color-primary: #2563eb;
    --color-primary-dark: #1d4ed8;
    --color-primary-light: #60a5fa;
    
    /* Estados */
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-danger: #ef4444;
    --color-info: #06b6d4;
    
    /* Estados de vivienda */
    --color-activa: #10b981;
    --color-inactiva: #6b7280;
    --color-mantenimiento: #f59e0b;
    
    /* Grises */
    --color-gray-50: #f9fafb;
    --color-gray-100: #f3f4f6;
    --color-gray-200: #e5e7eb;
    --color-gray-300: #d1d5db;
    --color-gray-400: #9ca3af;
    --color-gray-500: #6b7280;
    --color-gray-600: #4b5563;
    --color-gray-700: #374151;
    --color-gray-800: #1f2937;
    --color-gray-900: #111827;
}
```

### **Espaciado**
```css
:root {
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    --spacing-3xl: 64px;
}
```

### **Tipografía**
```css
:root {
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-base: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 20px;
    --font-size-2xl: 24px;
    --font-size-3xl: 30px;
    
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
}
```

### **Sombras**
```css
:root {
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

---

## 🧩 **8. COMPOSICIÓN DE COMPONENTES**

### **Página Principal de Viviendas**
```jsx
const ViviendasPage = () => {
    const [showModal, setShowModal] = useState(false);
    const [modalMode, setModalMode] = useState('create'); // 'create', 'edit', 'view'
    const [selectedVivienda, setSelectedVivienda] = useState(null);
    
    return (
        <div className="viviendas-page">
            <PageHeader 
                title="🏠 Gestión de Viviendas"
                actions={[
                    {
                        label: "Nueva Vivienda",
                        icon: "➕",
                        onClick: () => {
                            setModalMode('create');
                            setSelectedVivienda(null);
                            setShowModal(true);
                        }
                    }
                ]}
            />
            
            <EstadisticasWidget showGraphics={false} compact />
            
            <ViviendaList 
                onViviendaSelect={(vivienda) => {
                    setSelectedVivienda(vivienda);
                    setModalMode('view');
                    setShowModal(true);
                }}
            />
            
            <Modal 
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                title={getModalTitle(modalMode)}
                size={modalMode === 'view' ? 'large' : 'medium'}
            >
                {modalMode === 'create' && (
                    <ViviendaForm 
                        onSave={() => setShowModal(false)}
                        onCancel={() => setShowModal(false)}
                    />
                )}
                
                {modalMode === 'edit' && (
                    <ViviendaForm 
                        vivienda={selectedVivienda}
                        onSave={() => setShowModal(false)}
                        onCancel={() => setShowModal(false)}
                    />
                )}
                
                {modalMode === 'view' && (
                    <ViviendaDetail 
                        viviendaId={selectedVivienda?.id}
                        onEdit={() => setModalMode('edit')}
                        showPropiedades
                    />
                )}
            </Modal>
        </div>
    );
};
```

Esta biblioteca de componentes proporciona una base sólida y escalable para implementar el frontend del CU05.