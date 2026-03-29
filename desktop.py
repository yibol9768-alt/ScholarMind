"""
ScholarMind 桌面应用启动器
启动 NiceGUI 服务并打开 pywebview 窗口
"""

import os
import sys
import socket
import subprocess
import time

import webview

APP_DIR = os.path.dirname(os.path.abspath(__file__))
TITLE = "ScholarMind"
WIDTH, HEIGHT = 1440, 900
HOST = "127.0.0.1"


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_for_server(host, port, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def main():
    port = find_free_port()
    env = os.environ.copy()

    print(f"Starting ScholarMind on port {port}...")
    process = subprocess.Popen(
        [sys.executable, os.path.join(APP_DIR, "main.py")],
        cwd=APP_DIR,
        env={**env, "NICEGUI_PORT": str(port)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # NiceGUI默认8080，通过环境变量不一定生效，直接用8080
    actual_port = 8080
    if not wait_for_server(HOST, actual_port):
        print("Server start timeout")
        process.terminate()
        sys.exit(1)

    print(f"Server ready at http://{HOST}:{actual_port}")

    window = webview.create_window(
        title=TITLE,
        url=f"http://{HOST}:{actual_port}",
        width=WIDTH,
        height=HEIGHT,
        resizable=True,
        min_size=(1024, 680),
        text_select=True,
    )

    def on_closed():
        print("Shutting down...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    window.events.closed += on_closed
    webview.start(debug=False)
    process.terminate()
    print("ScholarMind closed")


if __name__ == "__main__":
    main()
