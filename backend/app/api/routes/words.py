from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import random

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_teacher
from app.models.user import User
from app.models.word import WordAssignment
from app.schemas.word import WordResponse, WordCreate, WordAssignmentResponse
from app.services.dictionary_service import dictionary_service

router = APIRouter()


@router.get("/words/{word}", response_model=WordResponse)
async def get_word(word: str, db: Session = Depends(get_db)):
    """Get word data from dictionary API"""

    # Fetch from API
    word_data = await dictionary_service.get_word_data(word)

    if not word_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found in dictionary"
        )

    # Check if word is already in our system
    word_assignment = db.query(WordAssignment).filter(
        WordAssignment.word_text == word.lower()
    ).first()

    # Add metadata from our database if exists
    if word_assignment:
        word_data['difficulty_level'] = word_assignment.difficulty_level
        word_data['topic_tags'] = word_assignment.topic_tags
        word_data['times_practiced'] = word_assignment.times_practiced

    return word_data


@router.get("/words/daily/challenge", response_model=WordResponse)
async def get_daily_word(db: Session = Depends(get_db)):
    """Get a daily challenge word"""

    # Get a random word from database
    word_assignment = db.query(WordAssignment).order_by(func.random()).first()

    if word_assignment:
        word_data = await dictionary_service.get_word_data(word_assignment.word_text)
        if word_data:
            word_data['difficulty_level'] = word_assignment.difficulty_level
            word_data['topic_tags'] = word_assignment.topic_tags
            return word_data

    # Fallback to a predefined common word
    common_words = [
        'beautiful', 'wonderful', 'important', 'different', 'possible',
        'comfortable', 'interesting', 'necessary', 'available', 'successful'
    ]
    daily_word = random.choice(common_words)

    word_data = await dictionary_service.get_word_data(daily_word)
    if not word_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch daily word"
        )

    return word_data


@router.get("/words/topic/{topic}", response_model=List[WordResponse])
async def get_words_by_topic(topic: str, db: Session = Depends(get_db)):
    """Get words by topic from word_assignments"""

    word_assignments = db.query(WordAssignment).filter(
        WordAssignment.topic_tags.contains([topic])
    ).all()

    if not word_assignments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No words found for topic: {topic}"
        )

    # Fetch details for all words
    words = [wa.word_text for wa in word_assignments]
    word_data_map = await dictionary_service.get_multiple_words(words)

    results = []
    for word_assignment in word_assignments:
        word_data = word_data_map.get(word_assignment.word_text)
        if word_data:
            word_data['difficulty_level'] = word_assignment.difficulty_level
            word_data['topic_tags'] = word_assignment.topic_tags
            word_data['times_practiced'] = word_assignment.times_practiced
            results.append(word_data)

    return results


@router.post("/words/assign", response_model=dict)
async def assign_word_to_system(
    word: WordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """Teacher adds a word to the system for practice"""

    # Verify word exists in dictionary
    word_data = await dictionary_service.get_word_data(word.word_text)
    if not word_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found in dictionary"
        )

    # Check if already in system
    existing = db.query(WordAssignment).filter(
        WordAssignment.word_text == word.word_text.lower()
    ).first()

    if existing:
        # Update metadata
        existing.difficulty_level = word.difficulty_level
        existing.topic_tags = word.topic_tags
        message = "Word updated in system"
    else:
        # Create new assignment
        word_assignment = WordAssignment(
            word_text=word.word_text.lower(),
            difficulty_level=word.difficulty_level,
            topic_tags=word.topic_tags,
            created_by=current_user.id
        )
        db.add(word_assignment)
        message = "Word added to system"

    db.commit()

    return {
        "message": message,
        "word": word.word_text,
        "dictionary_data": word_data
    }


@router.get("/words/search/{query}", response_model=WordResponse)
async def search_word(query: str):
    """Search for a word in dictionary"""

    word_data = await dictionary_service.get_word_data(query)
    if not word_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return word_data


@router.get("/words/assignments/all", response_model=List[WordAssignmentResponse])
def get_all_word_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all words in the system"""

    word_assignments = db.query(WordAssignment).all()
    return word_assignments
