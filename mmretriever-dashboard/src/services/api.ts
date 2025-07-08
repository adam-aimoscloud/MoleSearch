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

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
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

// API服务类
export class ApiService {
  // 健康检查
  static async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/health');
    return response.data;
  }

  // 获取服务状态
  static async getStatus(): Promise<StatusResponse> {
    const response = await api.get('/status');
    return response.data;
  }

  // 文本搜索
  static async searchText(request: TextSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/text', request);
    return response.data;
  }

  // 图像搜索
  static async searchImage(request: ImageSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/image', request);
    return response.data;
  }

  // 视频搜索
  static async searchVideo(request: VideoSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/video', request);
    return response.data;
  }

  // 多模态搜索
  static async searchMultimodal(request: MultimodalSearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search/multimodal', request);
    return response.data;
  }

  // 插入单条数据
  static async insertData(request: InsertDataRequest): Promise<InsertResponse> {
    const response = await api.post('/data/insert', request);
    return response.data;
  }

  // 批量插入数据
  static async batchInsertData(request: BatchInsertRequest): Promise<InsertResponse> {
    const response = await api.post('/data/batch_insert', request);
    return response.data;
  }

  // 全量数据查询
  static async listData(request: DataListRequest): Promise<DataListResponse> {
    const response = await api.post('/data/list', request);
    return response.data;
  }
}

export default api; 