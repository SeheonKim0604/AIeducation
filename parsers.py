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


def parse_pdf(file_bytes: bytes) -> list[str]:
    """PDF에서 텍스트 줄 추출 (20자 이상만)"""
    import fitz  # pymupdf
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    lines = []
    for page in doc:
        text = page.get_text()
        for line in text.splitlines():
            line = line.strip()
            if len(line) >= 20:
                lines.append(line)
    return lines


def parse_paste(raw_text: str) -> list[dict]:
    """
    붙여넣기 텍스트를 빈 줄 기준으로 블록 분리.
    반환: [{"text": ..., "auto_checked": bool}, ...]
    auto_checked는 요청형 어미로 끝나면 True (사용자가 수정 가능)
    """
    user_end_pattern = re.compile(
        r"[?？]$|줘$|까$|나요$|세요$|해봐$|알려줘$|해줘$|주세요$|볼까$|할까$"
    )

    blocks = [b.strip() for b in re.split(r"\n{2,}", raw_text) if b.strip()]
    result = []
    for block in blocks:
        last_line = [l.strip() for l in block.splitlines() if l.strip()]
        last_line = last_line[-1] if last_line else ""
        auto_checked = bool(user_end_pattern.search(last_line))
        result.append({"text": block, "auto_checked": auto_checked})
    return result
