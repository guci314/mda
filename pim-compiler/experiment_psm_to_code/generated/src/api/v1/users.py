from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from loguru import logger

from src.core.database import get_db
from src.schemas.user import UserCreate, UserResponse
from src.services.user_service import UserService

router = APIRouter()

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user with a unique email and username.",
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.

    - **email**: A valid email address.
    - **username**: A unique username (3-50 chars, letters, numbers, underscore).
    - **password**: Minimum 8 characters.
    """
    user_service = UserService(db)
    try:
        logger.info(f"Attempting to create user with email: {user_data.email}")
        new_user = await user_service.create_user(user_data)
        logger.info(f"Successfully created user with ID: {new_user.id}")
        return new_user
    except IntegrityError as e:
        logger.warning(f"Failed to create user. Conflict: {e.args[0]}")
        detail = "A user with this email or username already exists."
        if "Email already registered" in e.args[0]:
            detail = "A user with this email already exists."
        elif "Username already taken" in e.args[0]:
            detail = "A user with this username already exists."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred.",
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    description="Retrieves details for a specific user by their unique ID.",
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single user by their ID.
    """
    user_service = UserService(db)
    logger.info(f"Attempting to retrieve user with ID: {user_id}")
    db_user = await user_service.get_user_by_id(user_id)
    if db_user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Successfully retrieved user with ID: {user_id}")
    return db_user
