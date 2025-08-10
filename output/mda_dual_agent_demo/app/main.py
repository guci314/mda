from fastapi import FastAPI
from .database import engine
from . import models
from .routers import articles, categories, comments

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(comments.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API"}