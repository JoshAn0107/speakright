from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.db.session import Base


class FeatureSuggestion(Base):
    """Teacher feedback / feature requests for the platform"""
    __tablename__ = "feature_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="new", nullable=False)  # new / done
    reply = Column(Text, nullable=True)  # operator reply, shown to the teacher
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    replied_at = Column(DateTime(timezone=True), nullable=True)
