"""
测试数据文件
包含用于ES搜索引擎测试的embedding向量数据
"""
import random
from typing import List

# 设置随机种子以确保测试的可重复性
random.seed(42)

def generate_embedding(dims: int = 1024) -> List[float]:
    """生成指定维度的随机embedding向量"""
    return [random.uniform(-1.0, 1.0) for _ in range(dims)]

def generate_similar_embedding(base_embedding: List[float], similarity: float = 0.8) -> List[float]:
    """生成与基础embedding相似的向量"""
    result = []
    for val in base_embedding:
        # 添加小的随机噪声，保持相似性
        noise = random.uniform(-0.2, 0.2) * (1 - similarity)
        result.append(val + noise)
    return result

# 基础embedding向量
BASE_TEXT_EMBEDDING = generate_embedding(1024)
BASE_IMAGE_EMBEDDING = generate_embedding(1024)
BASE_VIDEO_EMBEDDING = generate_embedding(1024)

# 测试数据集
TEST_DATA = [
    {
        "text": "机器学习是人工智能的一个重要分支",
        "image": "/test/images/ml_concept.jpg",
        "video": "/test/videos/ml_intro.mp4",
        "text_embedding": BASE_TEXT_EMBEDDING,
        "image_embedding": BASE_IMAGE_EMBEDDING,
        "video_embedding": BASE_VIDEO_EMBEDDING
    },
    {
        "text": "深度学习通过神经网络模拟人脑的学习过程",
        "image": "/test/images/deep_learning.jpg",
        "video": "/test/videos/neural_network.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.9),
        "image_embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.85),
        "video_embedding": generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.8)
    },
    {
        "text": "自然语言处理是计算机科学的一个领域",
        "image": "/test/images/nlp_diagram.jpg",
        "video": "/test/videos/nlp_overview.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.7),
        "image_embedding": generate_embedding(1024),  # 不相似的图片embedding
        "video_embedding": generate_embedding(1024)   # 不相似的视频embedding
    },
    {
        "text": "计算机视觉让机器能够识别和理解图像",
        "image": "/test/images/computer_vision.jpg",
        "video": "/test/videos/cv_applications.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.6),
        "image_embedding": generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.9),
        "video_embedding": generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.85)
    },
    {
        "text": "强化学习通过奖励机制训练智能体",
        "image": "/test/images/reinforcement_learning.jpg",
        "video": "/test/videos/rl_demo.mp4",
        "text_embedding": generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.5),
        "image_embedding": generate_embedding(1024),
        "video_embedding": generate_embedding(1024)
    }
]

# 搜索测试用例
SEARCH_TEST_CASES = [
    {
        "name": "文本搜索 - 精确匹配",
        "search_input": {
            "text": "机器学习",
            "embeddings": [],
            "topk": 3
        },
        "expected_min_results": 1
    },
    {
        "name": "文本搜索 - 相关词汇",
        "search_input": {
            "text": "人工智能",
            "embeddings": [],
            "topk": 5
        },
        "expected_min_results": 1
    },
    {
        "name": "文本embedding搜索 - 相似向量",
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
        "name": "视频embedding搜索 - 相似向量",
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
        "name": "混合搜索 - 文本+embedding",
        "search_input": {
            "text": "深度学习",
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
        "name": "多模态embedding搜索",
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

# 不同embedding标签的测试数据
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
    ("unknown_label", "text_embedding")  # 默认映射到text_embedding
] 