# Gemini Bridge V2 (OpenAI compatible)

这是一个基于 Python FastAPI 开发的 Gemini Web 逆向接口桥接层，旨在为 Gemini 提供标准的 OpenAI API 兼容性，并实现高性能的 Function Calling（工具调用）支持。

## 🛠 核心特性

- **OpenAI 格式兼容**：完全支持 `/v1/chat/completions` 接口，可直接接入 Cursor, Dify, Chatbox 等工具。
- **内置后端引擎**：自动管理并运行 [geminiweb2api](https://github.com/XxxXTeam/geminiweb2api) 核心，无需手动配置多个 Docker。
- **多账号轮询 (Load Balancing)**：支持 `gemini_accounts.json` 多账号池，请求随机分发。
- **自动化账号管理**：请求失败（401/403）时自动从内存和配置文件中剔除失效账号，确保高可用。
- **高级工具调用 (Function Calling)**：通过“指令注入 + 响应拦截”技术，实现了闭合的工具调用能力。
- **热重载**：访问 `/reload` 接口即可在不重启服务的情况下更新账号配置。

## 🚀 部署方案

### 方案一：Docker 部署 (推荐，最快)

> **注意**：当前预构建镜像适用于 **ARM64** 架构 (如 Oracle ARM, Apple Silicon)。如果是 x86_64 环境，请使用方案二自行构建。

直接运行预构建镜像，无需配置 Python 或 Go 环境：

```bash
docker run -d \
  --name gemini-bridge-v2 \
  -p 18888:18888 \
  -v $(pwd)/gemini_accounts.json:/app/gemini_accounts.json \
  -v $(pwd)/gemini_bridge.log:/app/gemini_bridge.log \
  joe1280/gemini-bridge-v2:latest
```

或者使用 `docker-compose.yml`:
```bash
docker-compose up -d
```

### 方案二：源码手动部署

1. **克隆并安装依赖**
```bash
git clone https://github.com/joe12803/Gemini-Bridge-V2.git
cd Gemini-Bridge-V2
pip install httpx fastapi uvicorn pydantic
```

2. **二进制文件说明**
源码仓库中已包含 `geminiweb2api` 二进制文件 (适用于 **Linux ARM64**)。如果在 **x86_64** 环境下运行，请务必从原项目 [XxxXTeam/geminiweb2api](https://github.com/XxxXTeam/geminiweb2api) 重新下载对应的二进制文件进行替换。

3. **配置账号**
你可以直接编辑 `gemini_accounts.json`，或者使用交互式脚本添加：
```bash
bash add_account.sh
```

4. **启动服务**
```bash
python api_server.py
```
服务默认运行在 `http://localhost:18888`。

## 📂 项目结构

- `api_server.py`: Python 桥接主程序，处理 OpenAI 协议映射与工具调用逻辑。
- `geminiweb2api`: 内置的 Go 后端二进制执行文件。
- `gemini_accounts.json`: 账号池配置文件。
- `add_account.sh`: 账号交互式添加脚本。
- `Dockerfile` & `docker-compose.yml`: 容器化配置文件。

## 🧪 测试与使用

你可以直接使用 `curl` 快速验证服务状态：

### 1. 基础对话
```bash
curl -X POST http://localhost:18888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": false
  }'
```

### 2. 工具调用 (Function Calling)
```bash
curl -X POST http://localhost:18888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [{"role": "user", "content": "帮我查一下北京的天气"}],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "获取天气信息",
          "parameters": {
            "type": "object",
            "properties": { "location": {"type": "string"} }
          }
        }
      }
    ]
  }'
```

### 3. 配置热重载
```bash
curl http://localhost:18888/reload
```

## 开源协议
MIT
