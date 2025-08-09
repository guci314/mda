from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db
from .routers import books, readers, borrowings, reservations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    init_db()
    yield

app = FastAPI(title="图书借阅系统API", lifespan=lifespan)

# Include routers
app.include_router(books.router)
app.include_router(readers.router)
app.include_router(borrowings.router)
app.include_router(reservations.router)