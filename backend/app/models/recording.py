from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum, JSON
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class RecordingStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"


class Recording(Base):
    """Student pronunciation recordings"""
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word_text = Column(String(100), nullable=False, index=True)
    audio_file_path = Column(String(500), nullable=False)

    # Automated assessment from Azure Speech
    automated_scores = Column(JSON, nullable=True)

    # Teacher feedback
    teacher_feedback = Column(Text, nullable=True)
    teacher_audio_feedback_url = Column(String(500), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    teacher_grade = Column(String(10), nullable=True)

    # Status tracking
    status = Column(Enum(RecordingStatus), default=RecordingStatus.PENDING, nullable=False, index=True)
    flag_for_practice = Column(Boolean, default=False)
    is_automated_feedback = Column(Boolean, default=True)  # Track if feedback is automated or manually reviewed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
