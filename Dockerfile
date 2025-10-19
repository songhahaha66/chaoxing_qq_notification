FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装uv (Python包管理器)
RUN pip install uv

# 复制requirements文件
COPY requirements.txt .

# 使用uv安装依赖 (更快)
RUN uv venv
RUN uv pip install -r requirements.txt
RUN uv pip install "uvicorn[standard]"
# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 启动脚本
CMD ["./start.sh"]