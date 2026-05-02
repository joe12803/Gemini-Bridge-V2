# 使用轻量级 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (如有需要)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
# 虽然没写 requirements.txt，但我们直接装那几个核心依赖
RUN pip install --no-cache-dir httpx fastapi uvicorn pydantic

# 复制项目所有文件
COPY . .

# 确保二进制文件有执行权限
RUN chmod +x geminiweb2api add_account.sh setup.sh

# 暴露 Python Bridge 端口
EXPOSE 18888

# 启动程序
CMD ["python", "api_server.py"]
