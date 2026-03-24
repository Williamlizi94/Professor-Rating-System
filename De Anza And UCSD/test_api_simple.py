"""
简单的API测试脚本
快速验证API是否正常工作
"""

import requests

BASE_URL = "http://localhost:8000"

def quick_test():
    """快速测试API是否正常运行"""
    print("正在测试API服务器...")
    print(f"目标地址: {BASE_URL}\n")
    
    tests = [
        ("首页", "/"),
        ("统计信息", "/stats?format=json"),
        ("部门列表", "/departments?format=json"),
        ("教授列表（前5条）", "/professors?format=json&limit=5"),
    ]
    
    for name, endpoint in tests:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✓ {name}: OK (状态码 {response.status_code})")
            else:
                print(f"✗ {name}: 失败 (状态码 {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"✗ {name}: 无法连接 - 请确保API服务器正在运行")
            print(f"  启动命令: python api.py")
            return False
        except Exception as e:
            print(f"✗ {name}: 错误 - {e}")
    
    print("\n✓ API测试完成！")
    return True

if __name__ == "__main__":
    quick_test()




