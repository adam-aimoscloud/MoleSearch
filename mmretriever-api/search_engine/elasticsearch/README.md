# Elasticsearch搜索引擎

基于Elasticsearch实现的多模态检索引擎，支持文本搜索和多种embedding向量搜索。

## 功能特性

### 支持的搜索类型

1. **文本搜索** - 基于Elasticsearch的全文检索功能
2. **文本embedding搜索** - 基于文本向量的语义相似度搜索  
3. **图片embedding搜索** - 基于图片特征向量的相似度搜索
4. **视频embedding搜索** - 基于视频特征向量的相似度搜索
5. **混合搜索** - 支持文本和多种embedding的组合搜索

### 核心功能

- **自动索引管理** - 自动创建和配置Elasticsearch索引
- **向量相似度搜索** - 使用余弦相似度进行向量搜索
- **批量数据操作** - 支持单条和批量数据插入
- **灵活的配置** - 支持认证、自定义端口等配置
- **错误处理** - 完善的异常处理机制

## 安装依赖

```bash
pip install elasticsearch>=8.0.0
```

## 配置参数

### ESParam配置类

```python
@dataclass
class ESParam:
    host: str = 'localhost'          # ES服务器地址
    port: int = 9200                 # ES服务器端口  
    index: str = 'mmretriever'       # 索引名称
    username: str = ''               # 用户名(可选)
    password: str = ''               # 密码(可选)
```

## 数据结构

### 输入数据结构

```python
# 搜索输入
SearchInput(
    text="搜索文本",                 # 可选的文本查询
    embeddings=[                     # 可选的embedding列表
        EmbeddingInfo(
            label="text_embedding",  # embedding类型标签
            embedding=[...]          # 向量数据
        )
    ],
    topk=10                          # 返回结果数量
)

# 插入数据
InsertData(
    text="文本内容",
    image="/path/to/image.jpg",      # 图片路径
    video="/path/to/video.mp4",      # 视频路径
    embeddings=[                     # embedding向量列表
        EmbeddingInfo(label="text_embedding", embedding=[...]),
        EmbeddingInfo(label="image_embedding", embedding=[...]),
        EmbeddingInfo(label="video_embedding", embedding=[...])
    ]
)
```

### 输出数据结构

```python
SearchOutput(
    items=[
        SearchOutputItem(
            text="匹配的文本内容",
            image="/path/to/image.jpg",
            video="/path/to/video.mp4", 
            score=0.95                   # 相似度得分
        )
    ]
)
```

## 使用方法

### 1. 初始化搜索引擎

```python
from mmretriever.search_engine.elasticsearch.es import ESSearchEngine

# 配置参数
es_param = {
    "host": "localhost",
    "port": 9200,
    "index": "mmretriever_index",
    "username": "",  # 如果需要认证
    "password": ""   # 如果需要认证
}

# 创建搜索引擎实例
search_engine = ESSearchEngine(es_param)
```

### 2. 插入数据

```python
from mmretriever.search_engine.base import InsertData, EmbeddingInfo

# 准备数据
data = InsertData(
    text="这是一段关于机器学习的文本",
    image="/path/to/ml_image.jpg",
    video="/path/to/ml_video.mp4",
    embeddings=[
        EmbeddingInfo(label="text_embedding", embedding=[0.1, 0.2, ...]),
        EmbeddingInfo(label="image_embedding", embedding=[0.3, 0.4, ...]),
        EmbeddingInfo(label="video_embedding", embedding=[0.5, 0.6, ...])
    ]
)

# 单条插入
search_engine.insert(data)

# 批量插入
batch_data = [data1, data2, data3]
search_engine.batch_insert(batch_data)
```

### 3. 执行搜索

#### 文本搜索

```python
from mmretriever.search_engine.base import SearchInput

search_input = SearchInput(
    text="机器学习算法",
    topk=5
)
results = search_engine.search(search_input)
```

#### Embedding向量搜索

```python
# 文本embedding搜索
search_input = SearchInput(
    embeddings=[
        EmbeddingInfo(label="text_embedding", embedding=[0.1, 0.2, ...])
    ],
    topk=5
)
results = search_engine.search(search_input)

# 图片embedding搜索  
search_input = SearchInput(
    embeddings=[
        EmbeddingInfo(label="image_embedding", embedding=[0.3, 0.4, ...])
    ],
    topk=5
)
results = search_engine.search(search_input)

# 视频embedding搜索
search_input = SearchInput(
    embeddings=[
        EmbeddingInfo(label="video_embedding", embedding=[0.5, 0.6, ...])
    ],
    topk=5
)
results = search_engine.search(search_input)
```

#### 混合搜索

```python
# 文本 + 多种embedding组合搜索
search_input = SearchInput(
    text="人工智能",
    embeddings=[
        EmbeddingInfo(label="text_embedding", embedding=[0.1, 0.2, ...]),
        EmbeddingInfo(label="image_embedding", embedding=[0.3, 0.4, ...])
    ],
    topk=10
)
results = search_engine.search(search_input)
```

### 4. 处理搜索结果

```python
for item in results.items:
    print(f"文本: {item.text}")
    print(f"图片: {item.image}")
    print(f"视频: {item.video}")
    print(f"得分: {item.score}")
    print("-" * 50)
```

## Embedding标签映射

系统会根据embedding的标签自动映射到对应的向量字段：

| 标签关键词 | 映射字段 | 说明 |
|-----------|----------|------|
| text, tembed | text_embedding | 文本向量字段 |
| image, img, iembed | image_embedding | 图片向量字段 |
| video, vid, vembed | video_embedding | 视频向量字段 |

## 索引配置

搜索引擎会自动创建具有以下结构的Elasticsearch索引：

```json
{
  "mappings": {
    "properties": {
      "text": {
        "type": "text",
        "analyzer": "standard"
      },
      "image": {
        "type": "keyword"
      },
      "video": {
        "type": "keyword" 
      },
      "text_embedding": {
        "type": "dense_vector",
        "dims": 1024,
        "index": true,
        "similarity": "cosine"
      },
      "image_embedding": {
        "type": "dense_vector", 
        "dims": 1024,
        "index": true,
        "similarity": "cosine"
      },
      "video_embedding": {
        "type": "dense_vector",
        "dims": 1024, 
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

## 性能优化建议

1. **批量操作** - 使用`batch_insert()`进行批量数据插入
2. **向量维度** - 根据实际embedding维度调整索引配置
3. **分片配置** - 根据数据量合理配置ES分片数量
4. **内存设置** - 为ES分配足够的堆内存用于向量搜索

## 注意事项

1. 确保Elasticsearch服务正在运行
2. 向量维度需要与索引配置一致（默认1024维）
3. 大量数据插入时建议使用批量操作
4. 搜索结果按相似度得分降序排列

## 错误处理

搜索引擎包含完善的错误处理机制：

- 连接失败时会抛出相应异常
- 搜索失败时返回空结果列表
- 插入失败时会抛出异常并提供错误信息

## 示例代码

完整的使用示例请参考 `example.py` 文件。 