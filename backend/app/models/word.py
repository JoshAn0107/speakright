from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WordAssignment(Base):
    """Tracks which words are in the system - actual definitions fetched from API"""
    __tablename__ = "word_assignments"

    id = Column(Integer, primary_key=True, index=True)
    word_text = Column(String(100), unique=True, nullable=False, index=True)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=True)
    topic_tags = Column(JSON, default=[])  # Changed from ARRAY to JSON for SQLite
    times_practiced = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
