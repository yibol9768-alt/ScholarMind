#!/bin/bash
# ScholarMind 一键启动（桌面模式）
cd "$(dirname "$0")"
if [ -x "venv/bin/python" ]; then
  ./venv/bin/python desktop.py
else
  python desktop.py
fi
