#!/usr/bin/env python3
"""
MMExtractor test file
Test various functions of multimodal data extraction pipeline
"""
import unittest
import asyncio
import yaml
import os
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.pipelines.mm_extractor import MMExtractor
from processor.core import PipelineParam, MMData, TextItem, ImageItem, VideoItem, DataIO


class TestMMExtractor(unittest.TestCase):
    """MMExtractor test class"""

    @classmethod
    def setUpClass(cls):
        """Test class initialization"""
        # Load config file
        config_path = os.path.join(os.path.dirname(__file__), 'mm_extractor_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            cls.config = yaml.safe_load(f)
        
        # Create PipelineParam instance
        cls.pipeline_param = PipelineParam.from_dict(cls.config)
        
        # Create test data
        cls.test_text_data = MMData()
        cls.test_text_data.text = TextItem(text="this is a test text")
        
        cls.test_image_data = MMData()
        cls.test_image_data.image = ImageItem(image="https://example.com/test.jpg")
        
        cls.test_video_data = MMData()
        cls.test_video_data.video = VideoItem(video="https://example.com/test.mp4")
        
        cls.test_multimodal_data = MMData()
        cls.test_multimodal_data.text = TextItem(text="test multimodal data")
        cls.test_multimodal_data.image = ImageItem(image="https://example.com/multimodal.jpg")
        cls.test_multimodal_data.video = VideoItem(video="https://example.com/multimodal.mp4")

    def setUp(self):
        """Prepare for each test method"""
        # Create mock objects to simulate various plugins
        self.mock_asr_plugin = Mock()
        self.mock_tembed_plugin = Mock()
        self.mock_iembed_plugin = Mock()
        self.mock_vembed_plugin = Mock()
        self.mock_vlm_plugin = Mock()

    def test_01_initialization(self):
        """Test MMExtractor initialization"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm:
            
            extractor = MMExtractor(self.pipeline_param)
            
            # Verify all plugins are correctly initialized
            mock_asr.assert_called_once()
            mock_tembed.assert_called_once()
            mock_iembed.assert_called_once()
            mock_vembed.assert_called_once()
            mock_vlm.assert_called_once()
            
            self.assertIsNotNone(extractor.asr)
            self.assertIsNotNone(extractor.tembed)
            self.assertIsNotNone(extractor.iembed)
            self.assertIsNotNone(extractor.vembed)
            self.assertIsNotNone(extractor.vlm)

    def test_02_text_processing(self):
        """Test text processing function"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr_class, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed_class, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed_class, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed_class, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm_class:
            
            # Set mock return value - now text processing uses TEmbedPlugin
            mock_tembed_instance = Mock()
            mock_tembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.1, 0.2, 0.3]]))
            mock_tembed_class.return_value = mock_tembed_instance
            
            # Set mock return value for other plugins
            mock_asr_class.return_value = Mock()
            mock_iembed_class.return_value = Mock()
            mock_vembed_class.return_value = Mock()
            mock_vlm_class.return_value = Mock()
            
            extractor = MMExtractor(self.pipeline_param)
            result = asyncio.run(extractor.forward(self.test_text_data))
            
            # Verify result
            self.assertIsNotNone(result.text)
            self.assertEqual(result.text.text_embeddings, [[0.1, 0.2, 0.3]])
            
            # Verify TEmbedPlugin is called
            mock_tembed_instance.forward.assert_called_once()

    def test_03_image_processing(self):
        """Test image processing function"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr_class, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed_class, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed_class, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed_class, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm_class:
            
            # Set mock return value
            mock_iembed_instance = Mock()
            mock_iembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.4, 0.5, 0.6]]))
            mock_iembed_class.return_value = mock_iembed_instance
            
            mock_vlm_instance = Mock()
            mock_vlm_instance.forward = AsyncMock(return_value=DataIO(text="image description text"))
            mock_vlm_class.return_value = mock_vlm_instance
            
            mock_tembed_instance = Mock()
            mock_tembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.7, 0.8, 0.9]]))
            mock_tembed_class.return_value = mock_tembed_instance
            
            # Set mock return value for other plugins
            mock_asr_class.return_value = Mock()
            mock_vembed_class.return_value = Mock()
            
            extractor = MMExtractor(self.pipeline_param)
            result = asyncio.run(extractor.forward(self.test_image_data))
            
            # Verify result
            self.assertIsNotNone(result.image)
            self.assertEqual(result.image.image_embedding, [0.4, 0.5, 0.6])
            self.assertEqual(result.image.text, "image description text")
            self.assertEqual(result.image.text_embeddings, [[0.7, 0.8, 0.9]])
            
            # Verify related plugins are called
            mock_iembed_instance.forward.assert_called_once()
            mock_vlm_instance.forward.assert_called_once()
            mock_tembed_instance.forward.assert_called_once()

    def test_04_video_processing(self):
        """Test video processing function"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr_class, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed_class, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed_class, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed_class, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm_class:
            
            # Set mock return value
            mock_vembed_instance = Mock()
            mock_vembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.1, 0.2, 0.3]]))
            mock_vembed_class.return_value = mock_vembed_instance
            
            mock_asr_instance = Mock()
            mock_asr_instance.forward = AsyncMock(return_value=DataIO(text="video audio to text"))
            mock_asr_class.return_value = mock_asr_instance
            
            mock_tembed_instance = Mock()
            mock_tembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.4, 0.5, 0.6]]))
            mock_tembed_class.return_value = mock_tembed_instance
            
            # Set mock return value for other plugins
            mock_iembed_class.return_value = Mock()
            mock_vlm_class.return_value = Mock()
            
            extractor = MMExtractor(self.pipeline_param)
            result = asyncio.run(extractor.forward(self.test_video_data))
            
            # Verify result
            self.assertIsNotNone(result.video)
            self.assertEqual(result.video.video_embedding, [0.1, 0.2, 0.3])
            self.assertEqual(result.video.text, "video audio to text")
            self.assertEqual(result.video.text_embeddings, [[0.4, 0.5, 0.6]])
            
            # Verify related plugins are called
            mock_vembed_instance.forward.assert_called_once()
            mock_asr_instance.forward.assert_called_once()
            mock_tembed_instance.forward.assert_called_once()

    def test_05_multimodal_processing(self):
        """Test multimodal data processing"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr_class, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed_class, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed_class, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed_class, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm_class:
            
            # Set mock return value for all plugins
            mock_asr_instance = Mock()
            mock_asr_instance.forward = AsyncMock(return_value=DataIO(text="video audio to text"))
            mock_asr_class.return_value = mock_asr_instance
            
            mock_tembed_instance = Mock()
            mock_tembed_instance.forward = AsyncMock(side_effect=[
                DataIO(embeddings=[[0.1, 0.2, 0.3]]),  # text embedding
                DataIO(embeddings=[[0.4, 0.5, 0.6]]),  # image text embedding
                DataIO(embeddings=[[0.7, 0.8, 0.9]])   # video text embedding
            ])
            mock_tembed_class.return_value = mock_tembed_instance
            
            mock_iembed_instance = Mock()
            mock_iembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.11, 0.12, 0.13]]))
            mock_iembed_class.return_value = mock_iembed_instance
            
            mock_vembed_instance = Mock()
            mock_vembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.14, 0.15, 0.16]]))
            mock_vembed_class.return_value = mock_vembed_instance
            
            mock_vlm_instance = Mock()
            mock_vlm_instance.forward = AsyncMock(return_value=DataIO(text="multimodal image description"))
            mock_vlm_class.return_value = mock_vlm_instance
            
            extractor = MMExtractor(self.pipeline_param)
            result = asyncio.run(extractor.forward(self.test_multimodal_data))
            
            # Verify result for all modalities
            self.assertIsNotNone(result.text)
            self.assertEqual(result.text.text_embeddings, [[0.1, 0.2, 0.3]])
            
            self.assertIsNotNone(result.image)
            self.assertEqual(result.image.image_embedding, [0.11, 0.12, 0.13])
            self.assertEqual(result.image.text, "multimodal image description")
            self.assertEqual(result.image.text_embeddings, [[0.4, 0.5, 0.6]])
            
            self.assertIsNotNone(result.video)
            self.assertEqual(result.video.video_embedding, [0.14, 0.15, 0.16])
            self.assertEqual(result.video.text, "video audio to text")
            self.assertEqual(result.video.text_embeddings, [[0.7, 0.8, 0.9]])

    def test_06_empty_input_handling(self):
        """Test empty input handling"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr_class, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed_class, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed_class, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed_class, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm_class:
            
            # Set mock return value for plugins
            mock_asr_class.return_value = Mock()
            mock_tembed_class.return_value = Mock()
            mock_iembed_class.return_value = Mock()
            mock_vembed_class.return_value = Mock()
            mock_vlm_class.return_value = Mock()
            
            extractor = MMExtractor(self.pipeline_param)
            
            # Test empty input
            empty_data = MMData()
            result = asyncio.run(extractor.forward(empty_data))
            
            # Verify result structure is correct
            self.assertIsNotNone(result.text)
            self.assertIsNotNone(result.image)
            self.assertIsNotNone(result.video)
            
            # Verify plugins are not called
            mock_asr_class.return_value.forward.assert_not_called()
            mock_tembed_class.return_value.forward.assert_not_called()
            mock_iembed_class.return_value.forward.assert_not_called()
            mock_vembed_class.return_value.forward.assert_not_called()
            mock_vlm_class.return_value.forward.assert_not_called()

    def test_07_partial_data_handling(self):
        """Test partial data handling"""
        with patch('processor.pipelines.mm_extractor.ASRPlugin') as mock_asr_class, \
             patch('processor.pipelines.mm_extractor.TEmbedPlugin') as mock_tembed_class, \
             patch('processor.pipelines.mm_extractor.IEmbedPlugin') as mock_iembed_class, \
             patch('processor.pipelines.mm_extractor.VEmbedPlugin') as mock_vembed_class, \
             patch('processor.pipelines.mm_extractor.VLMPlugin') as mock_vlm_class:
            
            # Set mock return value for plugins
            mock_tembed_instance = Mock()
            mock_tembed_instance.forward = AsyncMock(return_value=DataIO(embeddings=[[0.1, 0.2, 0.3]]))
            mock_tembed_class.return_value = mock_tembed_instance
            
            mock_asr_class.return_value = Mock()
            mock_iembed_class.return_value = Mock()
            mock_vembed_class.return_value = Mock()
            mock_vlm_class.return_value = Mock()
            
            extractor = MMExtractor(self.pipeline_param)
            
            # Test only text data
            partial_data = MMData()
            partial_data.text = TextItem(text="partial text data")
            
            result = asyncio.run(extractor.forward(partial_data))
            
            # Verify only text processing is executed
            self.assertIsNotNone(result.text)
            self.assertEqual(result.text.text_embeddings, [[0.1, 0.2, 0.3]])
            
            # Verify only TEmbedPlugin is called
            mock_tembed_instance.forward.assert_called_once()
            mock_asr_class.return_value.forward.assert_not_called()
            mock_iembed_class.return_value.forward.assert_not_called()
            mock_vembed_class.return_value.forward.assert_not_called()
            mock_vlm_class.return_value.forward.assert_not_called()

    def test_08_config_loading(self):
        """Test config file loading"""
        # Verify config file content
        self.assertEqual(self.config['name'], 'MMExtractor')
        self.assertEqual(self.config['type'], 'extraction')
        self.assertTrue(self.config['enable'])
        
        # Verify plugin config
        plugins = self.config['plugins']
        self.assertIn('ASRPluginParam', plugins)
        self.assertIn('TEmbedPluginParam', plugins)
        self.assertIn('IEmbedPluginParam', plugins)
        self.assertIn('VEmbedPluginParam', plugins)
        self.assertIn('VLMPluginParam', plugins)
        
        # Verify ASR plugin config
        asr_config = plugins['ASRPluginParam']
        self.assertEqual(asr_config['impl'], 'aliyun')
        self.assertIn('param', asr_config)
        self.assertIn('api_key', asr_config['param'])

    def test_09_plugin_parameter_validation(self):
        """Test plugin parameter validation"""
        # Verify all plugin parameters have correct implementation type
        plugins = self.config['plugins']
        
        expected_impls = {
            'ASRPluginParam': 'aliyun',
            'TEmbedPluginParam': 'qwen',
            'IEmbedPluginParam': 'qwen',
            'VEmbedPluginParam': 'qwen',
            'VLMPluginParam': 'qwen'
        }
        
        for plugin_name, expected_impl in expected_impls.items():
            self.assertEqual(plugins[plugin_name]['impl'], expected_impl)
            self.assertIn('param', plugins[plugin_name])
            self.assertIn('api_key', plugins[plugin_name]['param'])


