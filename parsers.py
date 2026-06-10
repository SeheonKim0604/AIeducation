import json
import re


def parse_json(file_bytes: bytes) -> list[str]:
    """ChatGPT conversations.json에서 사용자 프롬프트 추출"""
    data = json.loads(file_bytes.decode("utf-8"))
    prompts = []
    arr = data if isinstance(data, list) else [data]
    for conv in arr:
        mapping = conv.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message")
            if not msg:
                continue
            if msg.get("author", {}).get("role") != "user":
                continue
            parts = msg.get("content", {}).get("parts", [])
            text = " ".join(p for p in parts if isinstance(p, str)).strip()
            if len(text) > 5:
                prompts.append(text)
    return prompts


def parse_pdf(file_bytes: bytes) -> list[dict]:
    """
    PDF에서 줄 단위로 텍스트 추출.
    반환: [{"text": ..., "auto_checked": None}, ...]
    classify_blocks_with_gemini() 호출 후 사용자/AI 구분됨.
    """
    import fitz  # pymupdf

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    lines = []
    for page in doc:
        for line in page.get_text().splitlines():
            line = line.strip()
            if len(line) >= 10:   # 너무 짧은 줄(페이지번호, 헤더 등) 제거
                lines.append({"text": line, "auto_checked": None})
    return lines


def parse_paste(raw_text: str) -> list[dict]:
    """
    붙여넣기 텍스트를 빈 줄 기준으로 블록 분리.
    반환: [{"text": ..., "auto_checked": None}, ...]
    auto_checked는 classify_blocks_with_gemini() 호출 후 채워짐.
    """
    blocks = [b.strip() for b in re.split(r"\n{2,}", raw_text) if b.strip()]
    return [{"text": block, "auto_checked": None} for block in blocks]


def classify_blocks_with_gemini(blocks: list[dict], api_key: str) -> list[dict]:
    """
    Gemini API를 사용해 각 블록이 사용자 발화인지 AI 답변인지 분류.
    반환: [{"text": ..., "auto_checked": bool, "role": str}, ...]
    """
    import requests

    GEMINI_MODEL = "gemini-3.1-flash-lite"

    block_list = "\n".join(
        f'[{i}] {b["text"][:120]}{"…" if len(b["text"]) > 120 else ""}'
        for i, b in enumerate(blocks)
    )

    prompt = f"""You are analyzing a pasted chat conversation between a human user and an AI assistant (e.g. ChatGPT, Gemini, Claude).

Below are text blocks extracted from the conversation (separated by blank lines).
Each block is either written by the HUMAN USER or by the AI ASSISTANT.

Classify each block by its index number.

Human user characteristics:
- Short, direct requests or questions
- Conversational, informal tone possible
- Asks for information, help, or tasks
- May be incomplete sentences
- Written in first person

AI assistant characteristics:
- Longer, structured explanations
- Uses numbered lists, bullet points, headers
- Polite, formal tone
- Provides multiple options or detailed answers

BLOCKS TO CLASSIFY:
{block_list}

STRICT OUTPUT RULES:
- Output ONLY a raw JSON array. No markdown. No explanation. No extra text before or after.
- Every block index from 0 to {len(blocks)-1} must appear exactly once.
- Format: [{{"index": 0, "role": "user"}}, {{"index": 1, "role": "ai"}}, ...]"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max(512, len(blocks) * 30),
            "temperature": 0.0,
        },
    }

    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # JSON 배열만 추출 (앞뒤 텍스트, 마크다운 펜스 모두 제거)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise ValueError(f"JSON 배열을 찾을 수 없어요. Gemini 응답:\n{raw[:300]}")
    classifications = json.loads(match.group())

    role_map = {item["index"]: item["role"] for item in classifications}

    # 혹시 누락된 인덱스가 있으면 fallback으로 "unknown" 처리
    result = []
    for i, block in enumerate(blocks):
        role = role_map.get(i, "unknown")
        result.append({
            "text": block["text"],
            "auto_checked": (role == "user"),
            "role": role,
        })
    return result
