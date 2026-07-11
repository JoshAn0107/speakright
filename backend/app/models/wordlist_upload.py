from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.db.session import Base


class WordlistUpload(Base):
    """Teacher-uploaded wordlist files waiting to be adapted into word databases.

    Files are stored outside the public uploads dir and processed manually
    (adapted) by an operator; status tracks that lifecycle.
    """
    __tablename__ = "wordlist_uploads"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=False)
    target_name = Column(String(100), nullable=True)  # desired word database name
    note = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending / done / failed
    result_message = Column(Text, nullable=True)  # filled in when adapted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
