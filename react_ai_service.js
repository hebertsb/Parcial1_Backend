// src/services/aiService.js - Para tu frontend React
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AIService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE}/api/seguridad`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Token automático
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Entrenar modelo IA
  async trainModel() {
    const response = await this.api.post('/ia/entrenar/');
    return response.data;
  }

  // Obtener estadísticas IA
  async getStats() {
    const response = await this.api.get('/ia/estadisticas/');
    return response.data;
  }

  // Re-entrenar modelo
  async retrain() {
    const response = await this.api.post('/ia/re-entrenar/');
    return response.data;
  }

  // Probar con imagen
  async testImage(imageFile) {
    const formData = new FormData();
    formData.append('imagen', imageFile);
    
    const response = await this.api.post('/ia/probar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export default new AIService();