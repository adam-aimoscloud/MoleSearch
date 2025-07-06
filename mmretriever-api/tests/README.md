# MMExtractor 测试文档

## 概述

本目录包含了 MMExtractor（多模态数据提取器）的完整测试套件，使用 YAML 配置文件管理测试参数。

## 文件结构

```
tests/
├── mm_extractor_test.py       # 主要测试文件
├── mm_extractor_config.yaml   # 配置文件
├── qwen_vlm_prompt.txt        # VLM 提示词模板
└── README.md                  # 本文档
```

## 测试用例

测试套件包含以下 9 个测试用例：

### 1. 初始化测试 (`test_01_initialization`)
- 验证 MMExtractor 正确初始化所有插件
- 确保所有插件实例都被创建

### 2. 文本处理测试 (`test_02_text_processing`) 
- 测试纯文本输入的处理流程
- 验证 ASR 插件的调用和输出

### 3. 图像处理测试 (`test_03_image_processing`)
- 测试图像输入的完整处理流程
- 验证图像嵌入、VLM 描述生成、文本嵌入的流程

### 4. 视频处理测试 (`test_04_video_processing`)
- 测试视频输入的完整处理流程  
- 验证视频嵌入、ASR 音频转文本、文本嵌入的流程

### 5. 多模态处理测试 (`test_05_multimodal_processing`)
- 测试同时包含文本、图像、视频的输入
- 验证所有模态的并行处理

### 6. 空输入处理测试 (`test_06_empty_input_handling`)
- 测试空输入的处理
- 确保系统能正确处理边界情况

### 7. 部分数据处理测试 (`test_07_partial_data_handling`)
- 测试只包含部分模态数据的输入
- 验证系统的选择性处理能力

### 8. 配置加载测试 (`test_08_config_loading`)
- 验证 YAML 配置文件的正确加载
- 检查配置文件格式的正确性

### 9. 参数验证测试 (`test_09_plugin_parameter_validation`)
- 验证所有插件参数的正确配置
- 检查实现类型和 API 密钥的存在

## 运行测试

### 前置条件

确保安装了所有依赖：
```bash
pip install -r ../requirements.txt
```

### 运行完整测试套件

```bash
cd mmretriever-api/tests
python3 mm_extractor_test.py
```

### 预期输出

```
MMExtractor 测试开始
============================================================
test_01_initialization (__main__.TestMMExtractor.test_01_initialization)
测试MMExtractor初始化 ... ok
test_02_text_processing (__main__.TestMMExtractor.test_02_text_processing)
测试文本处理功能 ... ok
...

----------------------------------------------------------------------
Ran 9 tests in 0.009s

OK
```

## 配置文件说明

### mm_extractor_config.yaml

配置文件定义了所有插件的参数：

```yaml
name: "MMExtractor"
type: "extraction"
enable: true
plugins:
  ASRPluginParam:      # 语音识别插件
    impl: "aliyun"     # 使用阿里云实现
    param:
      api_key: "test_api_key"
      model: "paraformer-realtime-v2"
      
  TEmbedPluginParam:   # 文本嵌入插件  
    impl: "qwen"       # 使用 Qwen 实现
    param:
      api_key: "test_api_key"
      model: "text-embedding-v4"
      
  # ... 其他插件配置
```

### qwen_vlm_prompt.txt

VLM（视觉语言模型）的提示词模板，用于图像描述生成。

## Mock 策略

测试使用 Python 的 `unittest.mock` 来模拟外部 API 调用：

- **ASR 插件**: 模拟语音转文本结果
- **Embedding 插件**: 模拟嵌入向量生成  
- **VLM 插件**: 模拟图像描述文本生成

这样可以避免实际的 API 调用，使测试快速且可重复。

## 扩展测试

要添加新的测试用例：

1. 在 `TestMMExtractor` 类中添加新的测试方法
2. 使用 `test_XX_` 命名约定
3. 添加适当的 Mock 设置
4. 更新本文档

## 故障排除

### 常见问题

1. **ImportError**: 确保 Python 路径正确设置
2. **KeyError**: 检查配置文件中的插件名称
3. **Mock 失败**: 验证 Mock 设置和返回值

### 调试技巧

- 使用 `python3 -v mm_extractor_test.py` 获取详细输出
- 检查测试中的 Mock 调用是否正确
- 验证配置文件的 YAML 格式

## 贡献

提交测试相关的改进时，请确保：

1. 所有现有测试仍然通过
2. 新功能有对应的测试用例
3. 更新相关文档
4. 保持测试的独立性和可重复性 