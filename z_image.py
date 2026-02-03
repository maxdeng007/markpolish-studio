"""
Z-Image-Turbo (DashScope + ModelScope 魔搭) client for MarkPolish Studio.
Single place for text-to-image API calls. No UI; pure function.
"""

import base64
import os
import time
import requests
from typing import Optional

# Load .env as soon as this module is imported (so keys are available before any API call)
def _load_env():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_try = [
        os.path.join(_this_dir, ".env"),
        os.path.join(os.getcwd(), ".env"),
        ".env",
    ]
    try:
        from dotenv import load_dotenv
        for path in paths_to_try:
            if path and os.path.isfile(path):
                load_dotenv(path, override=True)
    except ImportError:
        pass
    # Manual fallback: read .env and set os.environ (handles path/encoding issues)
    want = ("MODELSCOPE_API_KEY", "MODELSCOPE_SDK_TOKEN", "DASHSCOPE_API_KEY")
    canon = {"modelscope_api_key": "MODELSCOPE_API_KEY", "modelscope_sdk_token": "MODELSCOPE_SDK_TOKEN", "dashscope_api_key": "DASHSCOPE_API_KEY"}
    for path in paths_to_try:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if not v:
                        continue
                    c = canon.get(k.lower()) or (k if k in want else None)
                    if c and not os.environ.get(c):
                        os.environ[c] = v
        except Exception:
            pass
        break

_load_env()

# DashScope synchronous generation endpoint
DASHSCOPE_GENERATION_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
# ModelScope 魔搭: async submit then poll task
MODELSCOPE_BASE = "https://api-inference.modelscope.cn/v1"
MODELSCOPE_GENERATIONS_URL = f"{MODELSCOPE_BASE}/images/generations"
TIMEOUT_SECONDS = 30
MODELSCOPE_POLL_INTERVAL = 5
MODELSCOPE_POLL_MAX_WAIT = 300  # max seconds to wait for task (5 min)

# Aspect ratio presets: label -> "width*height" for DashScope; same string parsed for ModelScope
IMAGE_SIZE_PRESETS = {
    "1:1": "1024*1024",
    "16:9": "1280*720",
    "9:16": "720*1280",
}


def _parse_size(size: str):
    """Parse 'width*height' string to (width, height). Default (1024, 1024) if invalid."""
    if not size or "*" not in size:
        return 1024, 1024
    parts = size.strip().split("*")
    if len(parts) != 2:
        return 1024, 1024
    try:
        w, h = int(parts[0].strip()), int(parts[1].strip())
        return (w, h) if w > 0 and h > 0 else (1024, 1024)
    except ValueError:
        return 1024, 1024


def get_dashscope_api_key() -> Optional[str]:
    """Get DashScope API key from environment or Streamlit Secrets."""
    key = os.getenv("DASHSCOPE_API_KEY")
    if key and str(key).strip():
        return key.strip()
    _load_env()
    key = os.getenv("DASHSCOPE_API_KEY")
    if key and str(key).strip():
        return key.strip()
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            key = st.secrets.get("DASHSCOPE_API_KEY")
            if key and str(key).strip():
                return key.strip()
    except Exception:
        pass
    return None


def get_modelscope_api_key() -> Optional[str]:
    """Get ModelScope (魔搭) API key from environment or Streamlit Secrets."""
    key = os.getenv("MODELSCOPE_API_KEY") or os.getenv("MODELSCOPE_SDK_TOKEN")
    if key and str(key).strip():
        return key.strip()
    _load_env()  # retry loading .env in case it was not available at import time
    key = os.getenv("MODELSCOPE_API_KEY") or os.getenv("MODELSCOPE_SDK_TOKEN")
    if key and str(key).strip():
        return key.strip()
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            key = st.secrets.get("MODELSCOPE_API_KEY") or st.secrets.get("MODELSCOPE_SDK_TOKEN")
            if key and str(key).strip():
                return key.strip() if isinstance(key, str) else None
    except Exception:
        pass
    return None


