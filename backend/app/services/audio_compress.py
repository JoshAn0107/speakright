"""Generate a small MP3 sibling for each saved recording.

Uncompressed WAVs (~32KB/s) are unplayable over cross-border mobile data;
a 24kbps mono MP3 is ~30x smaller and streams instantly. Fire-and-forget.
"""

import subprocess
import threading


def compress_async(audio_path: str):
    def run():
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", audio_path,
                 "-ac", "1", "-b:a", "24k", f"{audio_path}.mp3"],
                timeout=120, check=False
            )
        except Exception as e:
            print(f"mp3 compress failed (non-fatal): {e}")
    threading.Thread(target=run, daemon=True).start()
