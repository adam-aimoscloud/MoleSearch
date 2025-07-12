#!/usr/bin/env python3
"""
MMExtractor real API demo script
Show how to use the real API for text, image, and video multi-modal processing
"""

import asyncio
import yaml
import os
import sys
import json
from pathlib import Path

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.pipelines.mm_extractor import MMExtractor
from processor.core import PipelineParam, MMData, TextItem, ImageItem, VideoItem


async def demo_text_processing():
    """演示文本处理功能"""
    print("\n🔤 文本处理演示")
    print("-" * 40)
    
    # Load configuration
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create extractor
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # Test text
    test_text = "人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出能以人类智能相似的方式作出反应的智能机器。"
    
    print(f"输入文本: {test_text}")
    
    # Create input data
    input_data = MMData()
    input_data.text = TextItem(text=test_text)
    
    try:
        # Execute processing
        result = await extractor.forward(input_data)
        
        # Display result
        print(f"✅ Text embedding successful!")
        print(f"  Dimension: {len(result.text.text_embeddings[0])}")
        print(f"  First 10 values: {result.text.text_embeddings[0][:10]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text processing failed: {e}")
        return False


async def demo_image_processing():
    """Demo image processing function"""
    print("\n🖼️ Image processing demo")
    print("-" * 40)
    
    # Load configuration
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create extractor
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # Test image URL
    test_image = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    
    print(f"Input image: {test_image}")
    
    # Create input data
    input_data = MMData()
    input_data.image = ImageItem(image=test_image)
    
    try:
        # Execute processing
        result = await extractor.forward(input_data)
        
        # Display result
        print(f"✅ Image processing successful!")
        print(f"  Image embedding dimension: {len(result.image.image_embedding)}")
        print(f"  VLM description: {result.image.text}")
        print(f"  Text embedding dimension: {len(result.image.text_embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        return False


async def demo_video_processing():
    """Demo video processing function"""
    print("\n🎥 Video processing demo")
    print("-" * 40)
    
    # Load configuration
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create extractor
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # Test video URL
    test_video = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250107/lbcemt/new+video.mp4"
    
    print(f"Input video: {test_video}")
    
    # Create input data
    input_data = MMData()
    input_data.video = VideoItem(video=test_video)
    
    try:
        # Execute processing
        result = await extractor.forward(input_data)
        
        # Display result
        print(f"✅ Video processing successful!")
        print(f"  Video embedding dimension: {len(result.video.video_embedding)}")
        print(f"  ASR audio text: {result.video.text}")
        print(f"  Text embedding dimension: {len(result.video.text_embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Video processing failed: {e}")
        return False


async def demo_multimodal_processing():
    """Demo multimodal processing function"""
    print("\n🌈 Multimodal processing demo")
    print("-" * 40)
    
    # Load configuration
    config_path = Path(__file__).parent / 'mm_extractor_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create extractor
    pipeline_param = PipelineParam.from_dict(config)
    extractor = MMExtractor(pipeline_param)
    
    # Test data
    test_text = "This is a test case with multiple modalities"
    test_image = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    test_video = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250107/lbcemt/new+video.mp4"
    
    print(f"Input text: {test_text}")
    print(f"Input image: {test_image}")
    print(f"Input video: {test_video}")
    
    # Create input data
    input_data = MMData()
    input_data.text = TextItem(text=test_text)
    input_data.image = ImageItem(image=test_image)
    input_data.video = VideoItem(video=test_video)
    
    try:
        # Execute processing
        result = await extractor.forward(input_data)
        
        # Display result
        print(f"✅ Multimodal processing successful!")
        
        # Text result
        print(f"  📝 Text embedding: ✓ (dimension: {len(result.text.text_embeddings[0])})")
        
        # Image result
        print(f"  🖼️ Image embedding: ✓ (dimension: {len(result.image.image_embedding)})")
        print(f"     Image description: {result.image.text[:50]}...")
        
        # Video result
        print(f"  🎥 Video embedding: ✓ (dimension: {len(result.video.video_embedding)})")
        print(f"     Video audio: {result.video.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multimodal processing failed: {e}")
        return False


async def main():
    """Main function"""
    print("🚀 MMExtractor real API demo")
    print("=" * 60)
    print("⚠️  This demo will call the real API service, which may incur costs")
    print("⚠️  Please ensure your API key is configured correctly and has enough balance")
    print("=" * 60)
    
    # Get user confirmation
    confirm = input("\nContinue running demo? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ Demo cancelled")
        return
    
    # Run demo
    results = []
    
    try:
        # 1. Text processing demo
        results.append(await demo_text_processing())
        
        # 2. Image processing demo
        results.append(await demo_image_processing())
        
        # 3. Video processing demo
        results.append(await demo_video_processing())
        
        # 4. Multimodal processing demo
        results.append(await demo_multimodal_processing())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Demo summary")
        print("-" * 40)
        
        demos = ["Text processing", "Image processing", "Video processing", "Multimodal processing"]
        for i, (demo, success) in enumerate(zip(demos, results)):
            status = "✅ Success" if success else "❌ Failed"
            print(f"{i+1}. {demo}: {status}")
        
        total_success = sum(results)
        print(f"\nTotal: {total_success}/{len(results)} demos successful")
        
        if total_success == len(results):
            print("🎉 All demos completed successfully!")
        else:
            print("⚠️  Some demos failed, please check the configuration and network connection")
            
    except Exception as e:
        print(f"\n❌ Error occurred while running the demo: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Demo completed")


if __name__ == '__main__':
    asyncio.run(main()) 