# 音频提取器使用说明

本目录包含音频提取器的使用示例和说明文档。

## 功能概述

音频提取器可以从视频URL中提取WAV格式的音频文件，并自动上传到阿里云OSS，返回音频的访问URL。

### 主要特性

- ✅ 支持从任意视频URL提取音频
- ✅ 自动转换为WAV格式（16kHz单声道）
- ✅ 自动上传到阿里云OSS
- ✅ 完整的错误处理和日志记录
- ✅ 临时文件自动清理
- ✅ 批量处理支持
- ✅ 音频信息获取

## 安装依赖

```bash
cd mmretriever-api/processor
pip install -r requirements.txt
```

确保系统已安装ffmpeg：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载并安装ffmpeg到系统PATH
```

## 配置说明

### 方法1: 环境变量

```bash
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="https://oss-cn-hangzhou.aliyuncs.com"
export OSS_BUCKET_NAME="your_bucket_name"
```

### 方法2: 配置文件

创建 `oss_config.json` 文件：

```json
{
  "access_key_id": "your_oss_access_key_id",
  "access_key_secret": "your_oss_access_key_secret",
  "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
  "bucket_name": "your_oss_bucket_name"
}
```

## 基本使用

### 简单使用（便捷函数）

```python
from utils.audio_extractor import extract_audio

# OSS配置
oss_config = {
    'access_key_id': 'your_access_key_id',
    'access_key_secret': 'your_access_key_secret',
    'endpoint': 'https://oss-cn-hangzhou.aliyuncs.com',
    'bucket_name': 'your_bucket_name'
}

# 提取音频
video_url = "https://example.com/video.mp4"
audio_url = extract_audio(video_url, oss_config, "my_audio")
print(f"音频URL: {audio_url}")
```

### 高级使用（类实例）

```python
from utils.audio_extractor import AudioExtractor

# 创建提取器实例
extractor = AudioExtractor(
    oss_access_key_id='your_access_key_id',
    oss_access_key_secret='your_access_key_secret',
    oss_endpoint='https://oss-cn-hangzhou.aliyuncs.com',
    oss_bucket_name='your_bucket_name'
)

# 提取音频
audio_url = extractor.extract_audio(video_url, "my_audio")

# 获取音频信息
audio_info = extractor.get_audio_info(audio_url)
print(f"音频时长: {audio_info['duration']:.2f}秒")
```

## 运行示例

```bash
cd mmretriever-api/processor/examples
python audio_extraction_example.py
```

示例包含：
- 基本使用示例
- 高级功能示例
- 批量处理示例

## 输出格式

### 音频格式规格
- **格式**: WAV (PCM)
- **编码**: pcm_s16le (16位有符号小端)
- **采样率**: 16kHz
- **声道**: 单声道
- **适用场景**: 语音识别、语音处理

### OSS存储路径
```
{audio_prefix}/{uuid}.wav
```

例如：
```
audio/12345678-1234-5678-9abc-123456789abc.wav
examples/basic/12345678-1234-5678-9abc-123456789abc.wav
```

## API参考

### AudioExtractor类

#### 构造函数
```python
AudioExtractor(oss_access_key_id, oss_access_key_secret, oss_endpoint, oss_bucket_name)
```

#### 主要方法

- `extract_audio(video_url, audio_prefix="audio")` - 提取音频并上传
- `get_audio_info(audio_url)` - 获取音频信息

### 便捷函数

- `extract_audio(video_url, oss_config, audio_prefix="audio")` - 一行代码提取音频

## 错误处理

常见错误及解决方案：

### 1. FFmpeg未安装
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```
**解决**: 安装ffmpeg到系统PATH

### 2. OSS配置错误
```
oss2.exceptions.NoSuchBucket: The specified bucket does not exist.
```
**解决**: 检查bucket名称和endpoint配置

### 3. 网络连接问题
```
requests.exceptions.ConnectionError
```
**解决**: 检查网络连接和视频URL有效性

### 4. 权限问题
```
oss2.exceptions.AccessDenied
```
**解决**: 检查OSS访问密钥和权限配置

## 性能优化建议

1. **批量处理**: 使用相同的AudioExtractor实例处理多个视频
2. **并发处理**: 可以使用多线程/多进程并行处理
3. **错误重试**: 对网络相关错误实施重试机制
4. **缓存优化**: 避免重复下载相同视频

## 日志配置

默认日志级别为INFO，可以通过以下方式调整：

```python
import logging
logging.getLogger('audio_extractor').setLevel(logging.DEBUG)
```

## 许可证

请遵循项目的许可证要求使用本音频提取器。

## 支持与反馈

如有问题或建议，请提交Issue或Pull Request。 