"""
运行API服务器的脚本
支持后台运行和自动重启
"""

import subprocess
import sys
import os
import time
import signal

def run_api_server():
    """运行API服务器"""
    while True:
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 启动API服务器...")
            process = subprocess.Popen(
                [sys.executable, "api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 实时输出日志
            for line in process.stdout:
                print(line, end='')
            
            # 等待进程结束
            process.wait()
            
            if process.returncode != 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 服务器意外退出，等待5秒后重启...")
                time.sleep(5)
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 服务器正常退出")
                break
                
        except KeyboardInterrupt:
            print("\n正在关闭服务器...")
            if 'process' in locals():
                process.terminate()
            break
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误: {e}")
            print("等待5秒后重启...")
            time.sleep(5)


if __name__ == "__main__":
    run_api_server()


