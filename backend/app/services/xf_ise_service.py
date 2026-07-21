"""讯飞语音评测(ISE)流式版客户端。

国内节点、独立额度、专门针对少儿英语优化——作为主评分服务，避免 Azure
的跨境延迟和配额问题。输出对齐现有 assessment 结构（pronunciation_score
0-100 + words），供严格校验层和前端直接复用。
"""

import base64
import hashlib
import hmac
import json
import os
import ssl
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

try:
    import websocket  # websocket-client
    _WS_OK = True
except Exception:
    _WS_OK = False

HOST = "ise-api.xfyun.cn"
PATH = "/v2/open-ise"


def _creds():
    from app.core.config import settings
    return settings.XF_APPID, settings.XF_API_KEY, settings.XF_API_SECRET


def _configured():
    a, k, sec = _creds()
    return bool(a and k and sec)


def _build_url():
    _appid, api_key, api_secret = _creds()
    date = format_date_time(mktime(datetime.now().timetuple()))
    origin = f"host: {HOST}\ndate: {date}\nGET {PATH} HTTP/1.1"
    sig = base64.b64encode(
        hmac.new(api_secret.encode(), origin.encode(), hashlib.sha256).digest()
    ).decode()
    auth = (f'api_key="{api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{sig}"')
    auth_b64 = base64.b64encode(auth.encode()).decode()
    return f"wss://{HOST}{PATH}?" + urlencode(
        {"authorization": auth_b64, "date": date, "host": HOST}
    )


def _read_pcm(wav_path):
    with open(wav_path, "rb") as f:
        audio = f.read()
    if audio[:4] == b"RIFF":
        idx = audio.find(b"data")
        audio = audio[idx + 8:] if idx != -1 else audio[44:]
    return audio


def _evaluate(wav_path, text, category):
    audio = _read_pcm(wav_path)
    appid = _creds()[0]
    result = {}
    done = threading.Event()

    def on_open(ws):
        def send():
            marker = "[word]" if category == "read_word" else "[content]"
            ssb = {
                "category": category, "rstcd": "utf8", "sub": "ise",
                "ent": "en_vip", "tte": "utf-8", "cmd": "ssb",
                "auf": "audio/L16;rate=16000", "aue": "raw",
                "text": marker + "\n" + text,
            }
            ws.send(json.dumps({"common": {"app_id": appid}, "business": ssb,
                                "data": {"status": 0, "data": ""}}))
            frame = 1280
            i, first = 0, True
            while i < len(audio):
                chunk = audio[i:i + frame]
                i += frame
                last = i >= len(audio)
                aus = 1 if first else (4 if last else 2)
                first = False
                try:
                    ws.send(json.dumps({
                        "business": {"cmd": "auw", "aus": aus, "aue": "raw"},
                        "data": {"status": 2 if last else 1,
                                 "data": base64.b64encode(chunk).decode(),
                                 "data_type": 1, "encoding": "raw"},
                    }))
                except Exception:
                    return  # ws 已关闭（讯飞返回错误），停止发送
                time.sleep(0.04)
        threading.Thread(target=send, daemon=True).start()

    def on_message(ws, msg):
        m = json.loads(msg)
        if m.get("code") != 0:
            result["error"] = "code=" + str(m.get("code")) + " " + str(m.get("message"))
            ws.close()
            return
        data = m.get("data", {})
        if data.get("status") == 2:
            result["xml"] = base64.b64decode(data["data"]).decode("gbk", errors="ignore")
            ws.close()

    def on_error(ws, e):
        result["error"] = str(e)

    def on_close(ws, *a):
        done.set()

    ws = websocket.WebSocketApp(_build_url(), on_open=on_open,
                                on_message=on_message, on_error=on_error,
                                on_close=on_close)
    threading.Thread(
        target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}),
        daemon=True,
    ).start()
    done.wait(timeout=120)
    if "error" in result:
        raise RuntimeError(result["error"])
    if "xml" not in result:
        raise RuntimeError("xfyun timeout")
    return result["xml"]


def _score100(v):
    try:
        return round(float(v) * 20, 1)
    except (TypeError, ValueError):
        return 0.0


def _parse(xml_str):
    root = ET.fromstring(xml_str)
    # XML 有多个 read_word/read_sentence 节点，取带 total_score 属性的那个
    top = None
    for tag in ("read_word", "read_sentence", "read_chapter"):
        for node in root.iter(tag):
            if node.get("total_score") is not None:
                top = node
                break
        if top is not None:
            break
    total = _score100(top.get("total_score")) if top is not None else 0.0
    rejected = (top.get("is_rejected") == "true") if top is not None else False

    words = []
    for w in root.iter("word"):
        content = (w.get("content") or "").strip()
        if not content or content in ("sil", "silv", "fil"):
            continue
        dp = w.get("dp_message", "0")
        acc = _score100(w.get("total_score"))
        if not acc:
            acc = total
        words.append({"word": content, "accuracy_score": acc,
                      "error_type": ("Omission" if dp == "16" else "None")})

    return {
        "recognized_text": " ".join(x["word"] for x in words),
        "pronunciation_score": 0.0 if rejected else total,
        "accuracy_score": total,
        "fluency_score": None,
        "completeness_score": None,
        "words": words,
        "scorer": "xfyun",
        "rejected": rejected,
    }


def available():
    return _WS_OK and _configured()


def assess_word(wav_path, word):
    if not available():
        return None
    try:
        return _parse(_evaluate(wav_path, word, "read_word"))
    except Exception as e:
        print("XF ISE assess_word failed:", e)
        return None


def assess_words(wav_path, reference_words):
    """连读多词评测：read_word 接受换行分隔的词表，逐词返回分数+漏读。"""
    if not available():
        return None
    try:
        text = "\n".join(reference_words)
        return _parse(_evaluate(wav_path, text, "read_word"))
    except Exception as e:
        print("XF ISE assess_words failed:", e)
        return None


# ---- 境内评分节点转发 ----
import requests as _requests

def _node_url():
    from app.core.config import settings
    return getattr(settings, "SCORING_NODE_URL", None) or os.getenv("SCORING_NODE_URL")


def _node_token():
    from app.core.config import settings
    return getattr(settings, "SCORING_NODE_TOKEN", None) or os.getenv("SCORING_NODE_TOKEN") or "sr-cn-2026-xfyun"


def assess_via_node(wav_path, reference_words, poll_timeout=180):
    """转发到境内评分节点（异步 job + 轮询，避免跨境长连接）。返回 dict 或 None。"""
    url = _node_url()
    if not url:
        return None
    base = url.rstrip("/")
    hdr = {"X-Token": _node_token()}
    try:
        with open(wav_path, "rb") as f:
            resp = _requests.post(
                base + "/score", headers=hdr,
                files={"audio_file": ("audio.wav", f, "audio/wav")},
                data={"reference": "\n".join(reference_words)},
                timeout=30,
            )
        resp.raise_for_status()
        job_id = resp.json().get("job_id")
        if not job_id:
            return None
        deadline = time.time() + poll_timeout
        while time.time() < deadline:
            time.sleep(3)
            pr = _requests.get(base + f"/result/{job_id}", headers=hdr, timeout=15)
            if pr.status_code != 200:
                continue
            j = pr.json()
            if j.get("status") == "done":
                return j["result"]
            if j.get("status") == "error":
                print(f"scoring node error: {j.get('result')}")
                return None
        print("scoring node poll timeout")
        return None
    except Exception as e:
        print(f"scoring node failed, falling back: {e}")
        return None
