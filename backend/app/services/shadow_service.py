"""
Shadow scoring: forward each real submission to the self-hosted
speakright-ml model (wav2vec2 GOP) and log its score next to Azure's.
Fire-and-forget — never affects the user-facing result.
"""

import os
import time
import sqlite3
import shutil
import subprocess
import tempfile
import threading

import requests

SHADOW_ML_URL = os.getenv(
    "SHADOW_ML_URL",
    "http://159.89.193.226:8002/pronunciation-assessment/file"
)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app.db")


def submit_shadow(recording_id: int, word_text: str, audio_path: str, assessment: dict):
    """Send the audio to the shadow model in a background thread."""
    def run():
        started = time.time()
        ml_pron = ml_acc = None
        ml_recognized = None
        error = None
        wav_path = None
        try:
            # the shadow model needs 16k mono wav; original upload may be webm/44.1k
            fd, wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", audio_path,
                 "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", wav_path],
                check=True, timeout=60
            )
            with open(wav_path, "rb") as f:
                resp = requests.post(
                    SHADOW_ML_URL,
                    files={"audio_file": ("audio.wav", f, "audio/wav")},
                    data={"reference_text": word_text},
                    timeout=120,
                )
            resp.raise_for_status()
            nbest = (resp.json().get("NBest") or [{}])[0]
            ml_pron = nbest.get("PronScore")
            ml_acc = nbest.get("AccuracyScore")
            ml_recognized = nbest.get("Display") or nbest.get("Lexical")
        except Exception as e:
            error = str(e)[:300]
        finally:
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)

        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            conn.execute(
                "INSERT INTO shadow_scores (recording_id, word_text, azure_score, azure_accuracy, final_score, ml_pron_score, ml_accuracy, ml_recognized, ml_error, latency_ms) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    recording_id,
                    word_text,
                    assessment.get("azure_pronunciation_score"),
                    assessment.get("accuracy_score"),
                    assessment.get("pronunciation_score"),
                    ml_pron,
                    ml_acc,
                    ml_recognized,
                    error,
                    int((time.time() - started) * 1000),
                ),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Shadow score logging failed: {e}")

    if not shutil.which("ffmpeg"):
        return
    threading.Thread(target=run, daemon=True, name="shadow-score").start()
