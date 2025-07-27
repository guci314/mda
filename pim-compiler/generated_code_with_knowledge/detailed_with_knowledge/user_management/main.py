from fastapi import FastAPI
from .database import engine, Base
from .api.routes import users

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="User Management System")

# Register routes
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "User Management System API"}