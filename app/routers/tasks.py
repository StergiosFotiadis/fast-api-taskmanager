from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db import get_session
from app.models import Tasks, User, Category
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # If a category_id is provided, verify it belongs to the current user (IDOR prevention)
    if data.category_id is not None:
        category = db.query(Category).filter(
            Category.id == data.category_id,
            Category.owner_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    try:
        new_task = Tasks(
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            is_completed=data.is_completed or False,
            category_id=data.category_id
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception:
        db.rollback()
        logger.exception("Failed to create task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the task."
        )


@router.get("/", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(
    category_id: Optional[int] = Query(default=None, description="Filter tasks by category ID"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # If filtering by category, verify the category belongs to the current user (IDOR prevention)
    if category_id is not None:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.owner_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    query = db.query(Tasks).filter(Tasks.user_id == current_user.id)
    if category_id is not None:
        query = query.filter(Tasks.category_id == category_id)
    return query.all()


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(
    task_id: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == current_user.id
    ).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task


@router.delete("/completed", status_code=status.HTTP_200_OK)
def delete_completed_tasks(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        deleted = db.query(Tasks).filter(
            Tasks.user_id == current_user.id,
            Tasks.is_completed == True  # noqa: E712
        ).delete(synchronize_session=False)
        db.commit()
        return {"deleted": deleted}
    except Exception:
        db.rollback()
        logger.exception("Failed to delete completed tasks")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting completed tasks."
        )


@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: str,
    data: TaskUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        db_task = db.query(Tasks).filter(
            Tasks.id == task_id,
            Tasks.user_id == current_user.id
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # If updating category_id, verify the category belongs to the current user (IDOR prevention)
        if data.category_id is not None:
            category = db.query(Category).filter(
                Category.id == data.category_id,
                Category.owner_id == current_user.id
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)

        db.commit()
        db.refresh(db_task)
        return db_task
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Failed to update task id=%s", task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the task."
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        db_task = db.query(Tasks).filter(
            Tasks.id == task_id,
            Tasks.user_id == current_user.id
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        db.delete(db_task)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Failed to delete task id=%s", task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the task."
        )
