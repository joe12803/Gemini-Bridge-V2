# Gemini Bridge V2 (OpenAI compatible)

这是一个基于 Python FastAPI 开发的 Gemini Web 逆向接口桥接层，旨在为 Gemini 提供标准的 OpenAI API 兼容性，并实现高性能的 Function Calling（工具调用）支持。

## 🛠 核心特性

- **OpenAI 格式兼容**：完全支持 `/v1/chat/completions` 接口，可直接接入 Cursor, Dify, Chatbox 等工具。
- **内置后端引擎**：自动管理并运行 [geminiweb2api](https://github.com/XxxXTeam/geminiweb2api) 核心，无需手动配置多个 Docker。
- **多账号轮询 (Load Balancing)**：支持 `gemini_accounts.json` 多账号池，请求随机分发。
- **自动化账号管理**：请求失败（401/403）时自动从内存和配置文件中剔除失效账号，确保高可用。
- **高级工具调用 (Function Calling)**：通过“指令注入 + 响应拦截”技术，实现了闭合的工具调用能力。
- **热重载**：访问 `/reload` 接口即可在不重启服务的情况下更新账号配置。

## 🚀 快速开始

### 1. 克隆并安装依赖
```bash
git clone https://github.com/joe12803/Gemini-Bridge-V2.git
cd Gemini-Bridge-V2
pip install httpx fastapi uvicorn pydantic
```

### 2. 获取后端二进制文件 (重要)
由于本项目依赖于 Go 编写的后端引擎，你需要在项目根目录下放置一个编译好的 `geminiweb2api` 二进制文件。
- **方案 A (推荐)**：从原项目 [XxxXTeam/geminiweb2api](https://github.com/XxxXTeam/geminiweb2api) 下载 Release 或自行编译。
- **方案 B (如果你在本地已有)**：运行 `./setup.sh`，脚本会尝试从常见目录自动拷贝。

确保文件具有执行权限：
```bash
chmod +x geminiweb2api
```

### 3. 配置账号
你可以直接编辑 `gemini_accounts.json`，或者使用交互式脚本添加：
```bash
bash add_account.sh
```

### 4. 启动服务
```bash
python api_server.py
```
服务默认运行在 `http://localhost:18888`。

## 📂 项目结构

- `api_server.py`: Python 桥接主程序，处理 OpenAI 协议映射与工具调用逻辑。
- `geminiweb2api`: (需手动放入) Go 后端二进制执行文件。
- `gemini_accounts.json`: 账号池配置文件。
- `add_account.sh`: 账号交互式添加脚本。
- `setup.sh`: 环境初始化辅助脚本。

## ⚠️ 常见问题
1. **端口冲突**：本项目会同时占用 `18888` (Python) 和 `18889` (Go Backend) 端口。
2. **账号失效**：如果日志显示 "Account removed"，说明该账号的 Cookie 已失效，请重新获取。

## 开源协议
MIT
