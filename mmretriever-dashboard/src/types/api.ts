// API响应类型定义
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

// 搜索结果项
export interface SearchResultItem {
  id: string;
  text: string;
  image_url: string;
  video_url: string;
  score: number;
}

// 搜索响应
export interface SearchResponse {
  success: boolean;
  message: string;
  total: number;
  results: SearchResultItem[];
  query_time: number;
}

// 插入响应
export interface InsertResponse {
  success: boolean;
  message: string;
  inserted_count?: number;
  processing_time?: number;
}

// 批量插入请求
export interface BatchInsertRequest {
  data: InsertDataRequest[];
}

// 插入数据请求
export interface InsertDataRequest {
  text: string;
  image_url: string;
  video_url: string;
}

// 文本搜索请求
export interface TextSearchRequest {
  query: string;
  top_k: number;
}

// 图像搜索请求
export interface ImageSearchRequest {
  image_url: string;
  top_k: number;
}

// 视频搜索请求
export interface VideoSearchRequest {
  video_url: string;
  top_k: number;
}

// 多模态搜索请求
export interface MultimodalSearchRequest {
  text?: string;
  image_url?: string;
  video_url?: string;
  top_k: number;
}

// 服务状态
export interface ServiceStatus {
  initialized: boolean;
  mm_extractor: boolean;
  search_engine: boolean;
  search_engine_connected: boolean;
}

// 状态响应
export interface StatusResponse {
  success: boolean;
  message: string;
  status: ServiceStatus;
}

// 健康检查响应
export interface HealthResponse {
  status: string;
  timestamp: string;
} 