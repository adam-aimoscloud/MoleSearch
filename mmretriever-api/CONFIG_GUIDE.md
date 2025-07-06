# MMRetriever 配置指南

## 概述

MMRetriever 使用 `config.yaml` 文件进行统一配置管理，包含服务器配置、MMExtractor配置、搜索引擎配置等所有必要配置项。所有配置都直接从配置文件读取，不依赖环境变量。

## 配置文件结构

### 1. 服务器配置 (`server`)

```yaml
server:
  host: "0.0.0.0"          # 服务监听地址
  port: 8000               # 服务端口
  log_level: "INFO"        # 日志级别
  dev_mode: false          # 开发模式（启用热重载）
  access_log: true         # 启用访问日志
  cors_origins: ["*"]      # 跨域设置
  docs_url: "/docs"        # API文档路径
  redoc_url: "/redoc"      # ReDoc文档路径
```

### 2. MMExtractor配置 (`mmextractor`)

#### 2.1 基本配置

```yaml
mmextractor:
  name: "MMExtractor"
  type: "extraction"
  enable: true
```

#### 2.2 插件配置

##### ASR (语音识别) 插件

```yaml
plugins:
  ASRPluginParam:
    name: "asr"
    type: "speech_recognition"
    impl: "aliyun"
    param:
      oss_access_key_id: "${OSS_ACCESS_KEY_ID}"
      oss_access_key_secret: "${OSS_ACCESS_KEY_SECRET}"
      oss_endpoint: "oss-cn-hangzhou.aliyuncs.com"
      oss_bucket_name: "mmretriever-audio"
      model: "paraformer-realtime-v2"
      api_key: "${DASHSCOPE_API_KEY}"
      audio_prefix: "audio_"
```

##### 文本嵌入插件

```yaml
TEmbedPluginParam:
  name: "text_embed"
  type: "text_embedding"
  impl: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model: "text-embedding-v4"
```

##### 图像嵌入插件

```yaml
IEmbedPluginParam:
  name: "image_embed"
  type: "image_embedding"
  impl: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model: "multimodal-embedding-v1"
```

##### 视频嵌入插件

```yaml
VEmbedPluginParam:
  name: "video_embed"
  type: "video_embedding"
  impl: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model: "multimodal-embedding-v1"
```

##### 视觉语言模型插件

```yaml
VLMPluginParam:
  name: "vlm"
  type: "vision_language_model"
  impl: "qwen"
  param:
    api_key: "${DASHSCOPE_API_KEY}"
    model: "qwen-vl-max-latest"
    prompt_path: "tests/qwen_vlm_prompt.txt"
```

### 3. 搜索引擎配置 (`search_engine`)

```yaml
search_engine:
  type: "elasticsearch"
  config:
    host: "localhost"
    port: 9200
    scheme: "http"
    index: "mmretriever"
    username: ""              # 可选
    password: ""              # 可选
    timeout: 30
    max_retries: 3
    vector_dimensions:
      text_embedding: 1536
      image_embedding: 1536
      video_embedding: 1536
    batch_size: 100
    refresh_policy: "wait_for"
```

### 4. 凭证配置 (`credentials`)

```yaml
credentials:
  # 阿里云DashScope API密钥
  dashscope_api_key: "your_dashscope_api_key_here"
  
  # 阿里云OSS配置
  oss:
    access_key_id: "your_oss_access_key_id_here"
    access_key_secret: "your_oss_access_key_secret_here"
    endpoint: "oss-cn-hangzhou.aliyuncs.com"
    bucket_name: "mmretriever-audio"
```

### 5. 配置验证 (`validation`)

```yaml
validation:
  # 验证必需的配置项
  required_fields:
    - "credentials.dashscope_api_key"
    - "credentials.oss.access_key_id"
    - "credentials.oss.access_key_secret"
  
  # 验证配置项格式
  format_validation:
    dashscope_api_key_min_length: 20
    oss_endpoint_pattern: "^oss-.*\\.aliyuncs\\.com$"
```

### 6. 性能配置 (`performance`)

```yaml
performance:
  max_concurrent_requests: 10
  request_timeout: 300
  max_memory_mb: 2048
  cache:
    enable: true
    ttl: 3600
    max_size: 1000
```

### 7. 安全配置 (`security`)

