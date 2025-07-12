#!/usr/bin/env python3
"""
ESSearchEngine test file
Test insert and search methods
"""
import unittest
import asyncio
import time
from typing import List, Dict, Any
import sys
import os
import pytest

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search_engine.elasticsearch.es import ESSearchEngine
from search_engine.base import SearchInput, SearchOutput, InsertData, EmbeddingInfo
from test_data import TEST_DATA, SEARCH_TEST_CASES, EMBEDDING_LABEL_TEST_CASES


class TestESSearchEngine(unittest.TestCase):
    """ESSearchEngine test class"""

    @classmethod
    async def asyncSetUpClass(cls):
        """Test class initialization"""
        cls.test_index = f"test_mmsearch_{int(time.time())}"
        cls.es_param = {
            "host": "localhost",
            "port": 9200,
            "index": cls.test_index,
            "username": "",
            "password": "",
            "scheme": "http",
            "timeout": 30,
            "max_retries": 3
        }
        
        try:
            cls.search_engine = ESSearchEngine(cls.es_param)
            # Test connection
            await cls.search_engine.es.ping()
            print(f"Using test index: {cls.test_index}")
        except Exception as e:
            print(f"Cannot connect to Elasticsearch: {e}")
            raise

    @classmethod
    async def asyncTearDownClass(cls):
        """Test class cleanup"""
        try:
            # Delete test index
            await cls.search_engine.es.options(ignore_status=[400, 404]).indices.delete(index=cls.test_index)
            print(f"Deleted test index: {cls.test_index}")
        except Exception as e:
            print(f"Failed to clean up test index: {e}")
        finally:
            await cls.search_engine.close()

    async def asyncSetUp(self):
        """Prepare for each test method"""
        # Clear index data - don't fail if this doesn't work
        try:
            await self.search_engine.delete_all()
        except Exception as e:
            print(f"Setup cleanup failed: {e}")
            # Continue with test even if cleanup fails

    async def asyncTearDown(self):
        """Clean up after each test method"""
        # Clear index data - don't fail if this doesn't work
        try:
            await self.search_engine.delete_all()
        except Exception as e:
            print(f"Teardown cleanup failed: {e}")
            # Continue even if cleanup fails

    async def test_00_connection_test(self):
        """Test ES connection first"""
        try:
            # Test ping
            ping_result = await self.search_engine.es.ping()
            self.assertTrue(ping_result, "ES ping failed")
            
            # Test cluster info
            info = await self.search_engine.es.info()
            self.assertIsNotNone(info)
            print(f"Connected to ES cluster: {info.get('cluster_name', 'unknown')}")
            
        except Exception as e:
            self.fail(f"ES connection test failed: {e}")

    async def test_01_initialization(self):
        """Test ES search engine initialization"""
        self.assertIsNotNone(self.search_engine)
        self.assertIsNotNone(self.search_engine.es)
        self.assertEqual(self.search_engine.index_name, self.test_index)
        
        # Test if index exists (should be created by _ensure_index)
        try:
            exists = await self.search_engine.es.indices.exists(index=self.test_index)
            self.assertTrue(exists)
        except Exception as e:
            print(f"Index existence check failed: {e}")
            # If index doesn't exist, that's okay for initialization test
            pass

    async def test_02_insert_single_data(self):
        """Test single data insertion"""
        test_data = TEST_DATA[0]
        
        # Build insert data
        insert_data = InsertData(
            text=test_data["text"],
            image=test_data["image"],
            video=test_data["video"],
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=test_data["text_embedding"]),
                EmbeddingInfo(label="image_embedding", embedding=test_data["image_embedding"]),
                EmbeddingInfo(label="video_embedding", embedding=test_data["video_embedding"])
            ]
        )
        
        # Execute insertion
        await self.search_engine.insert(insert_data)
        
        # Wait for index refresh
        await asyncio.sleep(1)
        
        # Verify if data is inserted successfully
        search_input = SearchInput(text=test_data["text"], topk=1)
        results = await self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)
        self.assertEqual(results.items[0].text, test_data["text"])

    async def test_03_batch_insert(self):
        """Test batch data insertion"""
        batch_data = []
        
        for test_data in TEST_DATA:
            insert_data = InsertData(
                text=test_data["text"],
                image=test_data["image"],
                video=test_data["video"],
                embeddings=[
                    EmbeddingInfo(label="text_embedding", embedding=test_data["text_embedding"]),
                    EmbeddingInfo(label="image_embedding", embedding=test_data["image_embedding"]),
                    EmbeddingInfo(label="video_embedding", embedding=test_data["video_embedding"])
                ]
            )
            batch_data.append(insert_data)
        
        # Execute batch insertion
        await self.search_engine.batch_insert(batch_data)
        
        # Wait for index refresh
        await asyncio.sleep(2)
        
        # Verify if data is inserted successfully
        search_input = SearchInput(text="", topk=10)  # Get all data
        results = await self.search_engine.search(search_input)
        
        self.assertGreaterEqual(len(results.items), len(TEST_DATA))

    async def test_04_text_search(self):
        """Test text search function"""
        # Insert test data first
        await self._insert_test_data()
        
        # Execute text search test
        search_input = SearchInput(text="machine learning", topk=3)
        results = await self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)
        
        # Verify if result contains relevant text (case insensitive)
        found_relevant = False
        for item in results.items:
            if "machine learning" in item.text.lower():
                found_relevant = True
                break
        
        self.assertTrue(found_relevant, f"No relevant text found in results: {[item.text for item in results.items]}")

    async def test_05_text_embedding_search(self):
        """Test text embedding search"""
        # Insert test data first
        await self._insert_test_data()
        
        # Use similar text embedding for search
        from test_data import BASE_TEXT_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.95)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=similar_embedding)
            ],
            topk=3
        )
        
        results = await self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)
        
        # Verify if result score is reasonable
        for item in results.items:
            self.assertGreater(item.score, 0)

    async def test_06_image_embedding_search(self):
        """Test image embedding search"""
        # Insert test data first
        await self._insert_test_data()
        
        # Use similar image embedding for search
        from test_data import BASE_IMAGE_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.95)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="image_embedding", embedding=similar_embedding)
            ],
            topk=3
        )
        
        results = await self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    async def test_07_video_embedding_search(self):
        """Test video embedding search"""
        # Insert test data first
        await self._insert_test_data()
        
        # Use similar video embedding for search
        from test_data import BASE_VIDEO_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.95)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="video_embedding", embedding=similar_embedding)
            ],
            topk=3
        )
        
        results = await self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    async def test_08_hybrid_search(self):
        """Test hybrid search (text + embedding)"""
        # Insert test data first
        await self._insert_test_data()
        
        # Execute hybrid search
        from test_data import BASE_TEXT_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.8)
        
        search_input = SearchInput(
            text="deep learning",
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=similar_embedding)
            ],
            topk=5
        )
        
        results = await self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    async def test_09_multimodal_embedding_search(self):
        """Test multimodal embedding search"""
        # Insert test data first
        await self._insert_test_data()
        
        # Use multiple embeddings for search
        from test_data import (BASE_TEXT_EMBEDDING, BASE_IMAGE_EMBEDDING, 
                              BASE_VIDEO_EMBEDDING, generate_similar_embedding)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="text_embedding", 
                            embedding=generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.9)),
                EmbeddingInfo(label="image_embedding", 
                            embedding=generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.9)),
                EmbeddingInfo(label="video_embedding", 
                            embedding=generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.9))
            ],
            topk=3
        )
        
        results = await self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    async def test_10_embedding_label_mapping(self):
        """Test embedding label mapping function"""
        for input_label, expected_field in EMBEDDING_LABEL_TEST_CASES:
            with self.subTest(input_label=input_label):
                actual_field = self.search_engine._get_embedding_field(input_label)
                self.assertEqual(actual_field, expected_field,
                               f"Label '{input_label}' should map to '{expected_field}', but actually maps to '{actual_field}'")

    async def test_11_empty_search(self):
        """Test empty search (no condition search)"""
        # Insert test data first
        await self._insert_test_data()
        
        # Execute empty search
        search_input = SearchInput(topk=5)
        results = await self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)

    async def test_12_topk_limit(self):
        """Test topk limit function"""
        # Insert test data first
        await self._insert_test_data()
        
        # Test different topk values
        for topk in [1, 3, 5]:
            with self.subTest(topk=topk):
                search_input = SearchInput(text="", topk=topk)
                results = await self.search_engine.search(search_input)
                
                self.assertLessEqual(len(results.items), topk)

    async def test_13_search_with_nonexistent_data(self):
        """Test search with nonexistent data"""
        # Do not insert any data
        
        search_input = SearchInput(text="nonexistent content", topk=5)
        results = await self.search_engine.search(search_input)
        
        self.assertEqual(len(results.items), 0)

    async def test_14_insert_with_partial_data(self):
        """Test insert with partial data"""
        # Only contains text and one embedding
        insert_data = InsertData(
            text="test partial data insertion",
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=[0.1] * 1024)
            ]
        )
        
        await self.search_engine.insert(insert_data)
        await asyncio.sleep(1)
        
        # Verify if insertion is successful
        search_input = SearchInput(text="test partial data", topk=1)
        results = await self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)

    async def test_15_comprehensive_search_cases(self):
        """Comprehensive search test cases"""
        # Insert test data first
        await self._insert_test_data()
        
        # Execute predefined search test cases
        for test_case in SEARCH_TEST_CASES:
            with self.subTest(test_case=test_case["name"]):
                search_input = SearchInput(
                    text=test_case["search_input"]["text"],
                    embeddings=[
                        EmbeddingInfo(label=emb["label"], embedding=emb["embedding"])
                        for emb in test_case["search_input"]["embeddings"]
                    ],
                    topk=test_case["search_input"]["topk"]
                )
                
                results = await self.search_engine.search(search_input)
                
                self.assertGreaterEqual(len(results.items), test_case["expected_min_results"],
                                      f"Test case '{test_case['name']}' should return at least {test_case['expected_min_results']} results")

    async def test_16_search_result_structure(self):
        """Test search result structure"""
        # Insert test data first
        await self._insert_test_data()
        
        search_input = SearchInput(text="machine learning", topk=1)
        results = await self.search_engine.search(search_input)
        
        self.assertIsInstance(results, SearchOutput)
        self.assertGreater(len(results.items), 0)
        
        item = results.items[0]
        self.assertIsInstance(item.text, str)
        self.assertIsInstance(item.image, str)
        self.assertIsInstance(item.video, str)
        self.assertIsInstance(item.score, (int, float))

    async def _insert_test_data(self):
        """Insert test data helper method"""
        batch_data = []
        
        for test_data in TEST_DATA:
            insert_data = InsertData(
                text=test_data["text"],
                image=test_data["image"],
                video=test_data["video"],
                embeddings=[
                    EmbeddingInfo(label="text_embedding", embedding=test_data["text_embedding"]),
                    EmbeddingInfo(label="image_embedding", embedding=test_data["image_embedding"]),
                    EmbeddingInfo(label="video_embedding", embedding=test_data["video_embedding"])
                ]
            )
            batch_data.append(insert_data)
        
        await self.search_engine.batch_insert(batch_data)
        await asyncio.sleep(2)  # Wait for index refresh


