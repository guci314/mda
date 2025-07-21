"""
Main API Router.

This module combines all the individual API routers from the 'auth' and 'users'
modules into a single main router for the application.
"""
from fastapi import APIRouter

from . import auth, users

api_router = APIRouter()

# Include the auth router with a specific prefix and tags
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include the users router with a specific prefix and tags
api_router.include_router(users.router, prefix="/users", tags=["Users"])
