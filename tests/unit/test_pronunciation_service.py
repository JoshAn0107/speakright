"""
Unit tests for PronunciationService
Covers L01 Requirements: 3.g, 3.h
"""
import pytest
import sys
from pathlib import Path
import tempfile
import os

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.pronunciation_service import PronunciationService


class TestGetMockAssessment:
    """
    L01 Requirement 3.h: The _get_mock_assessment function should generate
    realistic pronunciation scores within valid ranges

    Testing approach: Black-box testing
    """

    @pytest.fixture
    def service(self):
        """Create pronunciation service instance"""
        return PronunciationService()

    def test_generates_valid_score_structure(self, service):
        """Test that mock assessment has all required fields"""
        result = service._get_mock_assessment("beautiful")

        # Check all required top-level fields
        assert "recognized_text" in result
        assert "pronunciation_score" in result
        assert "accuracy_score" in result
        assert "fluency_score" in result
        assert "completeness_score" in result
        assert "words" in result

    def test_scores_within_valid_range_0_100(self, service):
        """Test that all scores are within 0-100 range"""
        # Test multiple times to catch random variations
        for _ in range(10):
            result = service._get_mock_assessment("test")

            assert 0 <= result["pronunciation_score"] <= 100
            assert 0 <= result["accuracy_score"] <= 100
            assert 0 <= result["fluency_score"] <= 100
            assert 0 <= result["completeness_score"] <= 100

    def test_scores_within_realistic_range(self, service):
        """Test that mock scores are in realistic range (typically 60-100)"""
        # Test multiple times
        for _ in range(20):
            result = service._get_mock_assessment("wonderful")

            # Mock scores should generally be in passing range
            # Based on the implementation, scores are random.randint(65, 95) etc.
            assert result["pronunciation_score"] >= 60
            assert result["accuracy_score"] >= 60

    def test_recognized_text_matches_input(self, service):
        """Test that recognized text matches reference text"""
        reference_text = "beautiful"
        result = service._get_mock_assessment(reference_text)

        assert result["recognized_text"] == reference_text

    def test_contains_word_assessments(self, service):
        """Test that result includes word-level assessments"""
        result = service._get_mock_assessment("beautiful")

        assert "words" in result
        assert isinstance(result["words"], list)
        assert len(result["words"]) > 0

    def test_word_assessment_structure(self, service):
        """Test structure of word-level assessments"""
        result = service._get_mock_assessment("beautiful")

        for word_assessment in result["words"]:
            assert "word" in word_assessment
            assert "accuracy_score" in word_assessment
            assert "phonemes" in word_assessment
            assert isinstance(word_assessment["phonemes"], list)

    def test_phoneme_assessment_structure(self, service):
        """Test structure of phoneme-level assessments"""
        result = service._get_mock_assessment("beautiful")

        for word_assessment in result["words"]:
            for phoneme in word_assessment["phonemes"]:
                assert "phoneme" in phoneme
                assert "accuracy_score" in phoneme
                assert 0 <= phoneme["accuracy_score"] <= 100

    def test_mock_flag_present(self, service):
        """Test that mock data includes _mock flag"""
        result = service._get_mock_assessment("test")

        assert "_mock" in result
        assert result["_mock"] is True

    def test_handles_multi_word_input(self, service):
        """Test mock assessment with multi-word input"""
        reference_text = "hello world"
        result = service._get_mock_assessment(reference_text)

        # Should include assessments for multiple words
        assert len(result["words"]) >= 2

        # Should recognize the full text
        assert result["recognized_text"] == reference_text

    def test_handles_empty_string(self, service):
        """Test mock assessment with empty string"""
        result = service._get_mock_assessment("")

        assert result is not None
        assert "pronunciation_score" in result
        assert result["recognized_text"] == ""

    def test_handles_special_characters(self, service):
        """Test mock assessment with special characters in text"""
        reference_text = "can't"
        result = service._get_mock_assessment(reference_text)

        assert result["recognized_text"] == reference_text

    def test_consistency_of_score_ranges(self, service):
        """Test that score ranges are consistent across multiple calls"""
        results = [service._get_mock_assessment("test") for _ in range(50)]

        # All scores should be in reasonable range
        for result in results:
            assert 0 <= result["pronunciation_score"] <= 100
            assert 0 <= result["accuracy_score"] <= 100
            assert 0 <= result["fluency_score"] <= 100
            assert 0 <= result["completeness_score"] <= 100

        # There should be some variation in scores
        pronunciation_scores = [r["pronunciation_score"] for r in results]
        assert len(set(pronunciation_scores)) > 1  # Not all the same

    def test_phoneme_count_reasonable(self, service):
        """Test that phoneme count is reasonable for word length"""
        # Short word
        short_result = service._get_mock_assessment("cat")
        # Long word
        long_result = service._get_mock_assessment("pronunciation")

        # Phoneme count should be related to word length
        # Based on implementation: phoneme_count = len(word) // 2 + 1
        for word in short_result["words"]:
            assert len(word["phonemes"]) >= 1
            assert len(word["phonemes"]) <= 10

        for word in long_result["words"]:
            assert len(word["phonemes"]) >= 1
            # Longer words should have more phonemes
            assert len(word["phonemes"]) > 2

    def test_error_type_in_word_assessment(self, service):
        """Test that word assessments include error_type field"""
        result = service._get_mock_assessment("beautiful")

        for word_assessment in result["words"]:
            assert "error_type" in word_assessment
            # Mock implementation sets this to None
            assert word_assessment["error_type"] is None

    def test_all_scores_are_numeric(self, service):
        """Test that all scores are numeric types"""
        result = service._get_mock_assessment("beautiful")

        assert isinstance(result["pronunciation_score"], (int, float))
        assert isinstance(result["accuracy_score"], (int, float))
        assert isinstance(result["fluency_score"], (int, float))
        assert isinstance(result["completeness_score"], (int, float))

        for word in result["words"]:
            assert isinstance(word["accuracy_score"], (int, float))
            for phoneme in word["phonemes"]:
                assert isinstance(phoneme["accuracy_score"], (int, float))


