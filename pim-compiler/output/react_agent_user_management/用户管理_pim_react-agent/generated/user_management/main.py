from fastapi import FastAPI
from .api.users import router as users_router
from .config.settings import settings

app = FastAPI(
    title="User Management System",
    description="A FastAPI-based user management service",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# Include routers
app.include_router(users_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)