def generate_image(prompt: str, api_key: Optional[str] = None, size: str = "1024*1024") -> Optional[str]:
    """
    Call DashScope Z-Image-Turbo to generate an image from text.
    Returns data URI (data:image/png;base64,...) or None on error/missing key.
    """
    key = api_key if api_key is not None else get_dashscope_api_key()
    if not key or not prompt or not prompt.strip():
        return None
    if not size or "*" not in size:
        size = "1024*1024"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    body = {
        "model": "z-image-turbo",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt.strip()[:800]}],
                }
            ]
        },
        "parameters": {
            "prompt_extend": False,
            "size": size,
        },
    }

    try:
        resp = requests.post(
            DASHSCOPE_GENERATION_URL,
            headers=headers,
            json=body,
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        output = data.get("output") or {}
        choices = output.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        content_list = message.get("content") or []
        image_url = None
        for item in content_list:
            if isinstance(item, dict) and "image" in item:
                image_url = item.get("image")
                break
        if not image_url:
            return None
        img_resp = requests.get(image_url, timeout=TIMEOUT_SECONDS)
        img_resp.raise_for_status()
        b64 = base64.b64encode(img_resp.content).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def _modelscope_log(msg: str, detail: Optional[str] = None) -> None:
    try:
        out = "[ModelScope] " + msg
        if detail:
            out += " " + (detail[:500] + "..." if len(detail) > 500 else detail)
        print(out, flush=True)
    except Exception:
        pass


def _fetch_image_as_data_uri(image_url: str) -> Optional[str]:
    try:
        img_resp = requests.get(image_url, timeout=TIMEOUT_SECONDS)
        img_resp.raise_for_status()
        b64 = base64.b64encode(img_resp.content).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        _modelscope_log("Failed to fetch image URL", str(e))
        return None


def _extract_image_url_from_task(task_data: dict) -> Optional[str]:
    output_raw = task_data.get("output") or task_data.get("data")
    if isinstance(output_raw, list) and output_raw:
        first = output_raw[0]
        if isinstance(first, str) and first.startswith(("http://", "https://")):
            return first
        if isinstance(first, dict):
            u = first.get("url") or first.get("image") or first.get("link")
            if u and isinstance(u, str):
                return u
    output = output_raw if isinstance(output_raw, dict) else {}
    if isinstance(output, dict):
        for key in ("output_images", "output_imgs", "results", "outputs", "images", "url"):
            val = output.get(key)
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, str) and first.startswith(("http://", "https://")):
                    return first
                if isinstance(first, dict):
                    u = first.get("url") or first.get("image") or first.get("link")
                    if u and isinstance(u, str):
                        return u
            if isinstance(val, str) and val.startswith(("http://", "https://")):
                return val
    outputs = task_data.get("outputs")
    if isinstance(outputs, list) and outputs:
        first = outputs[0]
        if isinstance(first, str) and first.startswith(("http://", "https://")):
            return first
        if isinstance(first, dict):
            u = first.get("url") or first.get("image")
            if u:
                return u
    def find_url(obj, depth=0):
        if depth > 10:
            return None
        if isinstance(obj, str) and obj.startswith(("http://", "https://")):
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                u = find_url(v, depth + 1)
                if u:
                    return u
        if isinstance(obj, list):
            for v in obj:
                u = find_url(v, depth + 1)
                if u:
                    return u
        return None
    return find_url(task_data)


def generate_image_modelscope(prompt: str, api_key: Optional[str] = None, size: str = "1024*1024") -> Optional[str]:
    """
    Call ModelScope (魔搭) Z-Image-Turbo via async API.
    Returns data URI or None. Sends requested size so API returns same ratio (16:9 -> 1280x720).
    """
    key = api_key if api_key is not None else get_modelscope_api_key()
    if not key or not prompt or not prompt.strip():
        return None
    key = key.strip()
    width, height = _parse_size(size)
    size_str_modelscope = f"{width}x{height}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "X-ModelScope-Async-Mode": "true",
    }
    body_async = {
        "model": "Tongyi-MAI/Z-Image-Turbo",
        "prompt": prompt.strip()[:800],
        "size": size_str_modelscope,
        "width": width,
        "height": height,
        "num_inference_steps": 9,
        "guidance_scale": 0.0,
    }
    try:
        resp = requests.post(
            MODELSCOPE_GENERATIONS_URL, headers=headers, json=body_async, timeout=TIMEOUT_SECONDS
        )
        data = resp.json() if resp.content else {}
        if resp.status_code != 200:
            err_msg = str(data.get("errors") or data)
            if ("queue is full" in err_msg or "user queue is full" in err_msg) and resp.status_code == 400:
                _modelscope_log("ModelScope queue full — retrying once in 20s...", "")
                time.sleep(20)
                resp2 = requests.post(
                    MODELSCOPE_GENERATIONS_URL, headers=headers, json=body_async, timeout=TIMEOUT_SECONDS
                )
                data = resp2.json() if resp2.content else {}
                if resp2.status_code != 200:
                    _modelscope_log("ModelScope queue still full — try again in a minute.", str(data)[:300])
                    return None
            else:
                _modelscope_log("Async submit HTTP " + str(resp.status_code), err_msg[:500])
                return None
        task_id = data.get("task_id") or (data.get("data") or {}).get("task_id")
        if not task_id:
            _modelscope_log("Async: no task_id in response", str(data)[:500])
            return None
        headers_poll = {"Authorization": f"Bearer {key}", "X-ModelScope-Task-Type": "image_generation"}
        task_url = f"{MODELSCOPE_BASE}/tasks/{task_id}"
        deadline = time.monotonic() + MODELSCOPE_POLL_MAX_WAIT
        while time.monotonic() < deadline:
            time.sleep(MODELSCOPE_POLL_INTERVAL)
            poll_resp = requests.get(task_url, headers=headers_poll, timeout=TIMEOUT_SECONDS)
            poll_resp.raise_for_status()
            task_data = poll_resp.json()
            status = task_data.get("task_status") or (task_data.get("data") or {}).get("task_status")
            if status in ("SUCCEED", "SUCCESS"):
                image_url = _extract_image_url_from_task(task_data)
                if image_url:
                    return _fetch_image_as_data_uri(image_url)
                _modelscope_log("Poll: SUCCESS but no image URL", "")
                return None
            if status in ("FAILED", "CANCELED", "CANCELLED"):
                _modelscope_log("Poll: task failed", str(task_data)[:500])
                return None
        _modelscope_log("Poll: timeout waiting for task", task_id)
    except Exception as e:
        _modelscope_log("Async flow failed", str(e))
    return None
