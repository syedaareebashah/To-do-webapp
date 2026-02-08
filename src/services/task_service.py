"""
Task Service for Todo AI Chatbot System

This module provides business logic for task-related operations.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from src.models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from src.database.session import get_session


class TaskService:
    """
    Service class for handling task-related operations.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the task service with a database session.

        Args:
            db_session (Session): Database session for operations
        """
        self.db = db_session

    def create(self, obj_in: TaskCreate) -> Task:
        """
        Create a new task.

        Args:
            obj_in (TaskCreate): Data for creating the task

        Returns:
            Task: The created task object
        """
        # Create a new Task instance from the input data
        db_obj = Task(
            user_id=obj_in.user_id,
            content=obj_in.content,
            status=obj_in.status if obj_in.status else TaskStatus.PENDING,
            due_date=obj_in.due_date,
            priority=obj_in.priority
        )

        # Add to database
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def get_by_id_and_user(self, task_id: UUID, user_id: str) -> Optional[Task]:
        """
        Get a specific task by its ID and user ID.

        Args:
            task_id (UUID): ID of the task to retrieve
            user_id (str): ID of the user who owns the task

        Returns:
            Optional[Task]: The task if found and owned by user, None otherwise
        """
        import uuid
        # Convert string user_id to UUID for comparison
        user_uuid = uuid.UUID(user_id)
        
        # Query for task that belongs to the specified user
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_uuid
        )
        task = self.db.exec(statement).first()
        return task

    def get_tasks_by_user(self, user_id: str, status_filter: Optional[str] = None, limit: int = 50) -> List[Task]:
        """
        Get all tasks for a specific user with optional filtering.

        Args:
            user_id (str): ID of the user whose tasks to retrieve
            status_filter (Optional[str]): Filter by status (pending, completed, etc.)
            limit (int): Maximum number of tasks to return (default: 50)

        Returns:
            List[Task]: List of tasks matching the criteria
        """
        import uuid
        # Convert string user_id to UUID for comparison
        user_uuid = uuid.UUID(user_id)
        
        # Start with base query for user's tasks
        statement = select(Task).where(Task.user_id == user_uuid)

        # Apply status filter if specified
        if status_filter:
            if status_filter.lower() == "completed":
                statement = statement.where(Task.status == TaskStatus.COMPLETED)
            elif status_filter.lower() == "pending":
                statement = statement.where(Task.status == TaskStatus.PENDING)

        # Add ordering by creation date and limit
        statement = statement.order_by(Task.created_at.desc()).limit(limit)

        tasks = self.db.exec(statement).all()
        return tasks

    def update(self, db_obj: Task, obj_in: TaskUpdate) -> Task:
        """
        Update an existing task.

        Args:
            db_obj (Task): The existing task object to update
            obj_in (TaskUpdate): Updated task data

        Returns:
            Task: The updated task object
        """
        # Update fields from the input data
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # If status is being updated to completed and completed_at is not set, set it
        if (hasattr(obj_in, 'status') and
            obj_in.status == TaskStatus.COMPLETED and
            not db_obj.completed_at):
            db_obj.completed_at = datetime.utcnow()

        # Commit changes
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def remove(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Remove a task by its ID and user ID.

        Args:
            task_id (str): ID of the task to remove (will be converted to UUID)
            user_id (str): ID of the user who owns the task

        Returns:
            Optional[Task]: The removed task if successful, None otherwise
        """
        import uuid
        # Convert string IDs to UUIDs
        task_uuid = uuid.UUID(task_id)
        
        # Get the task
        task = self.get_by_id_and_user(task_uuid, user_id)
        if not task:
            return None

        # Remove the task
        self.db.delete(task)
        self.db.commit()

        return task

    def complete_task(self, task_id: UUID, user_id: str) -> Optional[Task]:
        """
        Mark a task as completed.

        Args:
            task_id (UUID): ID of the task to complete
            user_id (str): ID of the user who owns the task

        Returns:
            Optional[Task]: The updated task if successful, None otherwise
        """
        # Get the task
        task = self.get_by_id_and_user(task_id, user_id)
        if not task:
            return None

        # Update task status to completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()

        # Commit changes
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def create_task(self, task_create: TaskCreate) -> Task:
        """
        Create a new task with user validation.

        Args:
            task_create (TaskCreate): Task creation data

        Returns:
            Task: The created task object
        """
        return self.create(task_create)

    def update_task_status(self, task_id: str, user_id: str, new_status: str) -> Optional[Task]:
        """
        Update the status of a task.

        Args:
            task_id (str): ID of the task to update (will be converted to UUID)
            user_id (str): ID of the user who owns the task
            new_status (str): New status for the task ('pending' or 'completed')

        Returns:
            Optional[Task]: The updated task if successful, None otherwise
        """
        import uuid
        # Convert string IDs to UUIDs
        task_uuid = uuid.UUID(task_id)
        
        task = self.get_by_id_and_user(task_uuid, user_id)
        if not task:
            return None

        # Convert string status to enum
        status_enum = TaskStatus(new_status.lower())

        # Update the task
        update_data = TaskUpdate(status=status_enum)
        updated_task = self.update(task, update_data)
        return updated_task

    def delete_task(self, task_id: UUID, user_id: str) -> Optional[Task]:
        """
        Delete a task by its ID and user ID.

        Args:
            task_id (UUID): ID of the task to delete
            user_id (str): ID of the user who owns the task

        Returns:
            Optional[Task]: The deleted task if successful, None otherwise
        """
        return self.remove(task_id, user_id)

    def partial_update_task(self, task_id: str, user_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """
        Partially update a task by its ID and user ID.

        Args:
            task_id (str): ID of the task to update (will be converted to UUID)
            user_id (str): ID of the user who owns the task
            task_update (TaskUpdate): Update data for the task

        Returns:
            Optional[Task]: The updated task if successful, None otherwise
        """
        import uuid
        # Convert string IDs to UUIDs
        task_uuid = uuid.UUID(task_id)
        
        task = self.get_by_id_and_user(task_uuid, user_id)
        if not task:
            return None

        updated_task = self.update(task, task_update)
        return updated_task