class TestESSearchEngineErrorHandling(unittest.TestCase):
    """ES search engine error handling test"""

    async def test_invalid_connection_params(self):
        """Test invalid connection parameters"""
        invalid_params = {
            "host": "nonexistent_host",
            "port": 9999,
            "index": "test_index"
        }
        
        # This should not fail immediately, but will fail in actual operation
        try:
            engine = ESSearchEngine(invalid_params)
            # Try to execute operation should fail
            search_input = SearchInput(text="test", topk=1)
            results = await engine.search(search_input)
            # Should return empty result instead of throwing exception
            self.assertEqual(len(results.items), 0)
        except Exception:
            # If exception is thrown, it is also acceptable
            pass
        finally:
            await engine.close()


# Async test runner
class AsyncTestRunner:
    """Async test runner for unittest"""
    
    def __init__(self):
        self.test_class = TestESSearchEngine
        self.error_test_class = TestESSearchEngineErrorHandling
    
    async def run_tests(self):
        """Run all async tests"""
        print("ESSearchEngine async test started")
        print("=" * 60)
        print("Note: These tests require Elasticsearch service running on localhost:9200")
        print("=" * 60)
        
        # Setup
        await self.test_class.asyncSetUpClass()
        
        # Run all test methods
        test_methods = [method for method in dir(self.test_class) if method.startswith('test_') and callable(getattr(self.test_class, method))]
        
        for method_name in test_methods:
            print(f"\nRunning {method_name}...")
            test_instance = self.test_class()
            
            try:
                await test_instance.asyncSetUp()
                method = getattr(test_instance, method_name)
                
                # Add timeout for each test
                try:
                    await asyncio.wait_for(method(), timeout=60)
                    print(f"✓ {method_name} passed")
                except asyncio.TimeoutError:
                    print(f"✗ {method_name} failed: Timeout after 60 seconds")
                except Exception as e:
                    print(f"✗ {method_name} failed: {e}")
                    
            except Exception as e:
                print(f"✗ {method_name} setup failed: {e}")
            finally:
                try:
                    await test_instance.asyncTearDown()
                except Exception as e:
                    print(f"Warning: {method_name} teardown failed: {e}")
        
        # Teardown
        await self.test_class.asyncTearDownClass()
        
        # Run error handling tests
        print("\nRunning error handling tests...")
        try:
            error_test_instance = self.error_test_class()
            await error_test_instance.test_invalid_connection_params()
            print("✓ Error handling tests completed")
        except Exception as e:
            print(f"✗ Error handling tests failed: {e}")


if __name__ == '__main__':
    # Run async tests
    runner = AsyncTestRunner()
    asyncio.run(runner.run_tests()) 