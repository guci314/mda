from fastapi import FastAPI
from contextlib import asynccontextmanager
import database
from routers import book_router, reader_router, borrowing_router, reservation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(title="Library Borrowing System", lifespan=lifespan)

app.include_router(book_router.router, prefix="/api", tags=["books"])
app.include_router(reader_router.router, prefix="/api", tags=["readers"])
app.include_router(borrowing_router.router, prefix="/api", tags=["borrowing"])
app.include_router(reservation_router.router, prefix="/api", tags=["reservations"])
