# MoleSearch

A multimodal search engine that supports text, image, and video content search with vector embeddings.

## Features

- **Multimodal Search**: Search across text, image, and video content
- **Vector Embeddings**: Advanced semantic search using embeddings
- **Elasticsearch Backend**: Scalable and fast search engine
- **Modern Web UI**: React-based dashboard with real-time search
- **Async Architecture**: High-performance async/await implementation

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
python main.py
```

### Frontend (Dashboard)

```bash
cd dashboard
npm install
npm start
```

### Elasticsearch

```bash
# Using Docker
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.12.2
```

## Testing

```bash
cd api
python tests/es_test.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 