from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import get_db

app = FastAPI()

@app.get("/hello")
def say_hello(db: Session = Depends(get_db)): # Changed models.Config to .models.Config and get_db to .database.get_db
    # 从数据库中获取配置信息
    config = db.query(models.Config).filter(models.Config.service_name == "hello-world").first()
    if config:
        return {"message": f"Hello World! (Version: {config.version})"}
    else:
        return {"message": "Hello World!"}