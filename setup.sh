#!/bin/bash

# Gemini Bridge V2 一键环境准备脚本

echo "开始准备 Gemini Bridge V2 环境..."

# 1. 检查 Python 依赖
pip install httpx fastapi uvicorn pydantic

# 2. 获取 geminiweb2api 二进制文件 (尝试从本地已存在的路径获取)
if [ -f "/usr/local/bin/geminiweb2api" ]; then
    cp /usr/local/bin/geminiweb2api ./
    echo "✅ 已从系统路径同步 geminiweb2api"
elif [ -f "/opt/geminiweb2api/geminiweb2api" ]; then
    cp /opt/geminiweb2api/geminiweb2api ./
    echo "✅ 已从 /opt 目录同步 geminiweb2api"
else
    echo "⚠️ 未找到本地二进制文件，请手动将 geminiweb2api 编译好的文件放置在项目根目录。"
    echo "参考项目: https://github.com/XxxXTeam/geminiweb2api"
fi

# 3. 设置权限
chmod +x ./geminiweb2api
chmod +x ./add_account.sh

echo "------------------------------------------"
echo "✅ 环境准备完成！"
echo "你可以通过执行 'python api_server.py' 启动服务。"
echo "或者使用 'gemini-add-acc' 添加账号。"
echo "------------------------------------------"
