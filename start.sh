#!/bin/bash

# 启动主程序
uv run main.py &

# 启动API服务
uv run uvicorn api:app --host 0.0.0.0 --port 8000 &

# 等待所有后台进程，防止容器退出
wait

