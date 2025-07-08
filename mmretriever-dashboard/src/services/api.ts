import axios from 'axios';
import {
  SearchResponse,
  InsertResponse,
  StatusResponse,
  HealthResponse,
  TextSearchRequest,
  ImageSearchRequest,
  VideoSearchRequest,
  MultimodalSearchRequest,
  InsertDataRequest,
  BatchInsertRequest,
  DataListRequest,
  DataListResponse
} from '../types/api';

// Create axios instance
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// API service class
export class ApiService {
  // Health check
  static async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/health');
    return response.data;
  }

  // Get service status
  static async getStatus(): Promise<StatusResponse> {
    const response = await api.get('/status');
    return response.data;
  }

  // Text search
  static async searchText(request: TextSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/text', request);
    return response.data;
  }

  // Image search
  static async searchImage(request: ImageSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/image', request);
    return response.data;
  }

  // Video search
  static async searchVideo(request: VideoSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/video', request);
    return response.data;
  }

  // Multimodal search
  static async searchMultimodal(request: MultimodalSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/multimodal', request);
    return response.data;
  }

  // Insert single data
  static async insertData(request: InsertDataRequest): Promise<InsertResponse> {
    const response = await api.post('/data/insert', request);
    return response.data;
  }

  // Batch insert data
  static async batchInsertData(request: BatchInsertRequest): Promise<InsertResponse> {
    const response = await api.post('/data/batch_insert', request);
    return response.data;
  }

  // Load all data
  static async listData(request: DataListRequest): Promise<DataListResponse> {
    const response = await api.post('/data/list', request);
    return response.data;
  }
}

export default api; 