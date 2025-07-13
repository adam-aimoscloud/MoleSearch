// API response type definition
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

// Search result item
export interface SearchResultItem {
  id: string;
  text: string;
  image_url: string;
  video_url: string;
  image_text: string;
  video_text: string;
  score: number;
}

// All data item
export interface DataListItem {
  id: string;
  text: string;
  image_url: string;
  video_url: string;
  image_text: string;
  video_text: string;
}

// All data query request
export interface DataListRequest {
  page: number;
  page_size: number;
}

// All data query response
export interface DataListResponse {
  success: boolean;
  message: string;
  total: number;
  items: DataListItem[];
  page: number;
  page_size: number;
}

// Search response
export interface SearchResponse {
  success: boolean;
  message: string;
  total: number;
  results: SearchResultItem[];
  query_time: number;
}

// Insert response
export interface InsertResponse {
  success: boolean;
  message: string;
  inserted_count?: number;
  processing_time?: number;
}

// Batch insert request
export interface BatchInsertRequest {
  data: InsertDataRequest[];
}

// Insert data request
export interface InsertDataRequest {
  text: string;
  image_url: string;
  video_url: string;
}

// Async task types
export interface AsyncInsertDataRequest {
  text?: string;
  image_url?: string;
  video_url?: string;
}

export interface AsyncBatchInsertRequest {
  data_list: AsyncInsertDataRequest[];
}

export interface AsyncTaskResponse {
  success: boolean;
  message: string;
  task_id: string;
  estimated_time?: number;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
}

export interface TaskStatusResponse {
  success: boolean;
  message: string;
  task_status: TaskStatus;
}

export interface TaskListResponse {
  success: boolean;
  message: string;
  tasks: TaskStatus[];
  total: number;
}

// API Key management types
export interface ApiKeyInfo {
  key_id: string;
  name: string;
  key: string;
  created_at: string;
  last_used_at?: string;
  expires_at?: string;
  permissions: string[];
}

export interface CreateApiKeyRequest {
  name: string;
  expires_in_days?: number;
  permissions?: string[];
}

export interface CreateApiKeyResponse {
  success: boolean;
  message: string;
  api_key: ApiKeyInfo;
}

export interface ApiKeyListResponse {
  success: boolean;
  message: string;
  api_keys: ApiKeyInfo[];
  total: number;
}

export interface DeleteApiKeyResponse {
  success: boolean;
  message: string;
}

// Text search request
export interface TextSearchRequest {
  query: string;
  top_k: number;
}

// Image search request
export interface ImageSearchRequest {
  image_url: string;
  top_k: number;
}

// Video search request
export interface VideoSearchRequest {
  video_url: string;
  top_k: number;
}

// Multimodal search request
export interface MultimodalSearchRequest {
  text?: string;
  image_url?: string;
  video_url?: string;
  top_k: number;
}

// Service status
export interface ServiceStatus {
  initialized: boolean;
  mm_extractor: boolean;
  search_engine: boolean;
  search_engine_connected: boolean;
}

// Status response
export interface StatusResponse {
  success: boolean;
  message: string;
  status: ServiceStatus;
}

// Health check response
export interface HealthResponse {
  status: string;
  timestamp: string;
}

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  token?: string;
  user_info?: {
    username: string;
    role: string;
    login_time: string;
  };
}

export interface UserInfo {
  username: string;
  role: string;
} 