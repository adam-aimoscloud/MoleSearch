#!/usr/bin/env python3
"""
真实API测试运行脚本
此脚本将启用真实的API测试，调用实际的阿里云DashScope API服务
"""

import os
import sys
import subprocess

def main():
    print("🔥 MMExtractor 真实API测试")
    print("=" * 60)
    print("⚠️  注意：此测试将调用真实的API服务，可能产生费用")
    print("⚠️  请确保您的API key配置正确且有足够的余额")
    print("=" * 60)
    
    # 设置环境变量
    os.environ['ENABLE_REAL_API_TESTS'] = 'true'
    
    # 运行测试
    print("\n🚀 开始运行真实API测试...")
    print("=" * 60)
    
    try:
        # 只运行真实API测试类
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 
            'mm_extractor_test.TestMMExtractorRealAPI',
            '-v'
        ], cwd=os.path.dirname(__file__), capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ 所有真实API测试通过！")
        else:
            print(f"\n❌ 测试失败，退出码: {result.returncode}")
            
    except Exception as e:
        print(f"\n❌ 运行测试时出错: {e}")
    
    print("\n" + "=" * 60)
    print("📊 测试完成")

if __name__ == '__main__':
    main() 