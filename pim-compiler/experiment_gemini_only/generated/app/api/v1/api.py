from fastapi import APIRouter

from app.api.v1.endpoints import users, articles, comments

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
# The comments router is included in the articles router for nested URLs
# but can be standalone if needed. We will include it under articles.
# api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
