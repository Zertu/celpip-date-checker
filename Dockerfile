FROM selenium/standalone-edge:latest

USER root

# 安装 Python 和依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制脚本
COPY celpip.py .

# 设置 Docker 环境变量
ENV DOCKER_ENV=true

# 运行脚本
CMD ["python3", "celpip.py"]