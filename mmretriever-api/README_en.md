# MMRetriever API

A FastAPI interface for multimodal retrieval, supporting search and data insertion for text, images, and videos.

## ✨ Features

- 🔍 **Multimodal Search**: Supports search for text, images, and videos
- 📊 **Vectorized Retrieval**: Uses MMExtractor for data vectorization
- 🧩 **Plugin Architecture**: ASR, text/image/video/multimodal embedding, and VLM support multiple plugins, easy to extend
- 🔄 **Hot Configuration Reload**: Supports dynamic loading and hot update of config.yaml
- 🚦 **Health Check Endpoint**: /health endpoint for service health monitoring
- 🚀 **High Performance**: High-performance search based on FastAPI and Elasticsearch
- 📝 **Complete Documentation**: Automatically generated API documentation
- 🔧 **Easy Deployment**: Docker support and simple environment configuration

## 🛠️ Installation

### 1. Requirements

- Python 3.8+
- Elasticsearch 8.x
- DashScope API Key (`DASHSCOPE_API_KEY`)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Required environment variables
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# Optional environment variables
export ES_HOST="localhost"
export ES_PORT="9200"
export ES_INDEX="mmretriever"
export ES_SCHEME="http"
export HOST="0.0.0.0"
export PORT="8000"
```

## 🚀 Start the Service

### Method 1: Use the Startup Script

```bash
python start_server.py
```

### Method 2: Start Directly

```bash
python main.py
```

### Method 3: Use uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API Endpoints

### Basic Endpoints

- `GET /` - Root path check
- `GET /health` - Health check
- `GET /api/v1/status` - Service status

### Search Endpoints

#### Text Search
```bash
POST /api/v1/search/text
```

Request body:
```json
{
  "query": "Development of AI technology",
  "top_k": 10
}
```

#### Image Search
```bash
POST /api/v1/search/image
```

Request body:
```json
{
  "image_url": "https://example.com/image.jpg",
  "top_k": 10
}
```

#### Video Search
```bash
POST /api/v1/search/video
```

Request body:
```json
{
  "video_url": "https://example.com/video.mp4",
  "top_k": 10
}
```

#### Multimodal Search
```bash
POST /api/v1/search/multimodal
```

Request body:
```json
{
  "text": "Artificial Intelligence",
  "image_url": "https://example.com/image.jpg",
  "video_url": "https://example.com/video.mp4",
  "top_k": 10
}
```

### Data Insertion Endpoints

#### Single Data Insertion
```bash
POST /api/v1/data/insert
```

Request body:
```json
{
  "text": "This is a piece of text",
  "image_url": "https://example.com/image.jpg",
  "video_url": "https://example.com/video.mp4"
}
```

#### Batch Data Insertion
```bash
POST /api/v1/data/batch_insert
```

Request body:
```json
{
  "data_list": [
    {
      "text": "Text 1",
      "image_url": "https://example.com/image1.jpg",
      "video_url": "https://example.com/video1.mp4"
    },
    {
      "text": "Text 2",
      "image_url": "https://example.com/image2.jpg",
      "video_url": "https://example.com/video2.mp4"
    }
  ]
}
```

## 📝 Usage Examples

### Python Client

```python
import requests

# Create client
client = requests.Session()
base_url = "http://localhost:8000"

# Text search
response = client.post(
    f"{base_url}/api/v1/search/text",
    json={"query": "Artificial Intelligence", "top_k": 5}
)
result = response.json()
print(result)

# Multimodal search
response = client.post(
    f"{base_url}/api/v1/search/multimodal",
    json={
        "text": "Deep Learning",
        "image_url": "https://example.com/ai.jpg",
        "top_k": 5
    }
)
result = response.json()
print(result)
```

### Use the Provided Example Script

```bash
python examples/api_examples.py
```

## 🔧 Configuration File

The system will automatically create a default configuration file `tests/mm_extractor_config.yaml`:

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

## 📚 API Documentation

After starting the service, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛡️ Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `422` - Request parameter error
- `500` - Internal server error

Error response format:
```json
{
  "detail": "Error description"
}
```

## 🧪 Testing

### Start Elasticsearch

```bash
# Using Docker
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  elasticsearch:8.15.0
```

### Run Tests

```bash
# Run API example
python examples/api_examples.py

# Or use curl to test
curl -X GET http://localhost:8000/health
```

## 📈 Performance Optimization

1. **Elasticsearch Configuration**:
   - Adjust JVM heap size
   - Configure appropriate number of shards and replicas
   - Use SSD storage

2. **API Service Configuration**:
   - Deploy with multiple processes (gunicorn)
   - Configure connection pools and caching
   - Enable compressed transmission

3. **Vectorization Optimization**:
   - Batch process data
   - Use asynchronous processing
   - Cache frequently used vectors

## 🔒 Security Recommendations

1. **API Key Management**:
   - Store sensitive information in environment variables
   - Rotate API keys regularly
   - Restrict API access permissions

2. **Network Security**:
   - Deploy with HTTPS
   - Configure firewall rules
   - Enable request rate limiting

3. **Data Security**:
   - Validate input data
   - Filter malicious content
   - Log operations

## 📞 Support

If you encounter problems, please check:

1. Whether environment variables are configured correctly
2. Whether Elasticsearch is running properly
3. Whether the network connection is normal
4. Whether the API key is valid

## 🚀 Deployment Recommendations

### Development Environment
```bash
python start_server.py
```

### Production Environment
```bash
# Use gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use Docker
docker build -t mmretriever-api .
docker run -p 8000:8000 mmretriever-api
```

## 📄 License

This project is licensed under the Apache License 2.0. See the LICENSE file for details. 