"""
ScholarMind 桌面应用启动器
基于 pywebview 的独立窗口应用，内嵌 Streamlit 服务
"""

import os
import sys
import signal
import socket
import subprocess
import threading
import time

import webview


APP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_TITLE = "ScholarMind - 智能文献分析系统"
WIDTH = 1440
HEIGHT = 900
HOST = "127.0.0.1"


def find_free_port() -> int:
    """找一个可用端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_for_server(host: str, port: int, timeout: int = 30) -> bool:
    """等待 Streamlit 服务启动"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


class StreamlitServer:
    """管理 Streamlit 子进程"""

    def __init__(self):
        self.process = None
        self.port = find_free_port()

    def start(self):
        env = os.environ.copy()
        env["STREAMLIT_SERVER_HEADLESS"] = "true"
        env["STREAMLIT_SERVER_PORT"] = str(self.port)
        env["STREAMLIT_SERVER_ADDRESS"] = HOST
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        env["STREAMLIT_THEME_BASE"] = "light"

        self.process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run",
                os.path.join(APP_DIR, "app.py"),
                "--server.headless=true",
                f"--server.port={self.port}",
                f"--server.address={HOST}",
                "--browser.gatherUsageStats=false",
                "--theme.base=light",
            ],
            cwd=APP_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return wait_for_server(HOST, self.port)

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    @property
    def url(self):
        return f"http://{HOST}:{self.port}"


def main():
    server = StreamlitServer()

    # 在后台线程启动 Streamlit
    print(f"正在启动 ScholarMind 服务 (端口 {server.port})...")
    ready = server.start()

    if not ready:
        print("错误：Streamlit 服务启动超时")
        server.stop()
        sys.exit(1)

    print(f"服务已就绪: {server.url}")
    print("正在打开桌面窗口...")

    # 创建桌面窗口
    window = webview.create_window(
        title=APP_TITLE,
        url=server.url,
        width=WIDTH,
        height=HEIGHT,
        resizable=True,
        min_size=(1024, 680),
        text_select=True,
    )

    def on_closed():
        print("正在关闭服务...")
        server.stop()

    window.events.closed += on_closed

    # 启动 GUI 主循环
    webview.start(debug=False)

    # 确保子进程退出
    server.stop()
    print("ScholarMind 已关闭")


if __name__ == "__main__":
    main()
