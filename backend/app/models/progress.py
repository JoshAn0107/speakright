from sqlalchemy import Column, Integer, Date, ForeignKey, Numeric
from app.db.session import Base


class StudentProgress(Base):
    """Daily progress tracking for students"""
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    words_practiced = Column(Integer, default=0)
    average_score = Column(Numeric(5, 2), nullable=True)
    total_attempts = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
