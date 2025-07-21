"""
API endpoints for todos.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.database import get_db
from ..services.todo_service import TodoService

router = APIRouter()
todo_service = TodoService()


@router.post(
    "/",
    response_model=schemas.Todo,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
)
def create_todo(
    todo_create: schemas.TodoCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new todo item.
    - **title**: The title of the todo.
    - **description**: An optional description.
    """
    return todo_service.create_todo(db=db, todo_create=todo_create)


@router.get(
    "/",
    response_model=List[schemas.Todo],
    summary="Retrieve all todos"
)
def get_all_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get a list of all todo items.
    Supports pagination via `skip` and `limit` query parameters.
    """
    todos = todo_service.get_all_todos(db, skip=skip, limit=limit)
    return todos


@router.get(
    "/{todo_id}",
    response_model=schemas.Todo,
    summary="Get a specific todo by ID"
)
def get_todo_by_id(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single todo item by its unique ID.
    """
    db_todo = todo_service.get_todo_by_id(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return db_todo


@router.patch(
    "/{todo_id}",
    response_model=schemas.Todo,
    summary="Update a todo"
)
def update_todo(
    todo_id: int,
    todo_update: schemas.TodoUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing todo item.
    Can update `title`, `description`, and `status`.
    """
    db_todo = todo_service.get_todo_by_id(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    updated_todo = todo_service.update_todo(db=db, todo=db_todo, todo_update=todo_update)
    return updated_todo


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo"
)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a todo item by its unique ID.
    """
    deleted_todo = todo_service.delete_todo(db, todo_id=todo_id)
    if deleted_todo is None:
        # Even if it didn't exist, from a REST perspective, the resource is gone.
        # So we don't raise a 404 here, we just return 204.
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)
