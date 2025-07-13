# MoleSearch

A multimodal search engine that supports text, image, and video content search with vector embeddings.

## Features

- **Multimodal Search**: Search across text, image, and video content
- **Vector Embeddings**: Advanced semantic search using embeddings
- **Elasticsearch Backend**: Scalable and fast search engine
- **Modern Web UI**: React-based dashboard with real-time search
- **Async Architecture**: High-performance async/await implementation
- **Async Data Insertion**: Background task processing for data insertion

## Demo

🌐 **Live Demo**: [https://molesearch.aimos.cloud/login](https://molesearch.aimos.cloud/login)

### Demo Account

For testing purposes, you can use the following demo account:

- **Username**: `molesearch`
- **Password**: `MoleSearch2025`

## Project Structure

```
MoleSearch/
├── api/                    # Backend API (FastAPI + Elasticsearch)
│   ├── handlers/          # API handlers
│   ├── search_engine/     # Search engine implementations
│   ├── processor/         # Data processing pipelines
│   ├── workers/           # Async task workers
│   ├── utils/             # Utility modules
│   └── tests/            # Backend tests
├── dashboard/             # Frontend React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── services/     # API services
│   └── public/           # Static assets
```

## Quick Start

### Backend (API)

```bash
cd api
pip install -r requirements.txt

# Start API server only
bash start.sh

# Start API server with async worker
bash start_with_worker.sh

# Start worker only
bash start.sh worker
```

### Frontend (Dashboard)

```bash
cd dashboard
npm install
npm start
```

## Async Data Insertion

Due to the time-consuming nature of embedding extraction, data insertion has been converted to asynchronous processing:

### Features
- **Fast Response**: API returns task ID immediately
- **Progress Tracking**: Monitor task status and progress
- **Batch Support**: Single and batch data insertion
- **Background Processing**: Non-blocking data processing

### API Endpoints
- `POST /api/v1/data/async_insert` - Async single data insertion
- `POST /api/v1/data/async_batch_insert` - Async batch data insertion  
- `GET /api/v1/tasks/{task_id}/status` - Query task status

### Usage Example
```python
import requests

# Create async insertion task
response = requests.post(
    "http://localhost:8000/api/v1/data/async_insert",
    json={
        "text": "Document content",
        "image_url": "https://example.com/image.jpg",
        "video_url": "https://example.com/video.mp4"
    }
)

task_id = response.json()['task_id']

# Monitor task status
status_response = requests.get(
    f"http://localhost:8000/api/v1/tasks/{task_id}/status"
)
```

For detailed documentation, see [ASYNC_INSERTION.md](api/ASYNC_INSERTION.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 