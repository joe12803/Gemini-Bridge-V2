# Gemini Bridge V2 (OpenAI compatible)

这是一个基于 Python FastAPI 开发的 Gemini Web 逆向接口桥接层，旨在为 Gemini 提供标准的 OpenAI API 兼容性，并实现高性能的 Function Calling（工具调用）支持。

## 核心特性

- **OpenAI 格式兼容**：完全支持 `/v1/chat/completions` 接口，可直接接入 Cursor, Dify, Chatbox 等工具。
- **多账号轮询 (Load Balancing)**：支持 `gemini_accounts.json` 多账号池，请求随机分发。
- **自动化账号管理**：请求失败（401/403）时自动从内存和配置文件中剔除失效账号，确保高可用。
- **高级工具调用 (Function Calling)**：通过“指令注入 + 响应拦截”技术，在 Web 逆向接口上实现了闭环的工具调用能力，支持单次多工具调用。
- **热重载**：访问 `/reload` 接口即可在不重启服务的情况下更新账号配置。
- **流式输出**：支持标准的 Server-Sent Events (SSE) 流式响应。

## 快速开始

### 1. 安装依赖
```bash
pip install httpx fastapi uvicorn pydantic
```

### 2. 配置账号
编辑 `gemini_accounts.json`:
```json
[
  {
    "id": "acc1",
    "cookies": "YOUR_COOKIE_HERE",
    "proxy": ""
  }
]
```

### 3. 启动服务
```bash
python api_server.py
```
默认监听端口：`18888`

### 4. 手动管理账号
使用内置脚本快速添加账号：
```bash
gemini-add-acc
```

## API 端点

- `POST /v1/chat/completions` - 对话接口
- `GET /reload` - 重新加载账号配置
- `GET /health` - 健康检查

## 部署信息

- **Systemd 服务**: `gemini-api.service`
- **运行环境**: Python 3.10+
- **项目路径**: `/home/joe1280/gemini-bridge-v2`

## 开源协议
MIT
