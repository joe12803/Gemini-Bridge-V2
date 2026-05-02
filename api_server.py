import os
import json
import uuid
import time
import random
import logging
import httpx
import asyncio
import subprocess
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- Configuration ---
ACCOUNTS_FILE = "gemini_accounts.json"
LOG_FILE = "gemini_bridge.log"
BACKEND_BIN = "./geminiweb2api"
BACKEND_PORT = 18889 # Internal backend port

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("gemini-bridge")

app = FastAPI(title="Gemini OpenAI Bridge V2")

class AccountManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.accounts = []
        self.load_accounts()
        self.backend_process = None

    def load_accounts(self):
        try:
            with open(self.filepath, 'r') as f:
                self.accounts = json.load(f)
            logger.info(f"Loaded {len(self.accounts)} accounts.")
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
            self.accounts = []

    def get_account(self):
        if not self.accounts:
            return None
        return random.choice(self.accounts)

    def remove_account(self, account_id):
        self.accounts = [a for a in self.accounts if a['id'] != account_id]
        with open(self.filepath, 'w') as f:
            json.dump(self.accounts, f, indent=2)
        logger.warning(f"Account {account_id} removed due to failure.")

    def ensure_backend(self):
        """Start geminiweb2api backend if not running"""
        if self.backend_process and self.backend_process.poll() is None:
            return
        
        logger.info("Starting geminiweb2api backend...")
        # Note: geminiweb2api seems to use 'port' in config or 8080 by default. 
        # But we want to override it. Let's check if it accepts -port or we need to write config.
        # Based on log, it says 8080.
        cmd = [BACKEND_BIN] 
        # Let's write a temporary config.json to force port 18889
        config = {
            "port": BACKEND_PORT,
            "proxy": "",
            "base_url": "https://gemini.google.com"
        }
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"), "w") as f:
            json.dump(config, f)

        self.backend_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        time.sleep(3) # Wait for startup

account_manager = AccountManager(ACCOUNTS_FILE)

@app.on_event("startup")
async def startup_event():
    account_manager.ensure_backend()

@app.on_event("shutdown")
async def shutdown_event():
    if account_manager.backend_process:
        account_manager.backend_process.terminate()

# --- OpenAI-like Models ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    tools: Optional[List[Dict[str, Any]]] = None

# --- Constants for Tool Injection ---
TOOL_INSTRUCTION = """
# Tool Use Protocol
You have access to tools. If you need to use a tool, wrap your request in:
<tool_call>
{"name": "tool_name", "arguments": {"arg1": "val1"}}
</tool_call>
The user will provide the tool result in the next message as:
<tool_result>
...result...
</tool_result>
"""

def inject_tool_instruction(messages: List[ChatMessage], tools: List[Dict]) -> List[Dict]:
    if not tools:
        return [m.dict() for m in messages]
    
    system_prompt = f"{TOOL_INSTRUCTION}\n\nAvailable tools:\n{json.dumps(tools, indent=2, ensure_ascii=False)}"
    new_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        new_messages.append(m.dict())
    return new_messages

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    acc = account_manager.get_account()
    if not acc:
        raise HTTPException(status_code=503, detail="No accounts available")

    # Injected prompt for function calling
    messages = inject_tool_instruction(request.messages, request.tools)
    
    # Map model ID
    target_model = "gemini-2.0-flash-exp" 
    
    payload = {
        "model": target_model,
        "messages": messages,
        "stream": request.stream,
        "cookies": acc['cookies'],
        "proxy": acc.get('proxy', '')
    }

    # Use our internal geminiweb2api backend
    backend_url = f"http://127.0.0.1:{BACKEND_PORT}/v1/chat/completions"

    async def stream_generator():
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream("POST", backend_url, json=payload) as response:
                    if response.status_code == 401 or response.status_code == 403:
                        account_manager.remove_account(acc['id'])
                        yield f"data: {json.dumps({'error': 'Account invalid, retrying...'})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if line:
                            yield f"{line}\n\n"
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

    if request.stream:
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(backend_url, json=payload)
            if response.status_code == 401 or response.status_code == 403:
                account_manager.remove_account(acc['id'])
                raise HTTPException(status_code=500, detail="Account error")
            return response.json()

@app.get("/reload")
async def reload_accounts():
    account_manager.load_accounts()
    return {"status": "ok", "count": len(account_manager.accounts)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18888)
