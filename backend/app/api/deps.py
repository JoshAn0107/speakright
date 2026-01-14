from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user_id
from app.models.user import User, UserRole


def get_current_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a student"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this resource"
        )
    return current_user


def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a teacher"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this resource"
        )
    return current_user
