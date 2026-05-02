
import os
import json
import random
import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

ACCOUNTS_FILE = "gemini_accounts.json"
LOG_FILE = "gemini_bridge.log"
BACKEND_PORT = 18889
API_KEY = "sk-gemini-bridge-2026"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)8s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("gemini-bridge")

app = FastAPI()

class AccountManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.accounts = []
        self.load()

    def load(self):
        try:
            with open(self.filepath, 'r') as f:
                self.accounts = json.load(f)
            logger.info(f"Loaded {len(self.accounts)} accounts")
        except:
            self.accounts = []

    def get(self):
        return random.choice(self.accounts) if self.accounts else None

    def remove(self, aid):
        self.accounts = [a for a in self.accounts if a['id'] != aid]
        with open(self.filepath, 'w') as f:
            json.dump(self.accounts, f, indent=2)
        logger.warning(f"Removed account {aid}")

am = AccountManager(ACCOUNTS_FILE)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False

@app.post("/v1/chat/completions")
async def chat(request: ChatCompletionRequest):
    acc = am.get()
    if not acc:
        am.load()
        acc = am.get()
        if not acc: raise HTTPException(status_code=503, detail="No accounts")

    payload = {
        "model": "gemini-3-flash",
        "messages": [m.dict() for m in request.messages],
        "stream": request.stream,
        "cookies": acc['cookies']
    }
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = f"http://127.0.0.1:{BACKEND_PORT}/v1/chat/completions"

    if request.stream:
        async def gen():
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as r:
                    if r.status_code == 401:
                        am.remove(acc['id'])
                        yield f"data: {{ 'error': '401' }}\\n\\n"
                        return
                    async for line in r.aiter_lines():
                        if line: yield f"{line}\\n\\n"
        return StreamingResponse(gen(), media_type="text/event-stream")
    else:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            if r.status_code == 401:
                am.remove(acc['id'])
                raise HTTPException(status_code=401, detail="Account error")
            return r.json()

@app.get("/reload")
async def reload():
    am.load()
    return {"count": len(am.accounts)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18888)
