from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_session
from app.models import Tasks, User
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        new_task = Tasks(
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            is_completed=data.is_completed or False
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return db.query(Tasks).filter(Tasks.user_id == current_user.id).all()


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
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


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
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)

        db.commit()
        db.refresh(db_task)
        return db_task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/completed", status_code=status.HTTP_200_OK)
def delete_completed_tasks(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    deleted = db.query(Tasks).filter(
        Tasks.user_id == current_user.id,
        Tasks.is_completed == True
    ).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}


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
            raise HTTPException(status_code=404, detail="Task not found")

        db.delete(db_task)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
