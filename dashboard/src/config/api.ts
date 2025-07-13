import { envConfig } from './environment';

// API Configuration
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  withCredentials: boolean;
}

// Get configuration based on environment
export const getApiConfig = (): ApiConfig => {
  return {
    baseURL: envConfig.apiBaseUrl,
    timeout: 30000,
    withCredentials: false,
  };
};

// Export current configuration
export const apiConfig = getApiConfig();

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  const baseURL = apiConfig.baseURL.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.replace(/^\//, ''); // Remove leading slash
  return `${baseURL}/${cleanEndpoint}`;
};

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  CURRENT_USER: '/auth/me',
  
  // Health and Status
  HEALTH: '/health',
  STATUS: '/status',
  
  // Search
  TEXT_SEARCH: '/search/text',
  IMAGE_SEARCH: '/search/image',
  VIDEO_SEARCH: '/search/video',
  MULTIMODAL_SEARCH: '/search/multimodal',
  
  // Data Management
  INSERT_DATA: '/data/insert',
  BATCH_INSERT: '/data/batch_insert',
  LIST_DATA: '/data/list',
  
  // Async Data Management
  ASYNC_INSERT_DATA: '/data/async_insert',
  ASYNC_BATCH_INSERT: '/data/async_batch_insert',
  TASK_STATUS: '/tasks',
  PENDING_TASKS: '/tasks/pending',
} as const;

console.log('API Configuration:', {
  environment: envConfig.environment,
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
}); 