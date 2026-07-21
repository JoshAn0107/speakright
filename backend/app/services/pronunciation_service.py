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
        # 讯飞语音评测优先：国内节点、独立额度、少儿优化，不受 Azure 跨境/配额影响
        xf_result = self._try_xfyun(audio_file_path, reference_text)
        if xf_result is not None:
            return xf_result

        if not self.enabled:
            # Return mock data for development/testing
            return self._get_mock_assessment(reference_text)

        converted_file_path = None
        transcribe_future = None
        try:
            # Convert audio to Azure-compatible format
            converted_file_path = self._convert_to_azure_format(audio_file_path)

            # kick off the unbiased second-pass transcription in parallel with
            # the pronunciation assessment call — halves Azure round-trip time.
            # It gets its own copy of the wav: two recognizers streaming the
            # same file handle makes the SDK cancel the session.
            import shutil as _shutil
            from concurrent.futures import ThreadPoolExecutor
            transcribe_copy = converted_file_path + ".stt.wav"
            _shutil.copyfile(converted_file_path, transcribe_copy)

            def _transcribe_and_cleanup(path):
                try:
                    return self._plain_transcribe(path)
                finally:
                    try:
                        os.remove(path)
                    except OSError:
                        pass

            from app.services.shadow_service import gop_transcribe_sync
            gop_copy = converted_file_path + ".gop.wav"
            _shutil.copyfile(converted_file_path, gop_copy)

            def _gop_and_cleanup(path, ref):
                try:
                    return gop_transcribe_sync(path, ref)
                finally:
                    try:
                        os.remove(path)
                    except OSError:
                        pass

            _executor = ThreadPoolExecutor(max_workers=2)
            transcribe_future = _executor.submit(_transcribe_and_cleanup, transcribe_copy)
            gop_future = _executor.submit(_gop_and_cleanup, gop_copy, reference_text)
            _executor.shutdown(wait=False)

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
                assessment["independent_transcript"] = (
                    transcribe_future.result(timeout=60) if transcribe_future else ""
                )
                try:
                    gop_heard, gop_score = gop_future.result(timeout=8)
                except Exception:
                    gop_heard, gop_score = None, None
                assessment["gop_heard"] = gop_heard
                assessment["gop_score"] = gop_score

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
                # Azure cancelled (quota exceeded / service error) -> fall back
                # to the self-hosted GOP model so scoring never fully stops
                details = ""
                if result.reason == speechsdk.ResultReason.Canceled:
                    try:
                        details = result.cancellation_details.error_details or ""
                    except Exception:
                        details = ""
                fb = self._gop_fallback(converted_file_path, reference_text)
                if fb:
                    return fb
                return {
                    "error": f"语音识别失败：{result.reason} {details[:100]}",
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
            # make sure the parallel transcription is finished before deleting the file
            if transcribe_future is not None and not transcribe_future.done():
                try:
                    transcribe_future.result(timeout=60)
                except Exception:
                    pass
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
        phoneme_scores = [float(p.get("accuracy_score") or 0) for p in phonemes]
        phoneme_mean = (sum(phoneme_scores) / len(phoneme_scores)) if phoneme_scores else None
        weak = [x for x in phoneme_scores if x < 60]
        weak_ratio = (len(weak) / len(phoneme_scores)) if phoneme_scores else 0.0
        result["error_word_count"] = len(error_words)
        result["weak_phoneme_ratio"] = round(weak_ratio, 2)
        result["phoneme_mean"] = round(phoneme_mean, 1) if phoneme_mean is not None else None

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
                    # teacher calibration: a recognizable-but-warped attempt
                    # (decent phonemes, wrong STT text) deserves C-, not F
                    harsh = azure_score * (0.25 + 0.5 * similarity)
                    floor = (phoneme_mean * 0.8) if phoneme_mean is not None else 0.0
                    score = min(max(harsh, floor), 60.0)
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

            # STT autocorrects near-miss words, so lean on phoneme evidence:
            # the overall Azure score must stay near what the phonemes support
            if phoneme_mean is not None:
                score = min(score, phoneme_mean + 12.0)
            clearly_bad = sum(1 for x in phoneme_scores if x < 55)
            mediocre = sum(1 for x in phoneme_scores if x < 65)
            if clearly_bad >= 2:
                score = min(score, 72.0)
            elif mediocre >= 3:
                score = min(score, 80.0)

            # dual-signal rule (calibrated on teacher corrections + 1341 shadow
            # rows): the prior-free GOP model heard something quite different
            # AND Azure's own phoneme evidence is mediocre -> not a clean read.
            # Either signal alone is too noisy; together they flag ~9% of
            # high-Azure reads and matched every teacher-flagged case.
            gop_heard = result.get("gop_heard")
            if gop_heard and phoneme_mean is not None:
                gop_sim = difflib.SequenceMatcher(
                    None,
                    re.sub(r"[^a-z]", "", gop_heard.lower()),
                    re.sub(r"[^a-z]", "", reference.lower()),
                ).ratio()
                result["gop_similarity"] = round(gop_sim, 2)
                if gop_sim < 0.55 and phoneme_mean <= 82:
                    score = min(score, 66.0)

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

    def _try_xfyun(self, audio_file_path: str, reference_text: str):
        """讯飞评测（主）。返回评分 dict；未配置/失败/乱读被拒时返回 None 走 Azure。"""
        try:
            from app.services import xf_ise_service
            if not xf_ise_service.available():
                return None
            converted = self._convert_to_azure_format(audio_file_path)
            try:
                r = xf_ise_service.assess_word(converted, reference_text)
            finally:
                try:
                    if converted and converted != audio_file_path and os.path.exists(converted):
                        os.remove(converted)
                except OSError:
                    pass
            # 乱读被判 reject（可能误判）→ 回退 Azure 复核
            if not r or r.get("rejected"):
                return None
            return r
        except Exception as e:
            print(f"xfyun scoring failed, falling back: {e}")
            return None

    def _gop_fallback(self, wav_path: str, reference_text: str):
        """Score with the self-hosted GOP model when Azure is unavailable."""
        try:
            from app.services.shadow_service import gop_assess_full
            fb = gop_assess_full(wav_path, reference_text)
            if not fb:
                return None
            # run the same strict layer; it degrades gracefully without prosody
            fb = self._apply_strict_scoring(fb, reference_text)
            fb["fallback"] = True
            return fb
        except Exception as e:
            print(f"GOP fallback failed: {e}")
            return None

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

    def _plain_transcribe_continuous(self, audio_file_path: str) -> str:
        """Unbiased full-file transcription using continuous recognition."""
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_REGION
            )
            speech_config.speech_recognition_language = "en-US"
            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )
            import threading as _threading
            texts = []
            done = _threading.Event()
            recognizer.recognized.connect(
                lambda evt: texts.append(evt.result.text)
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech else None
            )
            recognizer.session_stopped.connect(lambda evt: done.set())
            recognizer.canceled.connect(lambda evt: done.set())
            recognizer.start_continuous_recognition()
            done.wait(timeout=180)
            recognizer.stop_continuous_recognition()
            return " ".join(texts)
        except Exception as e:
            print(f"Continuous transcription failed (non-fatal): {e}")
            return ""

    def assess_continuous_reading(self, audio_file_path: str, reference_words: list) -> Dict:
        """Assess one continuous recording of many words (test mode).

        Uses continuous recognition (recognize_once stops at the first pause)
        with miscue enabled, so omitted/inserted words are flagged. Returns an
        overall score plus a per-reference-word breakdown.
        """
        reference_text = " ".join(reference_words)
        if not self.enabled:
            return {"error": "未配置语音服务", "pronunciation_score": 0, "per_word": []}

        converted = None
        transcribe_future = None
        try:
            converted = self._convert_to_azure_format(audio_file_path)

            # unbiased transcript in parallel, on its own copy of the file
            import shutil as _shutil
            from concurrent.futures import ThreadPoolExecutor
            stt_copy = converted + ".stt.wav"
            _shutil.copyfile(converted, stt_copy)

            def _stt(path):
                try:
                    return self._plain_transcribe_continuous(path)
                finally:
                    try:
                        os.remove(path)
                    except OSError:
                        pass

            _ex = ThreadPoolExecutor(max_workers=1)
            transcribe_future = _ex.submit(_stt, stt_copy)
            _ex.shutdown(wait=False)

            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_REGION
            )
            speech_config.speech_recognition_language = "en-US"
            pa_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=True
            )
            audio_config = speechsdk.audio.AudioConfig(filename=converted)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )
            pa_config.apply_to(recognizer)

            import threading as _threading
            azure_words = []
            texts = []
            fluency_parts = []
            done = _threading.Event()

            def on_recognized(evt):
                if evt.result.reason != speechsdk.ResultReason.RecognizedSpeech:
                    return
                texts.append(evt.result.text)
                try:
                    pr = speechsdk.PronunciationAssessmentResult(evt.result)
                    if pr.fluency_score is not None:
                        fluency_parts.append(float(pr.fluency_score))
                    # word timing comes from the detailed JSON (ticks of 100ns)
                    timing = []
                    try:
                        raw = evt.result.properties.get(
                            speechsdk.PropertyId.SpeechServiceResponse_JsonResult
                        )
                        jwords = json.loads(raw).get("NBest", [{}])[0].get("Words", [])
                        timing = [(jw.get("Offset"), jw.get("Duration")) for jw in jwords]
                    except Exception:
                        timing = []
                    for i, w in enumerate(pr.words):
                        off, dur = timing[i] if i < len(timing) else (None, None)
                        azure_words.append({
                            "word": w.word,
                            "accuracy_score": w.accuracy_score,
                            "error_type": getattr(w, "error_type", None),
                            "offset_ms": int(off / 10000) if off is not None else None,
                            "end_ms": int((off + dur) / 10000) if off is not None and dur is not None else None,
                        })
                except Exception as e:
                    print(f"PA parse error (segment): {e}")

            cancel_info = {}
            def on_canceled(evt):
                d = evt.cancellation_details
                if d and d.reason == speechsdk.CancellationReason.Error:
                    cancel_info["error"] = d.error_details or "recognition canceled"
                done.set()
            recognizer.recognized.connect(on_recognized)
            recognizer.session_stopped.connect(lambda evt: done.set())
            recognizer.canceled.connect(on_canceled)
            recognizer.start_continuous_recognition()
            finished = done.wait(timeout=240)
            recognizer.stop_continuous_recognition()

            # service-side failure (quota exceeded, timeout, network) — do NOT
            # score an empty result as "everything omitted / 0 分"
            if cancel_info.get("error"):
                is_quota = "quota" in cancel_info["error"].lower() or "1007" in cancel_info["error"]
                return {"error": ("配额不足" if is_quota else "语音服务错误") + "：" + cancel_info["error"][:120],
                        "pronunciation_score": 0, "per_word": []}
            if not finished:
                return {"error": "语音识别超时", "pronunciation_score": 0, "per_word": []}
            if not azure_words:
                return {"error": "未识别到语音，请重新录音", "pronunciation_score": 0, "per_word": []}

            # map azure word results back onto the reference sequence;
            # a reference entry may be a multi-token phrase (well done, only child)
            def _tok(t):
                return re.sub(r"[^a-z' ]", " ", (t or "").lower()).split()

            per_word = []
            ai = 0
            insertions = 0
            for ref in reference_words:
                ref_tokens = _tok(ref) or [ref.lower()]
                found_seq = None
                for j in range(ai, min(ai + 5, len(azure_words))):
                    if _tok(azure_words[j]["word"])[:1] == ref_tokens[:1]:
                        seq = azure_words[j:j + len(ref_tokens)]
                        seq_tokens = [t for w in seq for t in _tok(w["word"])]
                        if seq_tokens == ref_tokens:
                            insertions += sum(
                                1 for k in range(ai, j)
                                if (azure_words[k].get("error_type") or "") == "Insertion"
                            )
                            found_seq = seq
                            ai = j + len(seq)
                            break
                if not found_seq:
                    per_word.append({"word": ref, "score": 0, "error": "漏读"})
                    continue
                etypes = {(w.get("error_type") or "None") for w in found_seq}
                accs = [float(w.get("accuracy_score") or 0) for w in found_seq]
                mean_acc = round(sum(accs) / len(accs), 1) if accs else 0
                seg_offset = found_seq[0].get("offset_ms")
                seg_end = found_seq[-1].get("end_ms")
                if etypes == {"Omission"}:
                    per_word.append({"word": ref, "score": 0, "error": "漏读"})
                elif "Mispronunciation" in etypes or "Omission" in etypes:
                    per_word.append({"word": ref, "score": mean_acc, "error": "发音错误",
                                     "offset_ms": seg_offset, "end_ms": seg_end})
                else:
                    per_word.append({"word": ref, "score": mean_acc, "error": None,
                                     "offset_ms": seg_offset, "end_ms": seg_end})

            read_count = sum(1 for w in per_word if w["error"] != "漏读")
            accuracy_overall = sum(w["score"] for w in per_word) / len(per_word) if per_word else 0
            completeness = (read_count / len(reference_words) * 100) if reference_words else 0
            fluency = sum(fluency_parts) / len(fluency_parts) if fluency_parts else 0

            overall = accuracy_overall * 0.7 + completeness * 0.15 + fluency * 0.15

            # unbiased transcript cross-check (same idea as single-word strict layer)
            independent = ""
            if transcribe_future is not None:
                try:
                    independent = transcribe_future.result(timeout=200)
                except Exception:
                    pass
            token_ratio = None
            if independent:
                ref_tokens = self._normalize_text(reference_text).split()
                heard_tokens = self._normalize_text(independent).split()
                sm = difflib.SequenceMatcher(None, ref_tokens, heard_tokens)
                matched = sum(b.size for b in sm.get_matching_blocks())
                token_ratio = matched / max(len(ref_tokens), len(heard_tokens)) if heard_tokens else 0.0
                # if the unbiased transcript heard far fewer of the words, trust it
                if token_ratio < (read_count / len(reference_words)) * 0.6:
                    overall = min(overall, 55.0)

            return {
                "mode": "continuous",
                "pronunciation_score": round(max(0.0, min(100.0, overall)), 1),
                "accuracy_score": round(accuracy_overall, 1),
                "completeness_score": round(completeness, 1),
                "fluency_score": round(fluency, 1),
                "recognized_text": " ".join(texts),
                "independent_transcript": independent,
                "token_match_ratio": round(token_ratio, 2) if token_ratio is not None else None,
                "words_read": read_count,
                "words_total": len(reference_words),
                "insertions": insertions,
                "per_word": per_word,
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e), "pronunciation_score": 0, "per_word": []}
        finally:
            if transcribe_future is not None and not transcribe_future.done():
                try:
                    transcribe_future.result(timeout=200)
                except Exception:
                    pass
            if converted and converted != audio_file_path:
                try:
                    if os.path.exists(converted):
                        os.remove(converted)
                except OSError:
                    pass

pronunciation_service = PronunciationService()