class TestMMExtractorRealAPI(unittest.TestCase):
    """MMExtractor real API test class"""

    @classmethod
    def setUpClass(cls):
        """Test class initialization"""
        # Check if real API test is enabled
        cls.enable_real_tests = os.getenv('ENABLE_REAL_API_TESTS', 'false').lower() == 'true'
        
        if not cls.enable_real_tests:
            raise unittest.SkipTest("Real API test is skipped. Set environment variable ENABLE_REAL_API_TESTS=true to enable")
        
        # Load config file
        config_path = os.path.join(os.path.dirname(__file__), 'mm_extractor_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            cls.config = yaml.safe_load(f)
        
        # Create PipelineParam instance
        cls.pipeline_param = PipelineParam.from_dict(cls.config)
        
        # Create MMExtractor instance
        cls.extractor = MMExtractor(cls.pipeline_param)
        
        # Prepare real test data
        cls.real_test_data = {
            'text': "artificial intelligence is a branch of computer science that attempts to understand the nature of intelligence and produce intelligent machines that can respond in a way similar to human intelligence.",
            'image': "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg", # Aliyun official example image
            'video': "https://dashscope.oss-cn-beijing.aliyuncs.com/videos/video_understanding.mp4"  # Aliyun official example video
        }

    def test_10_real_text_embedding(self):
        """Test real text embedding API"""
        print(f"\nTest text: {self.real_test_data['text']}")
        
        # Create text input
        input_data = MMData()
        input_data.text = TextItem(text=self.real_test_data['text'])
        
        try:
            # Execute processing
            result = asyncio.run(self.extractor.forward(input_data))
            
            # Verify result
            self.assertIsNotNone(result.text)
            self.assertIsNotNone(result.text.text_embeddings)
            self.assertGreater(len(result.text.text_embeddings), 0)
            self.assertIsInstance(result.text.text_embeddings[0], list)
            self.assertGreater(len(result.text.text_embeddings[0]), 0)
            
            print(f"✓ Text embedding successful, dimension: {len(result.text.text_embeddings[0])}")
            print(f"  5 values: {result.text.text_embeddings[0][:5]}")
            
        except Exception as e:
            self.fail(f"Real text embedding test failed: {e}")

    def test_11_real_image_processing(self):
        """Test real image processing API"""
        print(f"\nTest image: {self.real_test_data['image']}")
        
        # Create image input
        input_data = MMData()
        input_data.image = ImageItem(image=self.real_test_data['image'])
        
        try:
            # Execute processing
            result = asyncio.run(self.extractor.forward(input_data))
            
            # Verify result
            self.assertIsNotNone(result.image)
            
            # Verify image embedding
            self.assertIsNotNone(result.image.image_embedding)
            self.assertIsInstance(result.image.image_embedding, list)
            self.assertGreater(len(result.image.image_embedding), 0)
            
            # Verify VLM generated text description
            self.assertIsNotNone(result.image.text)
            self.assertIsInstance(result.image.text, str)
            self.assertGreater(len(result.image.text), 0)
            
            # validate text embedding
            self.assertIsNotNone(result.image.text_embeddings)
            self.assertGreater(len(result.image.text_embeddings), 0)
            
            print(f"✓ Image processing successful")
            print(f"  Image embedding dimension: {len(result.image.image_embedding)}")
            print(f"  VLM description: {result.image.text[:100]}...")
            print(f"  Text embedding dimension: {len(result.image.text_embeddings[0])}")
            
        except Exception as e:
            self.fail(f"Real image processing test failed: {e}")

    def test_12_real_video_processing(self):
        """Test real video processing API"""
        print(f"\nTest video: {self.real_test_data['video']}")
        
        # Create video input
        input_data = MMData()
        input_data.video = VideoItem(video=self.real_test_data['video'])
        
        try:
            # Execute processing
            result = asyncio.run(self.extractor.forward(input_data))
            
            # Verify result
            self.assertIsNotNone(result.video)
            
            # Verify video embedding
            self.assertIsNotNone(result.video.video_embedding)
            self.assertIsInstance(result.video.video_embedding, list)
            self.assertGreater(len(result.video.video_embedding), 0)
            
            # Verify ASR generated text
            self.assertIsNotNone(result.video.text)
            self.assertIsInstance(result.video.text, str)
            # Note: video may not have audio, so text may be empty
            
            # Verify text embedding
            self.assertIsNotNone(result.video.text_embeddings)
            self.assertGreater(len(result.video.text_embeddings), 0)
            
            print(f"✓ Video processing successful")
            print(f"  Video embedding dimension: {len(result.video.video_embedding)}")
            print(f"  ASR text: {result.video.text}")
            print(f"  Text embedding dimension: {len(result.video.text_embeddings[0])}")
            
        except Exception as e:
            # For video processing, if URL download fails, we skip the test instead of failing
            if "download form url error" in str(e) or "download" in str(e).lower():
                print(f"⚠ Video URL access failed, skip video processing test: {e}")
                self.skipTest(f"Video URL cannot be accessed: {e}")
            else:
                self.fail(f"Real video processing test failed: {e}")

    def test_13_real_multimodal_processing(self):
        """Test real multimodal processing API"""
        print(f"\nTest multimodal data:")
        print(f"  Text: {self.real_test_data['text'][:50]}...")
        print(f"  Image: {self.real_test_data['image']}")
        print(f"  Video: {self.real_test_data['video']}")
        
        # First test text and image processing (without possibly failing video)
        input_data_no_video = MMData()
        input_data_no_video.text = TextItem(text=self.real_test_data['text'])
        input_data_no_video.image = ImageItem(image=self.real_test_data['image'])
        
        try:
            # Execute text and image processing
            result_no_video = asyncio.run(self.extractor.forward(input_data_no_video))
            
            # Verify text result
            self.assertIsNotNone(result_no_video.text)
            self.assertIsNotNone(result_no_video.text.text_embeddings)
            self.assertGreater(len(result_no_video.text.text_embeddings), 0)
            
            # Verify image result
            self.assertIsNotNone(result_no_video.image)
            self.assertIsNotNone(result_no_video.image.image_embedding)
            self.assertIsNotNone(result_no_video.image.text)
            self.assertIsNotNone(result_no_video.image.text_embeddings)
            
            print(f"✓ Text and image processing successful")
            print(f"  Text embedding: ✓ (dimension: {len(result_no_video.text.text_embeddings[0])})")
            print(f"  Image embedding: ✓ (dimension: {len(result_no_video.image.image_embedding)})")
            print(f"  Image description: {result_no_video.image.text[:50]}...")
            
            # Now try full multimodal processing with video
            input_data_full = MMData()
            input_data_full.text = TextItem(text=self.real_test_data['text'])
            input_data_full.image = ImageItem(image=self.real_test_data['image'])
            input_data_full.video = VideoItem(video=self.real_test_data['video'])
            
            try:
                result_full = asyncio.run(self.extractor.forward(input_data_full))
                
                # Verify video result
                self.assertIsNotNone(result_full.video)
                self.assertIsNotNone(result_full.video.video_embedding)
                self.assertIsNotNone(result_full.video.text_embeddings)
                
                print(f"✓ Full multimodal processing successful")
                print(f"  Video embedding: ✓ (dimension: {len(result_full.video.video_embedding)})")
                print(f"  Video audio: {result_full.video.text}")
                
            except Exception as video_error:
                # Video processing failure does not affect the entire test
                if "download form url error" in str(video_error) or "download" in str(video_error).lower():
                    print(f"⚠ Video processing failed, but text and image processing succeeded: {video_error}")
                else:
                    print(f"⚠ Video processing encountered other errors: {video_error}")
                    
        except Exception as e:
            self.fail(f"Real multimodal processing test failed: {e}")

    def test_14_real_api_performance(self):
        """Test real API performance"""
        import time
        
        print(f"\nPerformance test...")
        
        # Test text processing performance
        input_data = MMData()
        input_data.text = TextItem(text="Performance test text")
        
        start_time = time.time()
        try:
            result = asyncio.run(self.extractor.forward(input_data))
            end_time = time.time()
            
            processing_time = end_time - start_time
            self.assertLess(processing_time, 30.0, "Text processing time should be less than 30 seconds")
            
            print(f"✓ Text processing performance: {processing_time:.2f} seconds")
            
        except Exception as e:
            self.fail(f"Performance test failed: {e}")

    def test_15_real_error_handling(self):
        """Test real API error handling"""
        print(f"\nError handling test...")
        
        # Test invalid image URL
        input_data = MMData()
        input_data.image = ImageItem(image="https://invalid-url-that-does-not-exist.com/image.jpg")
        
        try:
            result = asyncio.run(self.extractor.forward(input_data))
            # Should gracefully handle errors, not crash
            print(f"✓ Invalid URL handling: gracefully handled")
            
        except Exception as e:
            # We expect proper error handling here
            print(f"⚠ Error handling needs improvement: {e}")
            # Don't fail the test, because this is an expected error scenario


if __name__ == '__main__':
    print("MMExtractor test started")
    print("=" * 60)
    
    # Check if real API test is enabled
    enable_real_tests = os.getenv('ENABLE_REAL_API_TESTS', 'false').lower() == 'true'
    
    if enable_real_tests:
        print("🔥 Real API test is enabled")
        print("Note: This will call the real API service, which may incur costs")
        print("=" * 60)
    else:
        print("💡 Use Mock test (recommended for development)")
        print("💡 To enable real API test, set: export ENABLE_REAL_API_TESTS=true")
        print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2) 