from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func

from app.db.session import Base


class Class(Base):
    """Teacher's classes"""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ClassEnrollment(Base):
    """Student enrollment in classes"""
    __tablename__ = "class_enrollment"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
