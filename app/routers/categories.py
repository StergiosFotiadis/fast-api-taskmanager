from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_session
from app.models import Category, User
from app.schemas.categories import CategoryCreate, CategoryOut
from app.utils.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        new_category = Category(
            name=data.name,
            owner_id=current_user.id
        )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create category")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the category."
        )


@router.get("/", response_model=List[CategoryOut], status_code=status.HTTP_200_OK)
def get_all_categories(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return db.query(Category).filter(Category.owner_id == current_user.id).all()


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        db_category = db.query(Category).filter(
            Category.id == category_id,
            Category.owner_id == current_user.id
        ).first()

        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        db.delete(db_category)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Failed to delete category id=%s", category_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the category."
        )
