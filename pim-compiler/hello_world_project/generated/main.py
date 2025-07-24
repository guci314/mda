from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import pytz

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 响应模型
class MessageResponse(BaseModel):
    message: str

class HelloResponse(BaseModel):
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@app.get("/", response_model=MessageResponse)
async def root():
    return {"message": "Hello World!"}

@app.get("/hello/{name}", response_model=HelloResponse)
async def say_hello(name: str):
    return {
        "message": f"Hello, {name}!",
        "timestamp": datetime.now(pytz.utc).isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "service": "hello-world-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)