"""
Service layer for handling todo-related business logic.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from .. import models, schemas
from ..models.todo import TodoStatus


class TodoService:
    """
    A service class for handling CRUD operations for Todo items.
    """

    def get_todo_by_id(self, db: Session, todo_id: int) -> Optional[models.Todo]:
        """
        Retrieves a single todo item by its ID.

        Args:
            db: The database session.
            todo_id: The ID of the todo to retrieve.

        Returns:
            The Todo model instance if found, otherwise None.
        """
        return db.get(models.Todo, todo_id)

    def get_all_todos(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Todo]:
        """
        Retrieves a list of all todo items with pagination.

        Args:
            db: The database session.
            skip: The number of items to skip.
            limit: The maximum number of items to return.

        Returns:
            A list of Todo model instances.
        """
        statement = select(models.Todo).offset(skip).limit(limit)
        return db.execute(statement).scalars().all()

    def create_todo(self, db: Session, todo_create: schemas.TodoCreate) -> models.Todo:
        """
        Creates a new todo item.

        Args:
            db: The database session.
            todo_create: The Pydantic schema with the todo creation data.

        Returns:
            The newly created Todo model instance.
        """
        db_todo = models.Todo(
            title=todo_create.title,
            description=todo_create.description,
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def update_todo(
        self, db: Session, todo: models.Todo, todo_update: schemas.TodoUpdate
    ) -> models.Todo:
        """
        Updates an existing todo item.

        Args:
            db: The database session.
            todo: The existing Todo model instance to update.
            todo_update: The Pydantic schema with the update data.

        Returns:
            The updated Todo model instance.
        """
        update_data = todo_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(todo, field, value)

        # Special handling for status change
        if "status" in update_data and update_data["status"] == TodoStatus.COMPLETED:
            if todo.completed_at is None:
                todo.completed_at = datetime.utcnow()
        elif "status" in update_data and update_data["status"] == TodoStatus.PENDING:
            todo.completed_at = None

        db.commit()
        db.refresh(todo)
        return todo

    def delete_todo(self, db: Session, todo_id: int) -> Optional[models.Todo]:
        """
        Deletes a todo item by its ID.

        Args:
            db: The database session.
            todo_id: The ID of the todo to delete.

        Returns:
            The deleted Todo model instance if found and deleted, otherwise None.
        """
        db_todo = self.get_todo_by_id(db, todo_id)
        if db_todo:
            db.delete(db_todo)
            db.commit()
        return db_todo
