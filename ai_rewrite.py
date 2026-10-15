# -*- coding: utf-8 -*-
"""AI rewrite: prompt building, candidate parsing, API calls."""
import json
import re
import urllib.request
from .config import PAYLOAD_MARKER

# ============================================================
# AI rewrite
# ============================================================
REWRITE_STYLES = {
    "自然口语": "把下面这段文本改写成日常自然口语",
    "书面正式": "把下面这段文本改写成正式书面语",
    "故事叙述": "把下面这段文本改写成一个自然的故事叙述段落",
    "邮件风格": "把下面这段文本改写成邮件正文风格",
    "备忘录": "把下面这段文本改写成工作备忘录风格",
}


def build_rewrite_prompt(style, text, n_candidates=1):
    base = REWRITE_STYLES.get(style, "把下面这段文本改写")
    if n_candidates <= 1:
        return f"{base}，保持原意和所有关键标记（如 {PAYLOAD_MARKER}）不变：\n{text}"
    return (
        f"{base}，生成 {n_candidates} 个不同表达方式的版本。\n"
        f"要求：\n"
        f"1. 每个版本保持原意，尤其是 {PAYLOAD_MARKER} 这类标记必须完整保留；\n"
        f"2. 版本之间用一行 \"---\" 分隔；\n"
        f"3. 只输出改写结果，不要编号、不要任何解释。\n\n"
        f"原文：\n{text}"
    )


def parse_candidates(text, expect_count=1):
    """Split API response into multiple candidates."""
    if not text:
        return [""]
    if expect_count <= 1:
        return [text.strip()]
    parts = re.split(r"\n\s*-{3,}\s*\n", text)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) < 2:
        parts = re.split(r"\n(?=\s*\d+[\.、])", text)
        parts = [re.sub(r"^\s*\d+[\.、]\s*", "", p).strip() for p in parts if p.strip()]
    return parts if parts else [text.strip()]


def call_openai_compatible(endpoint, api_key, model, prompt, timeout=60):
    url = endpoint.rstrip("/") + "/v1/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"unexpected response structure: {data}")


def call_ollama(endpoint, model, prompt, timeout=120):
    url = endpoint.rstrip("/") + "/api/generate"
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "")