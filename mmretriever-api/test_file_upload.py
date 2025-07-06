#!/usr/bin/env python3
"""
文件上传功能测试脚本
测试OSS文件上传、删除和查询功能
"""

import requests
import os
import tempfile
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

def create_test_file(content: str, extension: str = ".txt") -> str:
    """创建测试文件"""
    temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
    temp_file.write(content.encode('utf-8'))
    temp_file.close()
    return temp_file.name

def test_file_upload():
    """测试文件上传"""
    print("🔍 测试文件上传功能...")
    
    try:
        # 创建测试文件
        test_content = f"测试文件内容 - {datetime.now().isoformat()}"
        test_file_path = create_test_file(test_content, ".txt")
        
        print(f"   创建测试文件: {test_file_path}")
        
        # 上传文件
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_file.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/api/v1/files/upload", files=files)
        
        # 清理临时文件
        os.unlink(test_file_path)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 文件上传成功")
            print(f"   - 文件URL: {result.get('file_url')}")
            print(f"   - OSS路径: {result.get('oss_path')}")
            print(f"   - 文件大小: {result.get('file_size')} 字节")
            return result
        else:
            print(f"   ❌ 文件上传失败: {response.status_code}")
            print(f"   - 错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ 文件上传测试异常: {e}")
        return None

def test_file_info(oss_path: str):
    """测试获取文件信息"""
    print(f"\n🔍 测试获取文件信息: {oss_path}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/files/info/{oss_path}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 获取文件信息成功")
            print(f"   - 文件大小: {result.get('file_size')} 字节")
            print(f"   - 内容类型: {result.get('content_type')}")
            print(f"   - 最后修改: {result.get('last_modified')}")
            return result
        else:
            print(f"   ❌ 获取文件信息失败: {response.status_code}")
            print(f"   - 错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ 获取文件信息测试异常: {e}")
        return None

def test_file_delete(oss_path: str):
    """测试删除文件"""
    print(f"\n🔍 测试删除文件: {oss_path}")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/files/delete/{oss_path}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 文件删除成功")
            return result
        else:
            print(f"   ❌ 文件删除失败: {response.status_code}")
            print(f"   - 错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ 文件删除测试异常: {e}")
        return None

def test_upload_and_insert():
    """测试上传并插入到搜索索引"""
    print("\n🔍 测试上传并插入到搜索索引...")
    
    try:
        # 创建测试图像文件（模拟）
        test_content = "模拟图像文件内容"
        test_file_path = create_test_file(test_content, ".jpg")
        
        print(f"   创建测试图像文件: {test_file_path}")
        
        # 上传并插入
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            data = {'text': '这是一个测试图像文件'}
            response = requests.post(f"{BASE_URL}/api/v1/files/upload-and-insert", files=files, data=data)
        
        # 清理临时文件
        os.unlink(test_file_path)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 上传并插入成功")
            print(f"   - 文件URL: {result.get('file_url')}")
            print(f"   - OSS路径: {result.get('oss_path')}")
            return result
        else:
            print(f"   ❌ 上传并插入失败: {response.status_code}")
            print(f"   - 错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ 上传并插入测试异常: {e}")
        return None

def test_image_upload():
    """测试图像文件上传"""
    print("\n🔍 测试图像文件上传...")
    
    try:
        # 创建一个简单的测试图像（这里用文本模拟）
        test_content = "模拟图像数据"
        test_file_path = create_test_file(test_content, ".png")
        
        print(f"   创建测试图像文件: {test_file_path}")
        
        # 上传图像
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{BASE_URL}/api/v1/files/upload", files=files)
        
        # 清理临时文件
        os.unlink(test_file_path)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 图像上传成功")
            print(f"   - 文件URL: {result.get('file_url')}")
            print(f"   - 文件类型: {result.get('file_extension')}")
            return result
        else:
            print(f"   ❌ 图像上传失败: {response.status_code}")
            print(f"   - 错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ 图像上传测试异常: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始文件上传功能测试")
    print("=" * 50)
    
    # 测试1: 基本文件上传
    upload_result = test_file_upload()
    if not upload_result:
        print("❌ 基本文件上传测试失败，跳过后续测试")
        return
    
    oss_path = upload_result.get('oss_path')
    
    # 测试2: 获取文件信息
    file_info = test_file_info(oss_path)
    
    # 测试3: 图像文件上传
    image_result = test_image_upload()
    
    # 测试4: 上传并插入到搜索索引
    insert_result = test_upload_and_insert()
    
    # 测试5: 删除文件
    delete_result = test_file_delete(oss_path)
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"✅ 基本文件上传: {'通过' if upload_result else '失败'}")
    print(f"✅ 文件信息查询: {'通过' if file_info else '失败'}")
    print(f"✅ 图像文件上传: {'通过' if image_result else '失败'}")
    print(f"✅ 上传并插入: {'通过' if insert_result else '失败'}")
    print(f"✅ 文件删除: {'通过' if delete_result else '失败'}")
    
    print("\n🎉 文件上传功能测试完成！")

if __name__ == "__main__":
    main() 