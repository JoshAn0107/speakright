from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WordMeaning(BaseModel):
    """Definition from dictionary API"""
    partOfSpeech: str
    definition: str
    example: Optional[str] = None
    synonyms: List[str] = []


class WordResponse(BaseModel):
    """Word data from dictionary API + our metadata"""
    word: str
    phonetic: Optional[str] = None
    audio_url: Optional[str] = None
    meanings: List[WordMeaning]
    source: Optional[str] = None

    # Our metadata
    difficulty_level: Optional[str] = None
    topic_tags: List[str] = []
    times_practiced: Optional[int] = None


class WordCreate(BaseModel):
    """For teachers to add words to system"""
    word_text: str
    difficulty_level: Optional[str] = "beginner"
    topic_tags: List[str] = []


class WordAssignmentResponse(BaseModel):
    """Word assignment in our system"""
    id: int
    word_text: str
    difficulty_level: Optional[str]
    topic_tags: List[str]
    times_practiced: int
    created_at: datetime

    class Config:
        from_attributes = True