```yaml
security:
  api_key_required: false
  api_key_header: "X-API-Key"
  rate_limit:
    enable: false
    requests_per_minute: 100
    burst_size: 20
```

### 8. 监控配置 (`monitoring`)

```yaml
monitoring:
  health_check:
    endpoint: "/health"
    interval: 30
  metrics:
    enable: true
    endpoint: "/metrics"
    collect_system_metrics: true
    collect_app_metrics: true
```

### 9. 日志配置 (`logging`)

```yaml
logging:
  level: "INFO"
  format: "json"
  output: "stdout"
  file:
    path: "logs/mmretriever.log"
    max_size: "100MB"
    backup_count: 5
    rotation: "daily"
  access_log:
    enable: true
    format: "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\""
```

## 使用方法

### 1. 配置文件设置

在启动服务前，需要编辑 `config.yaml` 文件，填入必要的配置信息：

```yaml
# 编辑 config.yaml 文件
credentials:
  dashscope_api_key: "your_real_dashscope_api_key"
  oss:
    access_key_id: "your_real_oss_access_key_id"
    access_key_secret: "your_real_oss_access_key_secret"
    endpoint: "oss-cn-hangzhou.aliyuncs.com"
    bucket_name: "your-bucket-name"

# 插件配置中的占位符会自动替换为上述凭证
```

### 2. 启动服务

```bash
# 使用默认配置文件 (config.yaml)
python start_server.py

# 使用自定义配置文件
CONFIG_PATH="custom_config.yaml" python start_server.py
```

### 3. 配置文件验证

配置管理器会在启动时自动验证配置文件：

- 检查文件格式是否正确
- 验证必需的配置字段是否填写
- 检查配置项的有效性和格式
- 验证API密钥长度等格式要求

### 4. 动态配置

可以通过配置管理器动态获取配置：

```python
from utils.config import get_config_manager

config_manager = get_config_manager()

# 获取服务器配置
server_config = config_manager.get_server_config()

# 获取插件配置
plugin_config = config_manager.get_plugin_config('ASRPluginParam')

# 获取凭证配置
credentials = config_manager.get_credentials()

# 获取任意配置项
es_host = config_manager.get_config('search_engine.config.host')
```

## 最佳实践

### 1. 敏感信息管理

- 不要将包含真实API密钥的配置文件提交到版本控制
- 使用占位符（如 `your_api_key_here`）作为模板
- 在生产环境中使用专门的密钥管理服务

### 2. 配置文件分离

- 开发环境：`config.dev.yaml`
- 测试环境：`config.test.yaml`
- 生产环境：`config.prod.yaml`
- 使用配置模板：`config.template.yaml`

### 3. 配置备份

- 定期备份配置文件
- 使用版本控制管理配置变更
- 文档化配置变更的原因

### 4. 安全考虑

- 设置适当的文件权限（600或640）
- 使用加密存储敏感配置
- 定期轮换API密钥
- 限制配置文件的访问权限

## 故障排除

### 1. 配置文件加载失败

```
❌ 配置文件加载失败: [Errno 2] No such file or directory: 'config.yaml'
```

**解决方案：**
- 确保 `config.yaml` 文件存在于项目根目录
- 检查文件路径是否正确
- 验证 YAML 语法是否正确

### 2. 必需配置字段缺失

```
ValueError: 缺少必需的配置字段: ['credentials.dashscope_api_key']
```

**解决方案：**
- 检查配置文件中是否填写了所有必需的字段
- 确保没有使用占位符（如 `your_api_key_here`）
- 验证配置文件结构是否正确

### 3. API密钥格式错误

```
ValueError: DashScope API密钥长度不足，至少需要 20 个字符
```

**解决方案：**
- 检查API密钥是否正确
- 确保没有多余的空格或特殊字符
- 验证API密钥是否有效

### 4. 配置项访问失败

```
AttributeError: 'NoneType' object has no attribute 'get'
```

**解决方案：**
- 检查配置项路径是否正确
- 确保配置文件结构完整
- 使用默认值处理缺失的配置项

## 示例配置

参考项目根目录下的 `config.yaml` 文件，该文件包含了所有可用配置项的示例。

## 更多帮助

如果遇到配置问题，请：

1. 检查日志输出中的错误信息
2. 验证配置文件语法
3. 确认环境变量设置
4. 参考项目文档和示例 