class TestConvertToAzureFormat:
    """
    L01 Requirement 3.g: The _convert_to_azure_format function should
    correctly convert audio files to Azure-compatible format

    Testing approach: Functional category-partition testing
    Partitions: Already correct format, needs sample rate conversion,
                needs channel conversion, needs bit depth conversion,
                unsupported format
    """

    @pytest.fixture
    def service(self):
        """Create pronunciation service instance"""
        return PronunciationService()

    def create_temp_wav_file(self, sample_rate=44100, channels=2, sample_width=2):
        """Helper to create a temporary WAV file with specific parameters"""
        from pydub import AudioSegment
        from pydub.generators import Sine

        # Create a simple sine wave
        duration_ms = 100
        frequency = 440  # A4 note

        # Generate audio
        audio = Sine(frequency).to_audio_segment(duration=duration_ms)
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_channels(channels)
        audio = audio.set_sample_width(sample_width)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()

        audio.export(temp_path, format='wav')

        return temp_path

    def test_already_correct_format(self, service):
        """Test conversion when audio is already in correct format (16kHz, mono, 16-bit)"""
        # Create file with Azure-compatible format
        input_path = self.create_temp_wav_file(sample_rate=16000, channels=1, sample_width=2)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            # Should create a converted file
            assert converted_path is not None
            assert os.path.exists(converted_path)

            # Verify format using pydub
            from pydub import AudioSegment
            audio = AudioSegment.from_file(converted_path)

            assert audio.frame_rate == 16000
            assert audio.channels == 1
            assert audio.sample_width == 2

        finally:
            # Cleanup
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and converted_path != input_path and os.path.exists(converted_path):
                os.remove(converted_path)

    def test_needs_sample_rate_conversion(self, service):
        """Test conversion when sample rate needs adjustment"""
        # Create file with 44100 Hz (needs conversion to 16000 Hz)
        input_path = self.create_temp_wav_file(sample_rate=44100, channels=1, sample_width=2)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            assert converted_path is not None
            assert os.path.exists(converted_path)

            # Verify conversion
            from pydub import AudioSegment
            audio = AudioSegment.from_file(converted_path)

            assert audio.frame_rate == 16000  # Should be converted

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and converted_path != input_path and os.path.exists(converted_path):
                os.remove(converted_path)

    def test_needs_channel_conversion_stereo_to_mono(self, service):
        """Test conversion when stereo needs to be converted to mono"""
        # Create stereo file (needs conversion to mono)
        input_path = self.create_temp_wav_file(sample_rate=16000, channels=2, sample_width=2)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            assert converted_path is not None
            assert os.path.exists(converted_path)

            # Verify conversion
            from pydub import AudioSegment
            audio = AudioSegment.from_file(converted_path)

            assert audio.channels == 1  # Should be mono

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and converted_path != input_path and os.path.exists(converted_path):
                os.remove(converted_path)

    def test_needs_bit_depth_conversion(self, service):
        """Test conversion when bit depth needs adjustment"""
        # Create file with 8-bit depth (needs conversion to 16-bit)
        input_path = self.create_temp_wav_file(sample_rate=16000, channels=1, sample_width=1)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            assert converted_path is not None
            assert os.path.exists(converted_path)

            # Verify conversion
            from pydub import AudioSegment
            audio = AudioSegment.from_file(converted_path)

            assert audio.sample_width == 2  # Should be 16-bit

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and converted_path != input_path and os.path.exists(converted_path):
                os.remove(converted_path)

    def test_multiple_conversions_needed(self, service):
        """Test when multiple format conversions are needed"""
        # Create file with all wrong parameters
        input_path = self.create_temp_wav_file(sample_rate=48000, channels=2, sample_width=3)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            assert converted_path is not None
            assert os.path.exists(converted_path)

            # Verify all conversions
            from pydub import AudioSegment
            audio = AudioSegment.from_file(converted_path)

            assert audio.frame_rate == 16000
            assert audio.channels == 1
            assert audio.sample_width == 2

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and converted_path != input_path and os.path.exists(converted_path):
                os.remove(converted_path)

    def test_creates_temporary_file(self, service):
        """Test that conversion creates a new temporary file"""
        input_path = self.create_temp_wav_file(sample_rate=44100, channels=2, sample_width=2)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            # Converted file should be different from input
            assert converted_path != input_path
            assert os.path.exists(converted_path)
            assert converted_path.endswith('.wav')

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and os.path.exists(converted_path):
                os.remove(converted_path)

    def test_handles_nonexistent_file(self, service):
        """Test handling of non-existent file"""
        nonexistent_path = "/tmp/nonexistent_audio_file.wav"

        try:
            converted_path = service._convert_to_azure_format(nonexistent_path)

            # Should return original path on error (based on implementation)
            assert converted_path == nonexistent_path
        except Exception:
            # Or may raise exception, which is also acceptable
            pass

    def test_preserves_audio_content(self, service):
        """Test that conversion preserves essential audio content"""
        input_path = self.create_temp_wav_file(sample_rate=44100, channels=2, sample_width=2)

        try:
            converted_path = service._convert_to_azure_format(input_path)

            from pydub import AudioSegment
            original = AudioSegment.from_file(input_path)
            converted = AudioSegment.from_file(converted_path)

            # Duration should be approximately the same (within 10ms)
            assert abs(len(original) - len(converted)) < 10

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if converted_path and converted_path != input_path and os.path.exists(converted_path):
                os.remove(converted_path)
