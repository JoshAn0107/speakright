from typing import Dict, Optional
import azure.cognitiveservices.speech as speechsdk
import os
import re
import json
import wave
import array
import difflib

try:
    import cmudict
    _CMU = cmudict.dict()
except Exception:
    _CMU = {}
import tempfile
from pydub import AudioSegment

from app.core.config import settings


class PronunciationService:
    """Service for pronunciation assessment using Azure Speech Service"""

    def __init__(self):
        if not settings.AZURE_SPEECH_KEY or not settings.AZURE_REGION:
            print("警告：未配置 Azure 语音服务凭据")
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
            # prosody assessment: stress / intonation / rhythm (en-US)
            try:
                pronunciation_config.enable_prosody_assessment()
            except Exception as e:
                print(f"Prosody assessment unavailable: {e}")

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

                # syllable-level timings from the detailed JSON (for stress analysis)
                syllable_words = []
                try:
                    raw = result.properties.get(
                        speechsdk.PropertyId.SpeechServiceResponse_JsonResult
                    )
                    nbest = json.loads(raw).get("NBest", [{}])[0]
                    syllable_words = nbest.get("Words", [])
                except Exception as e:
                    print(f"Could not parse detailed JSON: {e}")

                prosody_score = getattr(pronunciation_result, "prosody_score", None)
                assessment = {
                    "recognized_text": result.text,
                    "prosody_score": prosody_score,
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
                assessment["independent_transcript"] = self._plain_transcribe(converted_file_path)

                # acoustic word-stress check for single multisyllabic words
                if len(reference_text.split()) == 1 and syllable_words:
                    stress = self._check_word_stress(
                        converted_file_path, syllable_words[0], reference_text
                    )
                    if stress:
                        assessment["stress_check"] = stress

                return self._apply_strict_scoring(assessment, reference_text)
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return {
                    "error": "未能识别到语音",
                    "pronunciation_score": 0
                }
            else:
                return {
                    "error": f"语音识别失败：{result.reason}",
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

    @staticmethod
    def _check_word_stress(wav_path: str, word_detail: dict, reference_word: str):
        """Detect misplaced word stress acoustically.

        Cues per syllable, measured on the vowel nucleus only (consonants like
        /sh/ carry loud but stress-irrelevant energy): RMS loudness, pitch (F0
        via autocorrelation), and duration with a discount on the final
        syllable (utterance-final lengthening otherwise biases the result).
        Expected stress position comes from CMUdict; syllable/phoneme timings
        from Azure's detailed result. Returns None when unsure.
        """
        VOWELS = {"aa", "ae", "ah", "ao", "aw", "ax", "ay", "eh", "er",
                  "ey", "ih", "iy", "ow", "oy", "uh", "uw"}
        try:
            syllables = word_detail.get("Syllables") or []
            phonemes = word_detail.get("Phonemes") or []
            if len(syllables) < 2:
                return None

            prons = _CMU.get(reference_word.lower().strip())
            if not prons:
                return None
            valid_primary = set()
            for pron in prons:
                digits = [ph[-1] for ph in pron if ph[-1] in "012"]
                if len(digits) == len(syllables) and "1" in digits:
                    valid_primary.add(digits.index("1"))
            if not valid_primary:
                return None

            with wave.open(wav_path, "rb") as w:
                framerate = w.getframerate()
                samples = array.array("h", w.readframes(w.getnframes()))

            def seg(start_ticks, dur_ticks):
                a = int(start_ticks / 1e7 * framerate)
                b = min(len(samples), int((start_ticks + dur_ticks) / 1e7 * framerate))
                return samples[a:b]

            def rms(x):
                return (sum(v * v for v in x) / len(x)) ** 0.5 if x else 0.0

            def f0(x):
                # autocorrelation pitch estimate, 60–400 Hz; 0 when unvoiced
                if len(x) < int(framerate / 60) * 2:
                    return 0.0
                mid = x[len(x) // 5: -len(x) // 5] or x  # trim edges
                n = len(mid)
                energy = sum(v * v for v in mid)
                if energy == 0:
                    return 0.0
                best_lag, best_corr = 0, 0.0
                lo, hi = int(framerate / 400), int(framerate / 60)
                step = max(1, (hi - lo) // 120)
                # stride-matched reference energy so the voicing check is fair
                ref = sum(mid[i] * mid[i] for i in range(0, n, 4)) or 1
                for lag in range(lo, min(hi, n - 1), step):
                    c = 0
                    for i in range(0, n - lag, 4):
                        c += mid[i] * mid[i + lag]
                    if c > best_corr:
                        best_corr, best_lag = c, lag
                if best_lag == 0 or best_corr < ref * 0.3:
                    return 0.0
                return framerate / best_lag

            # map each syllable to its vowel phoneme span (fallback: full syllable)
            cues = []
            for i, syl in enumerate(syllables):
                s_start = syl.get("Offset", 0)
                s_end = s_start + syl.get("Duration", 0)
                vowel_span = None
                for ph in phonemes:
                    name = re.sub(r"[^a-z]", "", (ph.get("Phoneme") or "").lower())
                    p_mid = ph.get("Offset", 0) + ph.get("Duration", 0) / 2
                    if name in VOWELS and s_start <= p_mid < s_end:
                        vowel_span = (ph.get("Offset", 0), ph.get("Duration", 0))
                        break
                if vowel_span is None:
                    vowel_span = (s_start, s_end - s_start)
                x = seg(*vowel_span)
                if len(x) > 40:
                    x = x[len(x) // 5: -len(x) // 5]  # middle 60% of the vowel
                dur = vowel_span[1] / 1e7
                if i == len(syllables) - 1:
                    dur *= 0.6  # utterance-final lengthening discount
                cues.append({"rms": rms(x), "f0": f0(x), "dur": dur})

            max_rms = max(c["rms"] for c in cues) or 1.0
            max_dur = max(c["dur"] for c in cues) or 1.0
            voiced_f0 = [c["f0"] for c in cues if c["f0"] > 0]
            max_f0 = max(voiced_f0) if voiced_f0 else 0.0
            use_f0 = max_f0 > 0 and len(voiced_f0) >= 2

            scores = []
            for c in cues:
                if use_f0:
                    val = (0.45 * c["rms"] / max_rms
                           + 0.35 * (c["f0"] / max_f0 if c["f0"] > 0 else 0.4)
                           + 0.20 * c["dur"] / max_dur)
                else:
                    val = 0.65 * c["rms"] / max_rms + 0.35 * c["dur"] / max_dur
                scores.append(val)

            predicted = scores.index(max(scores))
            expected_best = min(valid_primary, key=lambda i: abs(i - predicted))

            match = predicted in valid_primary
            if not match:
                # flag only when clearly more prominent than the expected syllable
                if scores[predicted] < scores[expected_best] * 1.25:
                    match = True
                elif use_f0:
                    # and only when pitch agrees loudness (both point away from
                    # every valid stress position); AGC onset bursts fool RMS alone
                    f0_rank = max(range(len(cues)), key=lambda i: cues[i]["f0"])
                    if f0_rank in valid_primary:
                        match = True

            return {
                "match": match,
                "expected_syllable": expected_best + 1,
                "predicted_syllable": predicted + 1,
                "syllables": [syl.get("Syllable", "") for syl in syllables],
                "prominence": [round(x, 2) for x in scores],
                "f0": [round(c["f0"]) for c in cues],
            }
        except Exception as e:
            print(f"Stress check failed (non-fatal): {e}")
            return None

    def _plain_transcribe(self, audio_file_path: str) -> str:
        """Second pass: plain STT without reference text.

        Pronunciation assessment aligns audio to the reference, so its
        recognized_text is biased toward the reference (it can even fill in
        words that were never spoken). An unbiased transcript is the reliable
        signal for did-they-say-the-right-words.
        """
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_REGION
            )
            speech_config.speech_recognition_language = "en-US"
            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            result = recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            return ""
        except Exception as e:
            print(f"Plain transcription failed (non-fatal): {e}")
            return ""

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = (text or "").lower()
        text = re.sub(r"[^a-z' ]+", " ", text)
        return " ".join(text.split())

    def _apply_strict_scoring(self, result: Dict, reference_text: str) -> Dict:
        """Stricter final score on top of Azure's assessment.

        Azure aligns the audio to the reference text, so saying a different or
        incomplete phrase can still score high. Signals combined here:
        - the unbiased second-pass transcript vs the reference text
        - Azure's per-word error types
        - phoneme-level weakness
        """
        azure_score = float(result.get("pronunciation_score") or 0)
        azure_accuracy = float(result.get("accuracy_score") or 0)
        recognized_pa = self._normalize_text(result.get("recognized_text", ""))
        independent_raw = result.get("independent_transcript") or ""
        independent = self._normalize_text(independent_raw)
        reference = self._normalize_text(reference_text)

        # prefer the unbiased transcript; fall back to the PA-aligned text
        heard = independent if independent else recognized_pa
        result["heard_text"] = independent_raw.strip() or result.get("recognized_text", "")
        result["azure_pronunciation_score"] = azure_score

        similarity = difflib.SequenceMatcher(None, heard, reference).ratio() if heard else 0.0
        text_match = heard == reference
        result["text_match"] = text_match
        result["recognized_similarity"] = round(similarity, 2)

        words = result.get("words") or []
        error_words = [
            w for w in words
            if (w.get("error_type") or "None") not in ("None", None)
        ]
        phonemes = [p for w in words for p in (w.get("phonemes") or [])]
        weak = [p for p in phonemes if float(p.get("accuracy_score") or 0) < 60]
        weak_ratio = (len(weak) / len(phonemes)) if phonemes else 0.0
        result["error_word_count"] = len(error_words)
        result["weak_phoneme_ratio"] = round(weak_ratio, 2)

        ref_tokens = reference.split()
        heard_tokens = heard.split()

        score = azure_score
        if not text_match:
            if len(ref_tokens) <= 1:
                # single word
                if azure_accuracy >= 90 and recognized_pa == reference:
                    # sound matched the reference very closely — likely a
                    # homophone / spelling variant from the plain STT pass
                    score = azure_score * 0.9
                elif similarity >= 0.85:
                    score = azure_score * 0.9
                else:
                    score = min(azure_score * (0.25 + 0.5 * similarity), 55.0)
            else:
                # phrase/sentence: token-level alignment, penalize missing or extra words
                sm = difflib.SequenceMatcher(None, ref_tokens, heard_tokens)
                matched = sum(b.size for b in sm.get_matching_blocks())
                token_ratio = matched / max(len(ref_tokens), len(heard_tokens)) if heard_tokens else 0.0
                result["token_match_ratio"] = round(token_ratio, 2)
                score = azure_score * (0.35 + 0.65 * token_ratio * token_ratio)
                if token_ratio < 0.5:
                    score = min(score, 55.0)
        else:
            # text matches; still penalize flagged errors and weak phonemes
            if error_words:
                score -= min(5.0 * len(error_words), 20.0)
            if weak_ratio > 0.6:
                score = min(score, 65.0)
            elif weak_ratio > 0.4:
                score = min(score, 75.0)

            # prosody (stress / intonation / rhythm): wrong stress must not score high
            prosody = result.get("prosody_score")
            if prosody is not None:
                prosody = float(prosody)
                if prosody < 40:
                    score = min(score, 55.0)
                elif prosody < 55:
                    score = min(score, 68.0)
                elif prosody < 70:
                    score = min(score, 80.0)

            # acoustic word-stress check: misplaced stress caps the score hard
            stress = result.get("stress_check")
            if stress and stress.get("match") is False:
                score = min(score, 62.0)

        score = max(0.0, min(100.0, round(score, 1)))
        result["pronunciation_score"] = score
        return result

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
