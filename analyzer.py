import json
import re
import requests
from rag_reference import RAG_REFERENCE

GEMINI_MODEL = "gemini-3.1-flash-lite"


def _call_gemini(api_key: str, prompt: str, max_tokens: int = 3000) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise ValueError(data["error"]["message"])
    return data["candidates"][0]["content"]["parts"][0]["text"]


def chat_reply(api_key: str, history: list[dict], user_msg: str) -> str:
    """챗봇 탭: 대화 히스토리 기반 응답"""
    contents = []
    for turn in history:
        contents.append({"role": turn["role"], "parts": [{"text": turn["text"]}]})
    contents.append({"role": "user", "parts": [{"text": user_msg}]})

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {
        "system_instruction": {
            "parts": [{"text": "You are a helpful educational assistant. Respond in Korean. Be concise and friendly."}]
        },
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.7},
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise ValueError(data["error"]["message"])
    return data["candidates"][0]["content"]["parts"][0]["text"]


def build_analysis_prompt(prompts: list[str]) -> str:
    avg_len = int(sum(len(p) for p in prompts) / max(len(prompts), 1))
    sample = "\n".join(f"[{i+1}] {p}" for i, p in enumerate(prompts[:30]))

    return f"""You are an AI literacy education expert analyzing a learner's AI prompt usage habits.
Your report will be READ DIRECTLY by middle and high school students (ages 13-18).
Write ALL Korean text with these strict rules:
1. Always use FORMAL POLITE speech ending (합쇼체 or 해요체): ~해요, ~입니다, ~있어요, ~거예요.
2. NEVER mix informal speech (~야, ~지, ~해, ~거야) with formal speech in the same report.
3. Refer to the learner as "사용자님" throughout the entire report.
4. Use simple, everyday vocabulary a middle schooler understands.
5. If a technical term is unavoidable, explain it simply in parentheses right after.
Example of CORRECT tone: "사용자님은 주로 AI에게 정보를 찾아달라고 하셨어요."
Example of WRONG tone: "넌 AI를 검색창처럼 쓰고 있어. 조금만 더 자세히 설명해봐."

REFERENCE FRAMEWORKS (use these as your evaluation basis):
{RAG_REFERENCE}

LEARNER DATA:
- Total prompts: {len(prompts)}
- Average prompt length: {avg_len} characters
- Prompt samples:
{sample}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS PROCEDURE — follow in this exact order:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1 — Infer the PURPOSE of each prompt.
  For each prompt sample, ask: "What was this learner actually trying to do?"
  Group them into purposes (e.g., 숙제 도움, 정보 검색, 아이디어 얻기, 글쓰기 도움, 궁금증 해소 등).
  Store the top 2-3 inferred purposes in "prompt_purposes".

STEP 2 — Evaluate how WELL the prompts serve their inferred purpose.
  For each purpose group: did the learner write prompts that would actually get a useful answer?
  Use this rubric per purpose:
    - Did they give enough context for that goal?
    - Did they specify what format or detail level they wanted?
    - Did they follow up or refine based on AI answers?
  Store this evaluation in "purpose_fit_analysis".

STEP 3 — Classify question types and interaction patterns (Frameworks 1 & 2).
STEP 4 — Score overall AI literacy (0-100) based on ALL steps above.
STEP 5 — Identify 3 AI literacy concepts the learner likely doesn't know yet.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Output ONLY valid JSON. No markdown, no explanation, no preamble.
2. ALL Korean text must be written at middle-school reading level.
   - Use "~해요", "~거예요" style (not formal academic style).
   - Replace jargon: "맥락" → "배경 설명", "반추" → "되돌아보기", "메타인지" → "내 생각을 점검하기".
3. q_types and interaction_codes values must be INTEGER counts.

{{
  "habit": {{
    "total": {len(prompts)},
    "avg_length": {avg_len},
    "top_keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
    "summary": "사용자님이 AI를 어떻게 사용하셨는지 2-3문장으로 쉽게 설명해주세요. 중학생이 읽는다고 생각하고 존댓말로 써주세요.",
    "insight": "사용자님에게 전하는 가장 중요한 한 마디. 응원하는 톤으로, 존댓말로."
  }},
  "purpose_analysis": {{
    "prompt_purposes": [
      {{"purpose": "사용자님이 AI를 사용한 주된 목적 (예: 숙제 도움, 정보 검색)", "count": 0, "examples": ["실제 프롬프트 예시 1", "예시 2"]}},
      {{"purpose": "두 번째 목적", "count": 0, "examples": ["예시"]}}
    ],
    "purpose_fit_analysis": "목적별로 프롬프트가 잘 작성됐는지 평가해주세요. 예: '숙제 도움을 받으려 하셨는데, 어떤 과목인지, 어디까지 알고 계신지를 알려주지 않아서 AI가 너무 일반적인 답변을 드렸을 거예요.' 처럼 구체적으로, 존댓말로.",
    "purpose_fit_score": "목적에 맞게 잘 쓰셨으면 높음 / 보통 / 낮음 중 하나"
  }},
  "usage_type": {{
    "q_types": {{"정보": 0, "적용": 0, "분석": 0, "평가": 0, "창안": 0}},
    "interaction_codes": {{"IG": 0, "B": 0, "EI": 0, "EA": 0, "R": 0}},
    "dominant_model": "모델A형 또는 모델B형 또는 단순의존형",
    "model_reason": "왜 이 모델로 분류했는지 2문장 이상. 사용자님께 존댓말로 설명해주세요.",
    "analysis_text": "사용자님의 질문 방식과 AI와 대화하는 패턴을 중학생이 이해할 수 있게 3-4문장으로 설명해주세요. 존댓말로."
  }},
  "score": {{
    "value": 0,
    "level": "입문 또는 기초 또는 중급 또는 고급",
    "level_desc": "사용자님의 현재 수준을 쉽게 설명해주세요. 예: '사용자님은 아직 AI를 검색창처럼 사용하고 계세요.' 처럼 친근하되 존댓말로.",
    "improvements": [
      "구체적인 개선 방법 1 — 어떻게 바꾸면 되는지 행동으로 설명. 존댓말로.",
      "개선 방법 2",
      "개선 방법 3"
    ],
    "before_prompt": "사용자님이 실제로 쓰신 것 같은 전형적인 프롬프트 예시",
    "after_prompt": "같은 목적인데 훨씬 잘 쓴 프롬프트 예시. 왜 더 나은지 한 줄 설명 포함."
  }},
  "literacy_gaps": [
    {{
      "concept": "사용자님이 아직 모르시는 AI 활용 개념 (중학생이 이해할 수 있는 이름으로)",
      "explanation": "이 개념이 무엇인지 중학생에게 설명하듯이 존댓말로. 비유나 예시 포함. 2-3문장.",
      "example": "사용자님의 실제 프롬프트에서 이 개념이 없어서 생긴 문제 + 어떻게 고치면 되는지. 존댓말로."
    }},
    {{"concept": "두 번째 개념", "explanation": "설명", "example": "사례"}},
    {{"concept": "세 번째 개념", "explanation": "설명", "example": "사례"}}
  ]
}}"""


def analyze(api_key: str, prompts: list[str]) -> dict:
    """프롬프트 목록을 분석해서 보고서 dict 반환"""
    prompt = build_analysis_prompt(prompts)
    raw = _call_gemini(api_key, prompt, max_tokens=3000)
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)
