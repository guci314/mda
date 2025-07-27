from fastapi import FastAPI
from .api.users import router as users_router
from .database import engine, Base

app = FastAPI()

# Include the router
app.include_router(users_router)

# Create database tables
Base.metadata.create_all(bind=engine)