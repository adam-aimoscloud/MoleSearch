# MMRetriever API

多模态检索系统 FastAPI 接口，支持文本、图像、视频的搜索和数据插入。

## ✨ 特性

- 🔍 **多模态搜索**：支持文本、图像、视频三种格式的搜索
- 📊 **向量化检索**：使用 MMExtractor 进行数据向量化
- 🧩 **插件化架构**：ASR、文本/图像/视频/多模态嵌入、VLM 支持多种插件，易于扩展
- 🔄 **配置热重载**：支持 config.yaml 动态加载和热更新
- 🚦 **健康检查接口**：/health 端点用于服务健康监控
- 🚀 **高性能**：基于 FastAPI 和 Elasticsearch 的高性能搜索
- 📝 **完整文档**：自动生成的 API 文档
- 🔧 **易于部署**：Docker 支持和简单的环境配置

## 🛠️ 安装

### 1. 环境要求

- Python 3.8+
- Elasticsearch 8.x
- 通义千问 API Key（DASHSCOPE_API_KEY）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境配置

```bash
# 必需的环境变量
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# 可选的环境变量
export ES_HOST="localhost"
export ES_PORT="9200"
export ES_INDEX="mmretriever"
export ES_SCHEME="http"
export HOST="0.0.0.0"
export PORT="8000"
```

## 🚀 启动服务

### 方式1：使用启动脚本

```bash
python start_server.py
```

### 方式2：直接启动

```bash
python main.py
```

### 方式3：使用 uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API 接口

### 基础接口

- `GET /` - 根路径检查
- `GET /health` - 健康检查
- `GET /api/v1/status` - 服务状态

### 搜索接口

#### 文本搜索
```bash
POST /api/v1/search/text
```

请求体：
```json
{
  "query": "人工智能技术发展",
  "top_k": 10
}
```

#### 图像搜索
```bash
POST /api/v1/search/image
```

请求体：
```json
{
  "image_url": "https://example.com/image.jpg",
  "top_k": 10
}
```

#### 视频搜索
```bash
POST /api/v1/search/video
```

请求体：
```json
{
  "video_url": "https://example.com/video.mp4",
  "top_k": 10
}
```

#### 多模态搜索
```bash
POST /api/v1/search/multimodal
```

请求体：
```json
{
  "text": "人工智能",
  "image_url": "https://example.com/image.jpg",
  "video_url": "https://example.com/video.mp4",
  "top_k": 10
}
```

### 数据插入接口

#### 单条数据插入
```bash
POST /api/v1/data/insert
```

请求体：
```json
{
  "text": "这是一段文本",
  "image_url": "https://example.com/image.jpg",
  "video_url": "https://example.com/video.mp4"
}
```

#### 批量数据插入
```bash
POST /api/v1/data/batch_insert
```

请求体：
```json
{
  "data_list": [
    {
      "text": "文本1",
      "image_url": "https://example.com/image1.jpg",
      "video_url": "https://example.com/video1.mp4"
    },
    {
      "text": "文本2",
      "image_url": "https://example.com/image2.jpg",
      "video_url": "https://example.com/video2.mp4"
    }
  ]
}
```

## 📝 使用示例

### Python 客户端

```python
import requests

# 创建客户端
client = requests.Session()
base_url = "http://localhost:8000"

# 文本搜索
response = client.post(
    f"{base_url}/api/v1/search/text",
    json={"query": "人工智能", "top_k": 5}
)
result = response.json()
print(result)

# 多模态搜索
response = client.post(
    f"{base_url}/api/v1/search/multimodal",
    json={
        "text": "深度学习",
        "image_url": "https://example.com/ai.jpg",
        "top_k": 5
    }
)
result = response.json()
print(result)
```

### 使用提供的示例脚本

```bash
python examples/api_examples.py
```

## 🔧 配置文件

系统会自动创建默认配置文件 `tests/mm_extractor_config.yaml`：

```yaml
# MMExtractor Configuration
asr_plugin:
  type: "aliyun"
  param:
    api_key: ""
    app_key: ""
    audio_prefix: "audio_"

text_embedding_plugin:
  type: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model_name: "text-embedding-v1"

image_embedding_plugin:
  type: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model_name: "multimodal-embedding-one-peace-v1"

video_embedding_plugin:
  type: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model_name: "multimodal-embedding-one-peace-v1"

vlm_plugin:
  type: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model_name: "qwen-vl-max"
    max_tokens: 1000
    temperature: 0.1
    top_p: 0.8
```

## 📚 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛡️ 错误处理

API 使用标准的 HTTP 状态码：

- `200` - 成功
- `422` - 请求参数错误
- `500` - 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述"
}
```

## 🧪 测试

### 启动 Elasticsearch

```bash
# 使用 Docker
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  elasticsearch:8.15.0
```

### 运行测试

```bash
# 运行 API 示例
python examples/api_examples.py

# 或者使用 curl 测试
curl -X GET http://localhost:8000/health
```

## 📈 性能优化

1. **Elasticsearch 配置**：
   - 调整 JVM 堆内存大小
   - 配置合适的分片和副本数量
   - 使用 SSD 存储

2. **API 服务配置**：
   - 使用多进程部署（gunicorn）
   - 配置连接池和缓存
   - 启用压缩传输

3. **向量化优化**：
   - 批量处理数据
   - 使用异步处理
   - 缓存常用向量

## 🔒 安全建议

1. **API Key 管理**：
   - 使用环境变量存储敏感信息
   - 定期轮换 API Key
   - 限制 API 访问权限

2. **网络安全**：
   - 使用 HTTPS 部署
   - 配置防火墙规则
   - 启用请求限流

3. **数据安全**：
   - 验证输入数据
   - 过滤恶意内容
   - 记录操作日志

## 📞 支持

如果遇到问题，请检查：

1. 环境变量是否正确配置
2. Elasticsearch 是否正常运行
3. 网络连接是否正常
4. API Key 是否有效

## 🚀 部署建议

### 开发环境
```bash
python start_server.py
```

### 生产环境
```bash
# 使用 gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用 Docker
docker build -t mmretriever-api .
docker run -p 8000:8000 mmretriever-api
```

## 📄 许可证

本项目采用 Apache License 2.0 许可证，详见 LICENSE 文件。 