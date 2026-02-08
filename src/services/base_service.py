"""
Base service layer module for the Todo AI Chatbot System.

This module defines the base service class with common database operations.
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlmodel import Session, SQLModel, select, and_, or_
from sqlalchemy import func
from uuid import UUID


# Generic type variable for models
ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseService(ABC, Generic[ModelType]):
    """
    Base service class providing common database operations for all models.

    Attributes:
        model (Type[SQLModel]): The SQLModel class this service handles
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the base service with a specific model.

        Args:
            model (Type[ModelType]): The SQLModel class this service handles
        """
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """
        Get a record by its ID.

        Args:
            db (Session): Database session
            id (UUID): ID of the record to retrieve

        Returns:
            Optional[ModelType]: The record if found, None otherwise
        """
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with optional filtering, pagination.

        Args:
            db (Session): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            filters (Optional[Dict[str, Any]]): Filters to apply

        Returns:
            List[ModelType]: List of records
        """
        query = select(self.model)

        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    attr = getattr(self.model, field)
                    if isinstance(value, list):
                        conditions.append(attr.in_(value))
                    else:
                        conditions.append(attr == value)

            if conditions:
                query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        return db.exec(query).all()

    def create(self, db: Session, *, obj_in: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            db (Session): Database session
            obj_in (ModelType): The object to create

        Returns:
            ModelType: The created object
        """
        db_obj = obj_in
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: ModelType
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db (Session): Database session
            db_obj (ModelType): The existing object to update
            obj_in (ModelType): The updated object

        Returns:
            ModelType: The updated object
        """
        # Update attributes from obj_in to db_obj
        for field in obj_in.__fields__:
            if hasattr(obj_in, field) and hasattr(db_obj, field):
                setattr(db_obj, field, getattr(obj_in, field))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> ModelType:
        """
        Remove a record by its ID.

        Args:
            db (Session): Database session
            id (UUID): ID of the record to remove

        Returns:
            ModelType: The removed object
        """
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session, *, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.

        Args:
            db (Session): Database session
            filters (Optional[Dict[str, Any]]): Filters to apply

        Returns:
            int: Count of matching records
        """
        query = select(self.model)

        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    attr = getattr(self.model, field)
                    if isinstance(value, list):
                        conditions.append(attr.in_(value))
                    else:
                        conditions.append(attr == value)

            if conditions:
                query = query.where(and_(*conditions))

        subq = query.subquery()
        return db.exec(select(func.count()).select_from(subq)).one()