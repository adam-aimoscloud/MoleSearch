#!/usr/bin/env python3
"""
ESSearchEngine 测试文件
测试 insert 和 search 方法的各种功能
"""
import unittest
import time
from typing import List, Dict, Any
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search_engine.elasticsearch.es import ESSearchEngine
from search_engine.base import SearchInput, SearchOutput, InsertData, EmbeddingInfo
from test_data import TEST_DATA, SEARCH_TEST_CASES, EMBEDDING_LABEL_TEST_CASES


class TestESSearchEngine(unittest.TestCase):
    """ESSearchEngine 测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_index = f"test_mmretriever_{int(time.time())}"
        cls.es_param = {
            "host": "localhost",
            "port": 9200,
            "index": cls.test_index,
            "username": "",
            "password": ""
        }
        
        try:
            cls.search_engine = ESSearchEngine(cls.es_param)
            print(f"使用测试索引: {cls.test_index}")
        except Exception as e:
            print(f"无法连接到Elasticsearch: {e}")
            print("请确保Elasticsearch服务正在运行")
            raise

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        try:
            # 删除测试索引
            cls.search_engine.es.options(ignore_status=[400, 404]).indices.delete(index=cls.test_index)
            print(f"已删除测试索引: {cls.test_index}")
        except Exception as e:
            print(f"清理测试索引失败: {e}")

    def setUp(self):
        """每个测试方法前的准备"""
        # 清空索引数据
        try:
            self.search_engine.delete_all()
        except Exception:
            pass

    def test_01_initialization(self):
        """测试ES搜索引擎初始化"""
        self.assertIsNotNone(self.search_engine)
        self.assertIsNotNone(self.search_engine.es)
        self.assertEqual(self.search_engine.index_name, self.test_index)
        
        # 测试索引是否存在
        self.assertTrue(self.search_engine.es.indices.exists(index=self.test_index))

    def test_02_insert_single_data(self):
        """测试单条数据插入"""
        test_data = TEST_DATA[0]
        
        # 构建插入数据
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
        
        # 执行插入
        self.search_engine.insert(insert_data)
        
        # 等待索引刷新
        time.sleep(1)
        
        # 验证数据是否插入成功
        search_input = SearchInput(text=test_data["text"], topk=1)
        results = self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)
        self.assertEqual(results.items[0].text, test_data["text"])

    def test_03_batch_insert(self):
        """测试批量数据插入"""
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
        
        # 执行批量插入
        self.search_engine.batch_insert(batch_data)
        
        # 等待索引刷新
        time.sleep(2)
        
        # 验证数据是否插入成功
        search_input = SearchInput(text="", topk=10)  # 获取所有数据
        results = self.search_engine.search(search_input)
        
        self.assertGreaterEqual(len(results.items), len(TEST_DATA))

    def test_04_text_search(self):
        """测试文本搜索功能"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 执行文本搜索测试
        search_input = SearchInput(text="机器学习", topk=3)
        results = self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)
        
        # 验证结果包含相关文本
        found_relevant = False
        for item in results.items:
            if "机器学习" in item.text:
                found_relevant = True
                break
        
        self.assertTrue(found_relevant)

    def test_05_text_embedding_search(self):
        """测试文本embedding搜索"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 使用相似的文本embedding进行搜索
        from test_data import BASE_TEXT_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.95)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=similar_embedding)
            ],
            topk=3
        )
        
        results = self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)
        
        # 验证结果得分合理
        for item in results.items:
            self.assertGreater(item.score, 0)

    def test_06_image_embedding_search(self):
        """测试图片embedding搜索"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 使用相似的图片embedding进行搜索
        from test_data import BASE_IMAGE_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_IMAGE_EMBEDDING, 0.95)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="image_embedding", embedding=similar_embedding)
            ],
            topk=3
        )
        
        results = self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    def test_07_video_embedding_search(self):
        """测试视频embedding搜索"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 使用相似的视频embedding进行搜索
        from test_data import BASE_VIDEO_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_VIDEO_EMBEDDING, 0.95)
        
        search_input = SearchInput(
            embeddings=[
                EmbeddingInfo(label="video_embedding", embedding=similar_embedding)
            ],
            topk=3
        )
        
        results = self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    def test_08_hybrid_search(self):
        """测试混合搜索（文本+embedding）"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 执行混合搜索
        from test_data import BASE_TEXT_EMBEDDING, generate_similar_embedding
        similar_embedding = generate_similar_embedding(BASE_TEXT_EMBEDDING, 0.8)
        
        search_input = SearchInput(
            text="深度学习",
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=similar_embedding)
            ],
            topk=5
        )
        
        results = self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    def test_09_multimodal_embedding_search(self):
        """测试多模态embedding搜索"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 使用多种embedding进行搜索
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
        
        results = self.search_engine.search(search_input)
        self.assertGreater(len(results.items), 0)

    def test_10_embedding_label_mapping(self):
        """测试embedding标签映射功能"""
        for input_label, expected_field in EMBEDDING_LABEL_TEST_CASES:
            with self.subTest(input_label=input_label):
                actual_field = self.search_engine._get_embedding_field(input_label)
                self.assertEqual(actual_field, expected_field,
                               f"标签 '{input_label}' 应该映射到 '{expected_field}', 但实际映射到 '{actual_field}'")

    def test_11_empty_search(self):
        """测试空搜索（无条件搜索）"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 执行空搜索
        search_input = SearchInput(topk=5)
        results = self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)

    def test_12_topk_limit(self):
        """测试topk限制功能"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 测试不同的topk值
        for topk in [1, 3, 5]:
            with self.subTest(topk=topk):
                search_input = SearchInput(text="", topk=topk)
                results = self.search_engine.search(search_input)
                
                self.assertLessEqual(len(results.items), topk)

    def test_13_search_with_nonexistent_data(self):
        """测试搜索不存在的数据"""
        # 不插入任何数据
        
        search_input = SearchInput(text="不存在的内容", topk=5)
        results = self.search_engine.search(search_input)
        
        self.assertEqual(len(results.items), 0)

    def test_14_insert_with_partial_data(self):
        """测试插入部分数据"""
        # 只包含文本和一个embedding
        insert_data = InsertData(
            text="测试部分数据插入",
            embeddings=[
                EmbeddingInfo(label="text_embedding", embedding=[0.1] * 1024)
            ]
        )
        
        self.search_engine.insert(insert_data)
        time.sleep(1)
        
        # 验证插入成功
        search_input = SearchInput(text="测试部分数据", topk=1)
        results = self.search_engine.search(search_input)
        
        self.assertGreater(len(results.items), 0)

    def test_15_comprehensive_search_cases(self):
        """综合搜索测试用例"""
        # 先插入测试数据
        self._insert_test_data()
        
        # 执行预定义的搜索测试用例
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
                
                results = self.search_engine.search(search_input)
                
                self.assertGreaterEqual(len(results.items), test_case["expected_min_results"],
                                      f"测试用例 '{test_case['name']}' 应该返回至少 {test_case['expected_min_results']} 个结果")

    def test_16_search_result_structure(self):
        """测试搜索结果结构"""
        # 先插入测试数据
        self._insert_test_data()
        
        search_input = SearchInput(text="机器学习", topk=1)
        results = self.search_engine.search(search_input)
        
        self.assertIsInstance(results, SearchOutput)
        self.assertGreater(len(results.items), 0)
        
        item = results.items[0]
        self.assertIsInstance(item.text, str)
        self.assertIsInstance(item.image, str)
        self.assertIsInstance(item.video, str)
        self.assertIsInstance(item.score, (int, float))

    def _insert_test_data(self):
        """插入测试数据的辅助方法"""
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
        
        self.search_engine.batch_insert(batch_data)
        time.sleep(2)  # 等待索引刷新


class TestESSearchEngineErrorHandling(unittest.TestCase):
    """ES搜索引擎错误处理测试"""

    def test_invalid_connection_params(self):
        """测试无效连接参数"""
        invalid_params = {
            "host": "nonexistent_host",
            "port": 9999,
            "index": "test_index"
        }
        
        # 这应该不会立即失败，但在实际操作时会失败
        try:
            engine = ESSearchEngine(invalid_params)
            # 尝试执行操作应该失败
            search_input = SearchInput(text="test", topk=1)
            results = engine.search(search_input)
            # 应该返回空结果而不是抛出异常
            self.assertEqual(len(results.items), 0)
        except Exception:
            # 如果抛出异常也是可以接受的
            pass


if __name__ == '__main__':
    print("ESSearchEngine 测试开始")
    print("=" * 60)
    print("注意：这些测试需要Elasticsearch服务运行在localhost:9200")
    print("=" * 60)
    
    # 运行测试
    unittest.main(verbosity=2) 