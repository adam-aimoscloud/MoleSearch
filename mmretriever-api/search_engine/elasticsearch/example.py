#!/usr/bin/env python3
"""
Elasticsearch搜索引擎使用示例
支持文本搜索、文本embedding搜索、图片embedding搜索和视频embedding搜索
"""

from es import ESSearchEngine
from ..base import SearchInput, SearchOutput, InsertData, EmbeddingInfo


def example_usage():
    """ES搜索引擎使用示例"""
    
    # 1. 初始化ES搜索引擎
    es_param = {
        "host": "localhost",
        "port": 9200,
        "index": "mmretriever_demo",
        "username": "",  # 如果ES需要认证
        "password": ""   # 如果ES需要认证
    }
    
    search_engine = ESSearchEngine(es_param)
    
    # 2. 插入示例数据
    print("插入示例数据...")
    
    # 插入包含文本和各种embedding的数据
    data1 = InsertData(
        text="这是一段关于机器学习的文本内容",
        image="/path/to/image1.jpg",
        video="/path/to/video1.mp4",
        embeddings=[
            EmbeddingInfo(label="text_embedding", embedding=[0.1] * 1024),
            EmbeddingInfo(label="image_embedding", embedding=[0.2] * 1024),
            EmbeddingInfo(label="video_embedding", embedding=[0.3] * 1024)
        ]
    )
    
    data2 = InsertData(
        text="深度学习是人工智能的重要分支",
        image="/path/to/image2.jpg", 
        video="/path/to/video2.mp4",
        embeddings=[
            EmbeddingInfo(label="text_embedding", embedding=[0.4] * 1024),
            EmbeddingInfo(label="image_embedding", embedding=[0.5] * 1024),
            EmbeddingInfo(label="video_embedding", embedding=[0.6] * 1024)
        ]
    )
    
    # 单条插入
    search_engine.insert(data1)
    search_engine.insert(data2)
    
    # 批量插入
    batch_data = [data1, data2]
    search_engine.batch_insert(batch_data)
    
    # 3. 执行搜索
    print("\n执行搜索测试...")
    
    # 文本搜索
    print("1. 文本搜索:")
    text_search = SearchInput(
        text="机器学习",
        topk=5
    )
    results = search_engine.search(text_search)
    print(f"找到 {len(results.items)} 个结果")
    for i, item in enumerate(results.items):
        print(f"  结果{i+1}: {item.text[:50]}... (得分: {item.score:.3f})")
    
    # 文本embedding搜索
    print("\n2. 文本embedding搜索:")
    text_embedding_search = SearchInput(
        embeddings=[
            EmbeddingInfo(label="text_embedding", embedding=[0.1] * 1024)
        ],
        topk=5
    )
    results = search_engine.search(text_embedding_search)
    print(f"找到 {len(results.items)} 个结果")
    for i, item in enumerate(results.items):
        print(f"  结果{i+1}: {item.text[:50]}... (得分: {item.score:.3f})")
    
    # 图片embedding搜索
    print("\n3. 图片embedding搜索:")
    image_embedding_search = SearchInput(
        embeddings=[
            EmbeddingInfo(label="image_embedding", embedding=[0.2] * 1024)
        ],
        topk=5
    )
    results = search_engine.search(image_embedding_search)
    print(f"找到 {len(results.items)} 个结果")
    for i, item in enumerate(results.items):
        print(f"  结果{i+1}: 图片={item.image} (得分: {item.score:.3f})")
    
    # 视频embedding搜索
    print("\n4. 视频embedding搜索:")
    video_embedding_search = SearchInput(
        embeddings=[
            EmbeddingInfo(label="video_embedding", embedding=[0.3] * 1024)
        ],
        topk=5
    )
    results = search_engine.search(video_embedding_search)
    print(f"找到 {len(results.items)} 个结果")
    for i, item in enumerate(results.items):
        print(f"  结果{i+1}: 视频={item.video} (得分: {item.score:.3f})")
    
    # 混合搜索（文本 + embedding）
    print("\n5. 混合搜索 (文本 + embedding):")
    hybrid_search = SearchInput(
        text="人工智能",
        embeddings=[
            EmbeddingInfo(label="text_embedding", embedding=[0.4] * 1024),
            EmbeddingInfo(label="image_embedding", embedding=[0.5] * 1024)
        ],
        topk=5
    )
    results = search_engine.search(hybrid_search)
    print(f"找到 {len(results.items)} 个结果")
    for i, item in enumerate(results.items):
        print(f"  结果{i+1}: {item.text[:50]}... (得分: {item.score:.3f})")


def cleanup_example():
    """清理示例数据"""
    es_param = {
        "host": "localhost",
        "port": 9200,
        "index": "mmretriever_demo"
    }
    
    search_engine = ESSearchEngine(es_param)
    search_engine.delete_all()
    print("已清理所有示例数据")


if __name__ == "__main__":
    print("ES搜索引擎功能演示")
    print("=" * 50)
    
    try:
        example_usage()
        print("\n演示完成！")
        
        # 可选：清理数据
        # cleanup_example()
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        print("请确保Elasticsearch服务正在运行，并且配置正确") 