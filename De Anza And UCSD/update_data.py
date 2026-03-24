"""
自动更新数据脚本
用于定期运行数据抓取并更新JSON文件
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def update_professor_data():
    """
    运行数据抓取脚本并更新数据
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始更新数据...")
    
    try:
        # 运行数据抓取脚本
        result = subprocess.run(
            [sys.executable, "DeAnza_AllProfessors.py"],
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据更新成功")
            print(result.stdout)
            return True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据更新失败")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据更新超时")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 错误: {e}")
        return False


def send_reload_signal():
    """
    发送信号给API服务器重新加载数据
    通过HTTP请求触发数据重新加载
    """
    try:
        import requests
        response = requests.post("http://localhost:8000/reload", timeout=5)
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] API数据重新加载成功")
            return True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] API数据重新加载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 无法发送重载信号: {e}")
        return False


if __name__ == "__main__":
    success = update_professor_data()
    if success:
        send_reload_signal()


