import httpx
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from app.core.config import settings


class DictionaryCache:
    """Simple in-memory cache for dictionary API responses"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, tuple] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Dict]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Dict):
        """Set cached value with current timestamp"""
        self.cache[key] = (value, datetime.now())

    def clear(self):
        """Clear all cache"""
        self.cache.clear()


class DictionaryService:
    """Service to fetch word data from Free Dictionary API"""

    def __init__(self):
        self.base_url = settings.DICTIONARY_API_URL
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cache = DictionaryCache(ttl_seconds=3600)

    async def get_word_data(self, word: str) -> Optional[Dict]:
        """
        Fetch word data from Free Dictionary API with caching

        Args:
            word: The word to look up

        Returns:
            Dictionary with word data or None if not found
        """
        word_lower = word.lower().strip()

        # Check cache first
        cached = self.cache.get(word_lower)
        if cached:
            return cached

        try:
            url = f"{self.base_url}/{word_lower}"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                parsed_data = self._parse_dictionary_response(data)

                # Cache the result
                if parsed_data:
                    self.cache.set(word_lower, parsed_data)

                return parsed_data
            elif response.status_code == 404:
                return None
            else:
                print(f"Dictionary API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching word data: {e}")
            return None

    def _parse_dictionary_response(self, api_response: List[Dict]) -> Optional[Dict]:
        """Parse the API response into a clean format"""
        if not api_response:
            return None

        # API returns a list, take first result
        word_data = api_response[0]

        # Extract phonetics
        phonetic_text = word_data.get('phonetic', '')
        audio_url = None

        for phonetic in word_data.get('phonetics', []):
            if phonetic.get('audio'):
                audio_url = phonetic['audio']
                if phonetic_text == '' and phonetic.get('text'):
                    phonetic_text = phonetic['text']
                break
            if not phonetic_text and phonetic.get('text'):
                phonetic_text = phonetic['text']

        # Extract meanings
        meanings = []
        for meaning in word_data.get('meanings', []):
            part_of_speech = meaning.get('partOfSpeech', '')

            for definition in meaning.get('definitions', [])[:3]:  # Limit to 3 definitions
                meanings.append({
                    'partOfSpeech': part_of_speech,
                    'definition': definition.get('definition', ''),
                    'example': definition.get('example', ''),
                    'synonyms': definition.get('synonyms', [])[:5]  # Limit synonyms
                })

        return {
            'word': word_data.get('word', ''),
            'phonetic': phonetic_text,
            'audio_url': audio_url,
            'meanings': meanings,
            'source': 'Free Dictionary API'
        }

    async def get_multiple_words(self, words: List[str]) -> Dict[str, Optional[Dict]]:
        """Fetch multiple words in parallel"""
        import asyncio
        tasks = [self.get_word_data(word) for word in words]
        results = await asyncio.gather(*tasks)
        return dict(zip(words, results))

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
dictionary_service = DictionaryService()
