import axios from 'axios';
import { apiConfig, API_ENDPOINTS } from '../config/api';
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
  DataListResponse,
  LoginRequest,
  LoginResponse
} from '../types/api';

// Create axios instance with configuration
const api = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
  withCredentials: apiConfig.withCredentials,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
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
    
    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// API service class
export class ApiService {
  // Authentication
  static async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await api.post(API_ENDPOINTS.LOGIN, request);
    return response.data;
  }

  static async logout(): Promise<any> {
    const response = await api.post(API_ENDPOINTS.LOGOUT);
    return response.data;
  }

  static async getCurrentUser(): Promise<any> {
    const response = await api.get(API_ENDPOINTS.CURRENT_USER);
    return response.data;
  }

  // Health check
  static async getHealth(): Promise<HealthResponse> {
    const response = await api.get(API_ENDPOINTS.HEALTH);
    return response.data;
  }

  // Get service status
  static async getStatus(): Promise<StatusResponse> {
    const response = await api.get(API_ENDPOINTS.STATUS);
    return response.data;
  }

  // Text search
  static async searchText(request: TextSearchRequest): Promise<SearchResponse> {
    const response = await api.post(API_ENDPOINTS.TEXT_SEARCH, request);
    return response.data;
  }

  // Image search
  static async searchImage(request: ImageSearchRequest): Promise<SearchResponse> {
    const response = await api.post(API_ENDPOINTS.IMAGE_SEARCH, request);
    return response.data;
  }

  // Video search
  static async searchVideo(request: VideoSearchRequest): Promise<SearchResponse> {
    const response = await api.post(API_ENDPOINTS.VIDEO_SEARCH, request);
    return response.data;
  }

  // Multimodal search
  static async searchMultimodal(request: MultimodalSearchRequest): Promise<SearchResponse> {
    const response = await api.post(API_ENDPOINTS.MULTIMODAL_SEARCH, request);
    return response.data;
  }

  // Insert single data
  static async insertData(request: InsertDataRequest): Promise<InsertResponse> {
    const response = await api.post(API_ENDPOINTS.INSERT_DATA, request);
    return response.data;
  }

  // Batch insert data
  static async batchInsertData(request: BatchInsertRequest): Promise<InsertResponse> {
    const response = await api.post(API_ENDPOINTS.BATCH_INSERT, request);
    return response.data;
  }

  // Load all data
  static async listData(request: DataListRequest): Promise<DataListResponse> {
    const response = await api.post(API_ENDPOINTS.LIST_DATA, request);
    return response.data;
  }
}

export default api; 