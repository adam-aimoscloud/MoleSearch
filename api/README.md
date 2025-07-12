# MoleRetriever API

A FastAPI interface for multimodal retrieval, supporting search and data insertion for text, images, and videos.

## ✨ Features

- 🔍 **Multimodal Search**: Supports search for text, images, and videos
- 📊 **Vectorized Retrieval**: Uses MMExtractor for data vectorization
- 🧩 **Plugin Architecture**: ASR, text/image/video/multimodal embedding, and VLM support multiple plugins, easy to extend
- 🚦 **Health Check Endpoint**: /health endpoint for service health monitoring
- 🚀 **High Performance**: High-performance search based on FastAPI and Elasticsearch
- 📝 **Complete Documentation**: Automatically generated API documentation
- 🔧 **Easy Deployment**: Docker support and simple environment configuration

## 🛠️ Installation

### 1. Requirements

- Python 3.8+
- Elasticsearch 8.x

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example configuration file and modify it as needed:
、、、bash
copy config.template.yaml config.yaml
vim config.yaml
```

## 🚀 Start the Service

### Using Shell Scripts (Recommended)

```bash
bash start.sh
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

## 📚 API Documentation

After starting the service, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ TODO

1. **PostgreSQL support for search engine**  
   Extend the current search engine backend to support PostgreSQL, improving flexibility and scalability for data storage and retrieval.

2. **Add asynchronous data ingestion API**  
   Provide asynchronous data ingestion API endpoints to enable efficient bulk data writing and improve system throughput.

3. **Support more embedding models in processor**  
   Continuously integrate and adapt more mainstream embedding models to meet diverse multimodal retrieval requirements.


## 📄 License

This project is licensed under the Apache License 2.0. See the LICENSE file for details. 