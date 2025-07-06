#!/usr/bin/env python3
"""
MMExtractor 真实API演示脚本
展示如何使用真实的API进行文本、图像和视频的多模态处理
"""

import asyncio
import yaml
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.pipelines.mm_extractor import MMExtractor
from processor.core import PipelineParam, MMData, TextItem, ImageItem, VideoItem


async def demo_text_processing():
    """演示文本处理功能"""
    print("\n🔤 文本处理演示")
    print("-" * 40)
    
    # 加载配置
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建提取器
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # 测试文本
    test_text = "人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出能以人类智能相似的方式作出反应的智能机器。"
    
    print(f"输入文本: {test_text}")
    
    # 创建输入数据
    input_data = MMData()
    input_data.text = TextItem(text=test_text)
    
    try:
        # 执行处理
        result = await extractor.forward(input_data)
        
        # 显示结果
        print(f"✅ 文本嵌入成功!")
        print(f"  维度: {len(result.text.text_embeddings[0])}")
        print(f"  前10个值: {result.text.text_embeddings[0][:10]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文本处理失败: {e}")
        return False


async def demo_image_processing():
    """演示图像处理功能"""
    print("\n🖼️ 图像处理演示")
    print("-" * 40)
    
    # 加载配置
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建提取器
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # 测试图像URL
    test_image = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    
    print(f"输入图像: {test_image}")
    
    # 创建输入数据
    input_data = MMData()
    input_data.image = ImageItem(image=test_image)
    
    try:
        # 执行处理
        result = await extractor.forward(input_data)
        
        # 显示结果
        print(f"✅ 图像处理成功!")
        print(f"  图像嵌入维度: {len(result.image.image_embedding)}")
        print(f"  VLM描述: {result.image.text}")
        print(f"  文本嵌入维度: {len(result.image.text_embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 图像处理失败: {e}")
        return False


async def demo_video_processing():
    """演示视频处理功能"""
    print("\n🎥 视频处理演示")
    print("-" * 40)
    
    # 加载配置
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建提取器
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # 测试视频URL
    test_video = "https://dashscope.oss-cn-beijing.aliyuncs.com/videos/video_understanding.mp4"
    
    print(f"输入视频: {test_video}")
    
    # 创建输入数据
    input_data = MMData()
    input_data.video = VideoItem(video=test_video)
    
    try:
        # 执行处理
        result = await extractor.forward(input_data)
        
        # 显示结果
        print(f"✅ 视频处理成功!")
        print(f"  视频嵌入维度: {len(result.video.video_embedding)}")
        print(f"  ASR音频文本: {result.video.text}")
        print(f"  文本嵌入维度: {len(result.video.text_embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 视频处理失败: {e}")
        return False


async def demo_multimodal_processing():
    """演示多模态处理功能"""
    print("\n🌈 多模态处理演示")
    print("-" * 40)
    
    # 加载配置
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建提取器
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # 测试数据
    test_text = "这是一个包含多种模态的测试案例"
    test_image = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    test_video = "https://dashscope.oss-cn-beijing.aliyuncs.com/videos/video_understanding.mp4"
    
    print(f"输入文本: {test_text}")
    print(f"输入图像: {test_image}")
    print(f"输入视频: {test_video}")
    
    # 创建输入数据
    input_data = MMData()
    input_data.text = TextItem(text=test_text)
    input_data.image = ImageItem(image=test_image)
    input_data.video = VideoItem(video=test_video)
    
    try:
        # 执行处理
        result = await extractor.forward(input_data)
        
        # 显示结果
        print(f"✅ 多模态处理成功!")
        
        # 文本结果
        print(f"  📝 文本嵌入: ✓ (维度: {len(result.text.text_embeddings[0])})")
        
        # 图像结果
        print(f"  🖼️ 图像嵌入: ✓ (维度: {len(result.image.image_embedding)})")
        print(f"     图像描述: {result.image.text[:50]}...")
        
        # 视频结果
        print(f"  🎥 视频嵌入: ✓ (维度: {len(result.video.video_embedding)})")
        print(f"     视频音频: {result.video.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 多模态处理失败: {e}")
        return False


async def main():
    """主函数"""
    print("🚀 MMExtractor 真实API演示")
    print("=" * 60)
    print("⚠️  此演示将调用真实的API服务，可能产生费用")
    print("⚠️  请确保您的API key配置正确且有足够的余额")
    print("=" * 60)
    
    # 获取用户确认
    confirm = input("\n继续运行演示吗？(y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ 演示已取消")
        return
    
    # 运行演示
    results = []
    
    try:
        # 1. 文本处理演示
        results.append(await demo_text_processing())
        
        # 2. 图像处理演示
        results.append(await demo_image_processing())
        
        # 3. 视频处理演示
        results.append(await demo_video_processing())
        
        # 4. 多模态处理演示
        results.append(await demo_multimodal_processing())
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 演示总结")
        print("-" * 40)
        
        demos = ["文本处理", "图像处理", "视频处理", "多模态处理"]
        for i, (demo, success) in enumerate(zip(demos, results)):
            status = "✅ 成功" if success else "❌ 失败"
            print(f"{i+1}. {demo}: {status}")
        
        total_success = sum(results)
        print(f"\n总计: {total_success}/{len(results)} 个演示成功")
        
        if total_success == len(results):
            print("🎉 所有演示都成功完成！")
        else:
            print("⚠️  部分演示失败，请检查配置和网络连接")
            
    except Exception as e:
        print(f"\n❌ 运行演示时出错: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 演示完成")


if __name__ == '__main__':
    asyncio.run(main()) 