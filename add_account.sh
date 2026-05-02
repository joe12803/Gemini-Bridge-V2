#!/bin/bash

# 配置路径
BASE_DIR="/home/joe1280/gemini-bridge-v2"
ACCOUNTS_FILE="$BASE_DIR/gemini_accounts.json"
RELOAD_URL="http://localhost:18888/reload"

echo "------------------------------------------"
echo "   Gemini Bridge V2 账号添加工具"
echo "------------------------------------------"

# 1. 输入账号 ID
read -p "请输入账号标识 (例如 acc6): " ACC_ID
if [ -z "$ACC_ID" ]; then
    echo "错误: ID 不能为空"
    exit 1
fi

# 2. 输入 Cookie
echo "请输入完整的 Cookie 字符串 (直接粘贴，回车结束):"
read -r COOKIES

if [ -z "$COOKIES" ]; then
    echo "错误: Cookie 不能为空"
    exit 1
fi

# 3. 输入代理 (可选)
read -p "请输入代理地址 (可选，留空则不使用): " PROXY

# 4. 使用 Python 安全地注入 JSON，防止手动编辑导致的语法错误
python3 -c "
import json
import sys

filepath = '$ACCOUNTS_FILE'
new_acc = {
    'id': '$ACC_ID',
    'cookies': '$COOKIES',
    'proxy': '$PROXY'
}

try:
    with open(filepath, 'r') as f:
        accounts = json.load(f)
except Exception:
    accounts = []

# 检查是否已存在同名 ID
accounts = [a for a in accounts if a['id'] != '$ACC_ID']
accounts.append(new_acc)

with open(filepath, 'w') as f:
    json.dump(accounts, f, indent=2)
"

if [ $? -eq 0 ]; then
    echo "------------------------------------------"
    echo "✅ 账号 $ACC_ID 已成功写入配置文件。"
    
    # 5. 尝试自动重载
    echo "正在通知后端重载配置..."
    RELOAD_RES=$(curl -s $RELOAD_URL)
    if [[ $RELOAD_RES == *"\"status\":\"ok\""* ]]; then
        COUNT=$(echo $RELOAD_RES | grep -oP '(?<="count":)\d+')
        echo "🚀 重载成功！当前有效账号总数: $COUNT"
    else
        echo "⚠️ 重载请求失败，可能服务未启动。你可以稍后手动执行: curl $RELOAD_URL"
    fi
else
    echo "❌ 写入失败，请检查文件权限。"
fi
