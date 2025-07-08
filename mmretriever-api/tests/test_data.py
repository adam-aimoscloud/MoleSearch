"""
Test data file
Contains embedding vector data for ES search engine tests
"""
import random
from typing import List

# Set random seed to ensure test reproducibility
random.seed(42)

def generate_embedding(dims: int = 1024) -> List[float]:
    """Generate random embedding vector of specified dimension"""
    return [random.uniform(-1.0, 1.0) for _ in range(dims)]

def generate_similar_embedding(base_embedding: List[float], similarity: float = 0.8) -> List[float]:
    """Generate similar embedding vector to the base embedding"""
    result = []
    for val in base_embedding:
        # Add small random noise to maintain similarity
        noise = random.uniform(-0.2, 0.2) * (1 - similarity)
        result.append(val + noise)
    return result

# Base embedding vector
BASE_TEXT_EMBEDDING = generate_embedding(1024)
BASE_IMAGE_EMBEDDING = generate_embedding(1024)
BASE_VIDEO_EMBEDDING = generate_embedding(1024)

# Test data set
TEST_DATA = [
    {
        "text": "Machine learning is an important branch of artificial intelligence",
        "image": "/test/images/ml_concept.jpg",
        "video": "/test/videos/ml_intro.mp4",
        "text_embedding": BASE_TEXT_EMBEDDING,
        "image_embedding": BASE_IMAGE_EMBEDDING,
        "video_embedding": BASE_VIDEO_EMBEDDING
    },
    {
        "text": "Deep learning simulates the learning process of the human brain through neural networks",
        "image": "/test/images/deep_learning.jpg",
        "video": "/test/videos/neural_network.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.9),
        "image_embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.85),
        "video_embedding": generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.8)
    },
    {
        "text": "Natural language processing is a field of computer science",
        "image": "/test/images/nlp_diagram.jpg",
        "video": "/test/videos/nlp_overview.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.7),
        "image_embedding": generate_embedding(1024),  # dissimilar image embedding
        "video_embedding": generate_embedding(1024)   # dissimilar video embedding
    },
    {
        "text": "Computer vision enables machines to recognize and understand images",
        "image": "/test/images/computer_vision.jpg",
        "video": "/test/videos/cv_applications.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.6),
        "image_embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.9),
        "video_embedding": generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.85)
    },
    {
        "text": "Reinforcement learning trains agents through reward mechanisms",
        "image": "/test/images/reinforcement_learning.jpg",
        "video": "/test/videos/rl_demo.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.5),
        "image_embedding": generate_embedding(1024),
        "video_embedding": generate_embedding(1024)
    }
]

# Search test cases
SEARCH_TEST_CASES = [
    {
        "name": "Text search - exact match",
        "search_input": {
            "text": "Machine learning",
            "embeddings": [],
            "topk": 3
        },
        "expected_min_results": 1
    },
    {
        "name": "Text search - related words",
        "search_input": {
            "text": "Artificial intelligence",
            "embeddings": [],
            "topk": 5
        },
        "expected_min_results": 1
    },
    {
        "name": "Text embedding search - similar vector",
        "search_input": {
            "text": "",
            "embeddings": [
                {
                    "label": "text_embedding",
                    "embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.95)
                }
            ],
            "topk": 3
        },
        "expected_min_results": 1
    },
    {
        "name": "图片embedding搜索 - 相似向量",
        "search_input": {
            "text": "",
            "embeddings": [
                {
                    "label": "image_embedding",
                    "embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.95)
                }
            ],
            "topk": 3
        },
        "expected_min_results": 1
    },
    {
        "name": "Video embedding search - similar vector",
        "search_input": {
            "text": "",
            "embeddings": [
                {
                    "label": "video_embedding",
                    "embedding": generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.95)
                }
            ],
            "topk": 3
        },
        "expected_min_results": 1
    },
    {
        "name": "Hybrid search - text + embedding",
        "search_input": {
            "text": "Deep learning",
            "embeddings": [
                {
                    "label": "text_embedding",
                    "embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.8)
                },
                {
                    "label": "image_embedding",
                    "embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.8)
                }
            ],
            "topk": 5
        },
        "expected_min_results": 1
    },
    {
        "name": "Multimodal embedding search",
        "search_input": {
            "text": "",
            "embeddings": [
                {
                    "label": "text_embedding",
                    "embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.9)
                },
                {
                    "label": "image_embedding",
                    "embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.9)
                },
                {
                    "label": "video_embedding",
                    "embedding": generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.9)
                }
            ],
            "topk": 3
        },
        "expected_min_results": 1
    }
]

# Test data for different embedding labels
EMBEDDING_LABEL_TEST_CASES = [
    ("text_embedding", "text_embedding"),
    ("tembed", "text_embedding"),
    ("text", "text_embedding"),
    ("image_embedding", "image_embedding"),
    ("iembed", "image_embedding"),
    ("image", "image_embedding"),
    ("img", "image_embedding"),
    ("video_embedding", "video_embedding"),
    ("vembed", "video_embedding"),
    ("video", "video_embedding"),
    ("vid", "video_embedding"),
    ("unknown_label", "text_embedding")  # Default mapped to text_embedding
] 