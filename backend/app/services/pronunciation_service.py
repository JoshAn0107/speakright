from typing import Dict, Optional
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
from pydub import AudioSegment

from app.core.config import settings


class PronunciationService:
    """Service for pronunciation assessment using Azure Speech Service"""

    def __init__(self):
        if not settings.AZURE_SPEECH_KEY or not settings.AZURE_REGION:
            print("WARNING: Azure Speech Service credentials not configured")
            self.enabled = False
        else:
            self.enabled = True

    def _convert_to_azure_format(self, audio_file_path: str) -> str:
        """
        Convert audio file to Azure-compatible format:
        - WAV format
        - 16kHz sample rate
        - 16-bit PCM
        - Mono channel

        Returns path to converted file (temporary file)
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_file_path)

            # Convert to mono
            audio = audio.set_channels(1)

            # Convert to 16kHz sample rate
            audio = audio.set_frame_rate(16000)

            # Convert to 16-bit
            audio = audio.set_sample_width(2)  # 2 bytes = 16 bits

            # Create temporary file for converted audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()

            # Export as WAV with correct format
            audio.export(
                temp_path,
                format='wav',
                parameters=['-acodec', 'pcm_s16le']  # 16-bit PCM
            )

            print(f"Audio converted to Azure format: {temp_path}")
            print(f"  Sample rate: {audio.frame_rate}Hz")
            print(f"  Channels: {audio.channels}")
            print(f"  Sample width: {audio.sample_width} bytes")

            return temp_path

        except Exception as e:
            print(f"Error converting audio: {e}")
            # If conversion fails, return original file
            return audio_file_path

    def assess_pronunciation(self, audio_file_path: str, reference_text: str) -> Optional[Dict]:
        """
        Assess pronunciation using Azure Speech Service

        Args:
            audio_file_path: Path to the audio file
            reference_text: The word or phrase being pronounced

        Returns:
            dict with assessment results or None if service not configured
        """
        if not self.enabled:
            # Return mock data for development/testing
            return self._get_mock_assessment(reference_text)

        converted_file_path = None
        try:
            # Convert audio to Azure-compatible format
            converted_file_path = self._convert_to_azure_format(audio_file_path)

            # Configure speech service
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_REGION
            )
            speech_config.speech_recognition_language = "en-US"

            # Configure pronunciation assessment
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=True
            )

            # Configure audio input with converted file
            audio_config = speechsdk.audio.AudioConfig(filename=converted_file_path)

            # Create recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            # Apply pronunciation assessment
            pronunciation_config.apply_to(recognizer)

            # Perform recognition
            result = recognizer.recognize_once()

            # Parse results
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                pronunciation_result = speechsdk.PronunciationAssessmentResult(result)

                return {
                    "recognized_text": result.text,
                    "pronunciation_score": pronunciation_result.pronunciation_score,
                    "accuracy_score": pronunciation_result.accuracy_score,
                    "fluency_score": pronunciation_result.fluency_score,
                    "completeness_score": pronunciation_result.completeness_score,
                    "words": [
                        {
                            "word": word.word,
                            "accuracy_score": word.accuracy_score,
                            "error_type": word.error_type if hasattr(word, 'error_type') else None,
                            "phonemes": [
                                {
                                    "phoneme": phoneme.phoneme,
                                    "accuracy_score": phoneme.accuracy_score
                                }
                                for phoneme in word.phonemes
                            ]
                        }
                        for word in pronunciation_result.words
                    ]
                }
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return {
                    "error": "No speech could be recognized",
                    "pronunciation_score": 0
                }
            else:
                return {
                    "error": f"Speech recognition failed: {result.reason}",
                    "pronunciation_score": 0
                }

        except Exception as e:
            import traceback
            print(f"Error in pronunciation assessment: {e}")
            print(f"Full traceback:")
            traceback.print_exc()
            return {
                "error": str(e),
                "pronunciation_score": 0
            }
        finally:
            # Clean up temporary converted file
            if converted_file_path and converted_file_path != audio_file_path:
                try:
                    if os.path.exists(converted_file_path):
                        os.remove(converted_file_path)
                        print(f"Cleaned up temporary file: {converted_file_path}")
                except Exception as e:
                    print(f"Error cleaning up temporary file: {e}")

    def _get_mock_assessment(self, reference_text: str) -> Dict:
        """
        Generate mock assessment data for development/testing
        Returns realistic-looking scores
        """
        import random

        # Generate random but realistic scores
        pronunciation_score = random.randint(65, 95)
        accuracy_score = random.randint(60, 95)
        fluency_score = random.randint(70, 95)
        completeness_score = random.randint(80, 100)

        # Simple phoneme breakdown (mock)
        words = reference_text.split()
        word_assessments = []

        for word in words:
            # Mock phonemes - simplified
            phoneme_count = len(word) // 2 + 1
            phonemes = []

            for i in range(phoneme_count):
                phonemes.append({
                    "phoneme": f"ph{i}",
                    "accuracy_score": random.randint(60, 100)
                })

            word_assessments.append({
                "word": word,
                "accuracy_score": random.randint(60, 95),
                "error_type": None,
                "phonemes": phonemes
            })

        return {
            "recognized_text": reference_text,
            "pronunciation_score": pronunciation_score,
            "accuracy_score": accuracy_score,
            "fluency_score": fluency_score,
            "completeness_score": completeness_score,
            "words": word_assessments,
            "_mock": True  # Flag to indicate this is mock data
        }


# Singleton instance
pronunciation_service = PronunciationService()
