# MMExtractor 真实API测试指南

## 概述

MMExtractor 现在支持两种类型的测试：

1. **Mock测试** - 使用模拟对象，快速验证逻辑，不产生费用
2. **真实API测试** - 调用实际的阿里云DashScope API，验证端到端功能

## 测试文件结构

```
mmretriever-api/tests/
├── mm_extractor_test.py          # 包含Mock和真实API测试
├── mm_extractor_config.yaml      # 配置文件（包含API key）
├── qwen_vlm_prompt.txt           # VLM提示词模板
├── run_real_tests.py             # 真实API测试运行脚本
├── demo_real_api.py              # 演示脚本
└── README.md                     # 基本说明
```

## 运行测试

### 1. Mock测试（推荐用于开发）

Mock测试使用模拟对象，不会调用真实API，快速且免费：

```bash
# 运行所有Mock测试
python -m pytest mm_extractor_test.py::TestMMExtractor -v

# 运行特定的Mock测试
python -m pytest mm_extractor_test.py::TestMMExtractor::test_01_initialization -v
```

### 2. 真实API测试

⚠️ **注意**: 真实API测试会调用阿里云DashScope API，可能产生费用！

#### 方法1：使用环境变量

```bash
# 设置环境变量启用真实API测试
export ENABLE_REAL_API_TESTS=true

# 运行真实API测试
python -m pytest mm_extractor_test.py::TestMMExtractorRealAPI -v
```

#### 方法2：使用运行脚本

```bash
# 交互式运行真实API测试
python run_real_tests.py
```

#### 方法3：使用演示脚本

```bash
# 运行演示，展示各种功能
python demo_real_api.py
```

## 测试内容

### Mock测试 (TestMMExtractor)

1. **test_01_initialization** - 测试MMExtractor初始化
2. **test_02_text_processing** - 测试文本处理功能
3. **test_03_image_processing** - 测试图像处理功能
4. **test_04_video_processing** - 测试视频处理功能
5. **test_05_multimodal_processing** - 测试多模态处理
6. **test_06_empty_input_handling** - 测试空输入处理
7. **test_07_partial_data_handling** - 测试部分数据处理
8. **test_08_config_loading** - 测试配置加载
9. **test_09_plugin_parameter_validation** - 测试插件参数验证

### 真实API测试 (TestMMExtractorRealAPI)

1. **test_10_real_text_embedding** - 真实文本嵌入API测试
2. **test_11_real_image_processing** - 真实图像处理API测试
3. **test_12_real_video_processing** - 真实视频处理API测试
4. **test_13_real_multimodal_processing** - 真实多模态处理API测试
5. **test_14_real_api_performance** - API性能测试
6. **test_15_real_error_handling** - 错误处理测试

## 配置说明

### API Key配置

确保在 `mm_extractor_config.yaml` 中正确配置API key：

```yaml
plugins:
  ASRPluginParam:
    param:
      api_key: "your-api-key-here"
  TEmbedPluginParam:
    param:
      api_key: "your-api-key-here"
  # ... 其他插件
```

### 测试数据

真实API测试使用以下官方示例数据：

- **文本**: "人工智能是计算机科学的一个分支..."
- **图像**: `https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg`
- **视频**: `https://dashscope.oss-cn-beijing.aliyuncs.com/videos/video_understanding.mp4`

## 常见问题

### Q: 为什么需要两种测试？

- **Mock测试**: 用于开发期间快速验证逻辑，不依赖外部服务
- **真实API测试**: 用于验证与实际API的集成，确保端到端功能正常

### Q: 真实API测试会产生多少费用？

费用取决于：
- API调用次数
- 处理的数据量
- 使用的模型类型

建议在测试前检查阿里云DashScope的计费说明。

### Q: 如何只运行特定的测试？

```bash
# 只运行文本处理测试
python -m pytest mm_extractor_test.py::TestMMExtractor::test_02_text_processing -v

# 只运行真实图像处理测试
ENABLE_REAL_API_TESTS=true python -m pytest mm_extractor_test.py::TestMMExtractorRealAPI::test_11_real_image_processing -v
```

### Q: 测试失败怎么办？

1. **检查配置**: 确保API key正确且有效
2. **检查网络**: 确保能访问阿里云服务
3. **检查余额**: 确保账户有足够余额
4. **查看日志**: 检查详细的错误信息

## 开发建议

1. **开发阶段**: 主要使用Mock测试，快速迭代
2. **集成测试**: 定期运行真实API测试，验证集成
3. **CI/CD**: 在持续集成中使用Mock测试，避免费用
4. **发布前**: 运行完整的真实API测试套件

## 添加新测试

### 添加Mock测试

1. 在 `TestMMExtractor` 类中添加新方法
2. 使用 `AsyncMock` 模拟插件行为
3. 使用 `asyncio.run()` 运行异步代码

```python
def test_new_feature(self):
    with patch('processor.pipelines.mm_extractor.SomePlugin') as mock_plugin:
        mock_instance = Mock()
        mock_instance.forward = AsyncMock(return_value=DataIO(...))
        mock_plugin.return_value = mock_instance
        
        extractor = MMExtractor(self.pipeline_param)
        result = asyncio.run(extractor.forward(input_data))
        
        # 验证结果
        self.assertIsNotNone(result)
```

### 添加真实API测试

1. 在 `TestMMExtractorRealAPI` 类中添加新方法
2. 使用真实的输入数据
3. 验证实际的API响应

```python
def test_new_real_feature(self):
    input_data = MMData()
    # 设置真实输入数据
    
    try:
        result = asyncio.run(self.extractor.forward(input_data))
        # 验证结果
        self.assertIsNotNone(result)
    except Exception as e:
        self.fail(f"测试失败: {e}")
```

## 故障排除

### 常见错误

1. **API Key错误**: 检查配置文件中的API key是否正确
2. **网络错误**: 检查网络连接和防火墙设置
3. **异步错误**: 确保使用 `asyncio.run()` 或 `await`
4. **依赖错误**: 确保安装了所有必需的依赖

### 调试技巧

1. **添加日志**: 使用 `print()` 或 `logging` 查看中间结果
2. **单步调试**: 使用断点调试器逐步检查
3. **简化测试**: 创建最小化的测试用例
4. **检查响应**: 打印API响应以了解具体错误

## 联系支持

如果遇到问题，请：

1. 检查本指南的故障排除部分
2. 查看阿里云DashScope官方文档
3. 联系团队技术支持 