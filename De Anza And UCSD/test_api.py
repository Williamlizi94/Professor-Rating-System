"""
API测试文件
用于测试所有API端点的功能
"""

import requests
import json
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"


def test_root():
    """测试根端点"""
    print("\n" + "="*50)
    print("测试: GET /")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        if response.headers.get('content-type', '').startswith('text/html'):
            print("✓ 返回HTML页面（正常）")
        else:
            data = response.json()
            print(f"✓ 返回JSON数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_professors(page=1, limit=5):
    """测试获取教授列表"""
    print("\n" + "="*50)
    print(f"测试: GET /professors?page={page}&limit={limit}")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/professors?format=json&page={page}&limit={limit}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 总教授数: {data.get('total', 0)}")
        print(f"✓ 当前页: {data.get('page', 0)}")
        print(f"✓ 每页数量: {data.get('limit', 0)}")
        print(f"✓ 返回数据条数: {len(data.get('data', []))}")
        if data.get('data'):
            first_prof = data['data'][0]
            print(f"✓ 第一条数据示例: {first_prof.get('Full_Name', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_professor_by_name(name="Smith"):
    """测试按姓名搜索"""
    print("\n" + "="*50)
    print(f"测试: GET /professors/name/{name}")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/professors/name/{name}?format=json")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 找到教授数: {data.get('count', 0)}")
        if data.get('data'):
            print(f"✓ 第一个匹配: {data['data'][0].get('Full_Name', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        if hasattr(e, 'response') and e.response.status_code == 404:
            print("  (404是正常的，如果该姓名不存在)")
        return False


def test_professor_by_department(department="Mathematics"):
    """测试按部门获取"""
    print("\n" + "="*50)
    print(f"测试: GET /professors/department/{department}")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/professors/department/{department}?format=json&limit=5")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 部门: {data.get('department', 'N/A')}")
        print(f"✓ 总教授数: {data.get('total', 0)}")
        print(f"✓ 返回数据条数: {len(data.get('data', []))}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        if hasattr(e, 'response') and e.response.status_code == 404:
            print("  (404是正常的，如果该部门不存在)")
        return False


def test_search(query="math"):
    """测试搜索"""
    print("\n" + "="*50)
    print(f"测试: GET /search?q={query}")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/search?q={query}&format=json&limit=5")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 搜索关键词: {data.get('query', 'N/A')}")
        print(f"✓ 总结果数: {data.get('total', 0)}")
        print(f"✓ 返回数据条数: {len(data.get('data', []))}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_stats():
    """测试统计信息"""
    print("\n" + "="*50)
    print("测试: GET /stats")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/stats?format=json")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 总教授数: {data.get('total_professors', 0)}")
        print(f"✓ 总评价数: {data.get('total_reviews', 0)}")
        print(f"✓ 部门数: {data.get('departments', {}).get('count', 0)}")
        print(f"✓ 平均评分: {data.get('ratings', {}).get('average', 0):.2f}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_departments():
    """测试部门列表"""
    print("\n" + "="*50)
    print("测试: GET /departments")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/departments?format=json")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 部门总数: {data.get('count', 0)}")
        depts = data.get('departments', [])
        if depts:
            print(f"✓ 前5个部门: {', '.join(depts[:5])}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_reload():
    """测试重新加载数据"""
    print("\n" + "="*50)
    print("测试: POST /reload")
    print("="*50)
    try:
        response = requests.post(f"{BASE_URL}/reload")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 状态: {data.get('status', 'N/A')}")
        print(f"✓ 消息: {data.get('message', 'N/A')}")
        print(f"✓ 时间戳: {data.get('timestamp', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_with_filters():
    """测试带筛选条件的查询"""
    print("\n" + "="*50)
    print("测试: GET /professors (带筛选条件)")
    print("="*50)
    try:
        url = f"{BASE_URL}/professors?format=json&department=Mathematics&min_rating=4.0&limit=5"
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"✓ 筛选结果总数: {data.get('total', 0)}")
        print(f"✓ 返回数据条数: {len(data.get('data', []))}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("De Anza College Professors API - 完整测试")
    print("="*60)
    print(f"测试目标: {BASE_URL}")
    print("\n注意: 请确保API服务器正在运行！")
    
    results = []
    
    # 运行所有测试
    results.append(("根端点", test_root()))
    results.append(("获取教授列表", test_professors()))
    results.append(("按姓名搜索", test_professor_by_name("Smith")))
    results.append(("按部门获取", test_professor_by_department("Mathematics")))
    results.append(("搜索功能", test_search("math")))
    results.append(("统计信息", test_stats()))
    results.append(("部门列表", test_departments()))
    results.append(("重新加载数据", test_reload()))
    results.append(("筛选查询", test_with_filters()))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20s}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/stats?format=json", timeout=2)
        print("✓ API服务器正在运行\n")
    except Exception as e:
        print("✗ 错误: API服务器未运行或无法访问")
        print(f"  请先启动API服务器: python api.py")
        print(f"  或访问: {BASE_URL}")
        exit(1)
    
    # 运行测试
    success = run_all_tests()
    exit(0 if success else 1)




