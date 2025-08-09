from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db
from .routers import books, readers

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="图书借阅系统API", lifespan=lifespan)

app.include_router(books.router)
app.include_router(readers.router)