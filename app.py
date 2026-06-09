import streamlit as st
import json
import re

from parsers import parse_json, parse_pdf, parse_paste, classify_blocks_with_gemini
from analyzer import analyze, chat_reply

# ════════════════════════════════════════
#  페이지 설정
# ════════════════════════════════════════
st.set_page_config(
    page_title="AI 리터러시 피드백",
    page_icon="🔍",
    layout="wide",
)

# ════════════════════════════════════════
#  공통 CSS
# ════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.al-topbar {
    background:#0f0e0c; color:#fff; padding:14px 24px;
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom:24px; border-radius:4px;
}
.al-topbar-brand { font-family:monospace; font-size:15px; font-weight:700; letter-spacing:.15em; }
.al-topbar-brand span { color:#6ea8d8; }

.al-section-label {
    font-family:monospace; font-size:10px; font-weight:700;
    letter-spacing:.18em; text-transform:uppercase; color:#888480; margin-bottom:4px;
}
.al-section-title { font-size:17px; font-weight:700; letter-spacing:-.02em; margin-bottom:14px; }

.al-card { background:#f9f7f4; border:1px solid #e8e5e0; padding:16px 18px; margin-bottom:8px; border-radius:4px; }
.al-insight {
    padding:14px 16px; background:#f0f4fb;
    border-left:4px solid #1a4a8a; font-size:13px; line-height:1.7;
    margin-bottom:12px; border-radius:0 4px 4px 0;
}
.al-kw {
    display:inline-block; font-family:monospace; font-size:11px; font-weight:600;
    padding:3px 10px; background:#f0f4fb; color:#1a4a8a;
    border:1px solid #c5d8f0; margin:2px; border-radius:3px;
}
.al-bar-wrap { display:inline-block; width:120px; height:8px; background:#e8e5e0; vertical-align:middle; border-radius:4px; }
.al-bar { display:inline-block; height:8px; background:#1a4a8a; border-radius:4px; }
.al-pct { font-family:monospace; font-size:11px; font-weight:700; color:#1a4a8a; margin-left:6px; }

.al-score-num { font-family:monospace; font-size:52px; font-weight:800; line-height:1; }
.al-level { font-size:22px; font-weight:800; margin-bottom:4px; }

.al-prompt-before { background:#fdf0ee; border:1px solid #f5c6c2; padding:12px 14px; margin-bottom:4px; border-radius:4px; }
.al-prompt-after  { background:#edf7f1; border:1px solid #a3d4b5; padding:12px 14px; border-radius:4px; }
.al-prompt-label  { font-family:monospace; font-size:10px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin-bottom:6px; }

.al-literacy-item { border-bottom:1px solid #e8e5e0; padding:14px 0; }
.al-literacy-tag  {
    display:inline-block; font-family:monospace; font-size:10px; font-weight:700;
    padding:3px 8px; background:#fdf6e3; color:#c8960c;
    border:1px solid #e6c96a; margin-right:8px; border-radius:3px;
}
.al-literacy-title { font-size:14px; font-weight:700; display:inline; }
.al-literacy-example {
    margin-top:8px; padding:8px 12px; background:#f9f7f4;
    border-left:3px solid #c8960c; font-size:12px; color:#888480; border-radius:0 4px 4px 0;
}
.al-improve-item { display:flex; gap:8px; padding:8px 0; font-size:13px; border-bottom:1px solid #e8e5e0; }
.al-arrow { color:#1a4a8a; font-weight:700; flex-shrink:0; }
.al-model-tag {
    display:inline-block; padding:8px 14px; font-size:13px; font-weight:700;
    border:1px solid #c5d8f0; background:#f0f4fb; color:#1a4a8a;
    margin-bottom:10px; border-radius:4px;
}
.al-purpose-card {
    background:#f9f7f4; border:1px solid #e8e5e0; padding:12px 16px;
    margin-bottom:8px; border-radius:4px;
}
.section-divider { border:none; border-top:1px solid #e8e5e0; margin:28px 0; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════
#  세션 상태 초기화
# ════════════════════════════════════════
if "prompts" not in st.session_state:
    st.session_state.prompts = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "report" not in st.session_state:
    st.session_state.report = None
if "paste_blocks" not in st.session_state:
    st.session_state.paste_blocks = []


# ════════════════════════════════════════
#  보고서 렌더링 함수
# ════════════════════════════════════════
def score_color(val):
    if val >= 81: return "#1a6b3a"
    if val >= 61: return "#1a4a8a"
    if val >= 31: return "#c8960c"
    return "#c0392b"


def render_report(report: dict):
    h  = report.get("habit", {})
    pa = report.get("purpose_analysis", {})
    u  = report.get("usage_type", {})
    s  = report.get("score", {})
    gaps = report.get("literacy_gaps", [])

    st.markdown("""
    <div class='al-topbar'>
      <span class='al-topbar-brand'>AI·<span>LITERACY</span>·REPORT</span>
      <span style='font-family:monospace;font-size:11px;color:rgba(255,255,255,.45)'>분석 완료</span>
    </div>""", unsafe_allow_html=True)

    # ── SECTION 1: 사용 습관
    st.markdown("<div class='al-section-label'>Section 01</div>", unsafe_allow_html=True)
    st.markdown("<div class='al-section-title'>📊 AI 사용 습관 한눈에 보기</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class='al-card'>
          <div style='font-family:monospace;font-size:10px;color:#888480;margin-bottom:4px'>분석한 질문 수</div>
          <div style='font-size:28px;font-weight:800;color:#1a4a8a'>{h.get('total',0)}<span style='font-size:14px;color:#888480'> 개</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='al-card'>
          <div style='font-family:monospace;font-size:10px;color:#888480;margin-bottom:4px'>질문 평균 길이</div>
          <div style='font-size:28px;font-weight:800;color:#1a4a8a'>{h.get('avg_length',0)}<span style='font-size:14px;color:#888480'> 자</span></div>
        </div>""", unsafe_allow_html=True)

    kws = "".join(f'<span class="al-kw">{k}</span>' for k in h.get("top_keywords", []))
    st.markdown(f"<div style='margin:10px 0'>{kws}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='al-insight'><strong>💡 {h.get('insight','')}</strong></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:13px;line-height:1.8;color:#3a3835'>{h.get('summary','')}</div>", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── SECTION 2: 목적 분석
    st.markdown("<div class='al-section-label'>Section 02</div>", unsafe_allow_html=True)
    st.markdown("<div class='al-section-title'>🎯 질문의 목적 분석</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12px;color:#888480;margin-bottom:12px'>사용자님이 AI에게 무엇을 원하셨는지 먼저 파악했어요.</div>", unsafe_allow_html=True)

    for p in pa.get("prompt_purposes", []):
        ex_chips = "".join(
            f"<span style='display:inline-block;background:#f0f4fb;border:1px solid #c5d8f0;"
            f"padding:2px 8px;margin:2px;font-size:11px;color:#1a4a8a;border-radius:3px'>{ex}</span>"
            for ex in p.get("examples", [])
        )
        st.markdown(f"""
        <div class='al-purpose-card'>
          <div style='font-weight:700;font-size:13px;color:#0f0e0c;margin-bottom:6px'>
            📌 {p.get('purpose','')}
            <span style='font-size:11px;color:#888480;font-weight:400'>({p.get('count',0)}개)</span>
          </div>
          <div>{ex_chips}</div>
        </div>""", unsafe_allow_html=True)

    fit_score = pa.get("purpose_fit_score", "")
    fit_color = {"높음":"#1a6b3a","보통":"#c8960c","낮음":"#c0392b"}.get(fit_score,"#888480")
    fit_bg    = {"높음":"#edf7f1","보통":"#fdf6e3","낮음":"#fdf0ee"}.get(fit_score,"#f9f7f4")
    st.markdown(f"""
    <div style='margin-top:12px'>
      <div style='font-family:monospace;font-size:10px;font-weight:700;letter-spacing:.08em;
                  text-transform:uppercase;color:#888480;margin-bottom:8px'>목적에 맞게 잘 쓰셨나요?</div>
      <div style='display:inline-block;padding:4px 12px;font-size:12px;font-weight:700;
                  background:{fit_bg};color:{fit_color};border:1px solid {fit_color};
                  margin-bottom:10px;border-radius:3px'>{fit_score}</div>
      <div class='al-insight' style='border-color:{fit_color};background:{fit_bg};color:#3a3835'>
        {pa.get('purpose_fit_analysis','')}
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── SECTION 3: 질문 방식
    st.markdown("<div class='al-section-label'>Section 03</div>", unsafe_allow_html=True)
    st.markdown("<div class='al-section-title'>🔬 질문 방식 분석</div>", unsafe_allow_html=True)

    qt = u.get("q_types", {})
    qt_total = max(sum(qt.values()), 1)
    st.markdown("<div style='font-family:monospace;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#888480;margin-bottom:8px'>어떤 종류의 질문을 하셨나요?</div>", unsafe_allow_html=True)
    qt_bars = ""
    for name, val in qt.items():
        pct = int(val / qt_total * 100)
        qt_bars += (
            f"<div style='padding:5px 0;font-size:12px;display:flex;align-items:center;gap:8px'>"
            f"<span style='width:36px;font-weight:700;color:#1a4a8a'>{name}</span>"
            f"<span class='al-bar-wrap'><span class='al-bar' style='width:{pct}%'></span></span>"
            f"<span class='al-pct'>{pct}%</span></div>"
        )
    st.markdown(f"<div style='margin-bottom:14px'>{qt_bars}</div>", unsafe_allow_html=True)

    ic = u.get("interaction_codes", {})
    ic_total = max(sum(ic.values()), 1)
    ic_names = {"IG":"정보 모으기","B":"연결 짓기","EI":"더 알아보기","EA":"내 생각 더하기","R":"되돌아보기"}
    st.markdown("<div style='font-family:monospace;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#888480;margin-bottom:8px'>AI와 어떻게 대화하셨나요?</div>", unsafe_allow_html=True)
    ic_bars = ""
    for code, val in ic.items():
        pct = int(val / ic_total * 100)
        ic_bars += (
            f"<div style='padding:5px 0;font-size:12px;display:flex;align-items:center;gap:8px'>"
            f"<span style='width:36px;font-weight:700;color:#1a4a8a'>{code}</span>"
            f"<span style='width:80px;color:#888480'>{ic_names.get(code,'')}</span>"
            f"<span class='al-bar-wrap'><span class='al-bar' style='width:{pct}%'></span></span>"
            f"<span class='al-pct'>{pct}%</span></div>"
        )
    st.markdown(f"<div style='margin-bottom:14px'>{ic_bars}</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-family:monospace;font-size:10px;font-weight:700;letter-spacing:.08em;
                text-transform:uppercase;color:#888480;margin-bottom:6px'>확장된 구성주의 모델 분류</div>
    <div class='al-model-tag'>⬢ {u.get('dominant_model','')}</div>
    <div style='font-size:13px;line-height:1.8;color:#3a3835;
                background:#f0f4fb;border:1px solid #c5d8f0;
                padding:12px 16px;margin:8px 0;border-radius:4px'>
      📖 <strong>이 분류가 무엇인가요?</strong><br>{u.get('model_explanation','')}</div>
    <div style='font-size:12px;color:#888480;line-height:1.7;margin-bottom:10px'>{u.get('model_reason','')}</div>
    <div class='al-insight' style='border-color:#c8960c;background:#fdf6e3'>{u.get('analysis_text','')}</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── SECTION 4: 점수
    st.markdown("<div class='al-section-label'>Section 04</div>", unsafe_allow_html=True)
    st.markdown("<div class='al-section-title'>📈 AI 활용 능력 점수</div>", unsafe_allow_html=True)

    sc = s.get("value", 0)
    sc_col = score_color(sc)
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown(f"""
        <div class='al-card' style='text-align:center'>
          <div class='al-score-num' style='color:{sc_col}'>{sc}</div>
          <div style='font-family:monospace;font-size:10px;color:#888480'>/ 100</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='al-card'>
          <div class='al-level' style='color:{sc_col}'>{s.get('level','')}</div>
          <div style='font-size:13px;color:#3a3835;line-height:1.6'>{s.get('level_desc','')}</div>
        </div>""", unsafe_allow_html=True)

    improvements = "".join(
        f"<div class='al-improve-item'><span class='al-arrow'>→</span><span>{imp}</span></div>"
        for imp in s.get("improvements", [])
    )
    st.markdown(f"""
    <div style='font-family:monospace;font-size:10px;font-weight:700;letter-spacing:.08em;
                text-transform:uppercase;color:#888480;margin:14px 0 8px'>이렇게 바꿔보세요</div>
    {improvements}""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-family:monospace;font-size:10px;font-weight:700;letter-spacing:.08em;
                text-transform:uppercase;color:#888480;margin:14px 0 8px'>질문 예시 비교</div>
    <div class='al-prompt-before'>
      <div class='al-prompt-label' style='color:#c0392b'>지금 이렇게 쓰고 계세요</div>
      <div style='font-size:13px;font-style:italic;color:#3a3835'>"{s.get('before_prompt','')}"</div>
    </div>
    <div class='al-prompt-after'>
      <div class='al-prompt-label' style='color:#1a6b3a'>이렇게 바꾸면 훨씬 좋아요</div>
      <div style='font-size:13px;font-style:italic;color:#3a3835'>"{s.get('after_prompt','')}"</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── SECTION 5: 알면 좋을 것들
    st.markdown("<div class='al-section-label'>Section 05</div>", unsafe_allow_html=True)
    st.markdown("<div class='al-section-title'>💡 알면 AI를 훨씬 잘 쓸 수 있어요</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12px;color:#888480;margin-bottom:12px'>사용자님이 아직 잘 모르시는 것 같은 AI 활용 방법이에요.</div>", unsafe_allow_html=True)

    gap_html = ""
    for i, g in enumerate(gaps):
        gap_html += f"""
        <div class='al-literacy-item'>
          <span class='al-literacy-tag'>놓친 점 {i+1}</span>
          <span class='al-literacy-title'>{g.get('concept','')}</span>
          <div style='margin-top:8px;font-size:13px;line-height:1.8;color:#3a3835'>{g.get('explanation','')}</div>
          <div class='al-literacy-example'>📌 {g.get('example','')}</div>
        </div>"""
    st.markdown(gap_html, unsafe_allow_html=True)


# ════════════════════════════════════════
#  메인 레이아웃
# ════════════════════════════════════════
st.markdown("""
<div class='al-topbar'>
  <span class='al-topbar-brand'>AI·<span>LITERACY</span>·FEEDBACK</span>
  <span style='font-family:monospace;font-size:11px;color:rgba(255,255,255,.45)'>BETA v0.3 — 프롬프트 습관 분석기</span>
</div>""", unsafe_allow_html=True)

left, right = st.columns([1, 1.6], gap="large")

# ════════════════════════════════════════
#  LEFT: 입력 패널
# ════════════════════════════════════════
with left:

    # ── STEP 1: API 키
    st.markdown("**① Gemini API 키 입력**")
    api_key = st.text_input("API Key", type="password", placeholder="AIza...", label_visibility="collapsed")
    st.caption("[Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료 발급 (하루 1,500회 무료)")

    st.markdown("---")

    # ── STEP 2: 프롬프트 수집
    st.markdown("**② 프롬프트 수집**")
    tab_json, tab_pdf, tab_paste, tab_chat = st.tabs(["JSON 업로드", "PDF 업로드", "채팅 직접 붙여넣기", "챗봇 입력"])

    # ── JSON 탭
    with tab_json:
        json_file = st.file_uploader("ChatGPT conversations.json", type=["json"], key="json_upload")
        if json_file:
            try:
                prompts = parse_json(json_file.read())
                st.session_state.prompts = prompts
                st.success(f"✓ {len(prompts)}개 프롬프트 추출 완료")
            except Exception as e:
                st.error(f"파싱 실패: {e}")
        st.caption("설정 → 데이터 내보내기 → conversations.json")

    # ── PDF 탭
    with tab_pdf:
        pdf_files = st.file_uploader("PDF 파일 업로드", type=["pdf"], accept_multiple_files=True, key="pdf_upload")
        if pdf_files:
            all_lines = []
            for f in pdf_files:
                try:
                    lines = parse_pdf(f.read())
                    all_lines.extend(lines)
                    st.write(f"📄 {f.name}: {len(lines)}줄")
                except Exception as e:
                    st.warning(f"{f.name}: {e}")
            st.session_state.prompts = all_lines
            st.success(f"✓ 총 {len(all_lines)}개 텍스트 블록 추출 완료")
        st.caption("학습자 대화 내역 PDF. 여러 파일 동시 선택 가능.")

    # ── 붙여넣기 탭
    with tab_paste:
        paste_text = st.text_area(
            "대화 내용 붙여넣기",
            placeholder="Gemini, ChatGPT 등 AI 채팅 내용을 여기에 붙여넣으세요.\n\n(공유 링크 페이지에서 Ctrl+A → Ctrl+C 후 붙여넣기)",
            height=150,
            label_visibility="collapsed"
        )
        if st.button("블록 나누기 →", key="parse_paste"):
            if not paste_text.strip():
                st.warning("내용을 먼저 붙여넣어 주세요.")
            elif not api_key:
                st.warning("API 키를 먼저 입력해야 분류할 수 있어요.")
            else:
                raw_blocks = parse_paste(paste_text)
                if not raw_blocks:
                    st.warning("블록을 인식하지 못했어요. 내용을 확인해주세요.")
                else:
                    with st.spinner(f"Gemini가 {len(raw_blocks)}개 블록을 분석 중..."):
                        try:
                            classified = classify_blocks_with_gemini(raw_blocks, api_key)
                            st.session_state.paste_blocks = classified
                            user_count = sum(1 for b in classified if b["auto_checked"])
                            st.success(f"✓ 분류 완료 — 사용자 발화 {user_count}개 / AI 답변 {len(classified) - user_count}개 감지됨")
                        except Exception as e:
                            st.error(f"분류 실패: {e}")

        if st.session_state.paste_blocks:
            st.markdown(f"**{len(st.session_state.paste_blocks)}개 블록 — 잘못 분류된 항목은 직접 수정해주세요**")
            selected = []
            for i, block in enumerate(st.session_state.paste_blocks):
                preview = block["text"][:80] + ("…" if len(block["text"]) > 80 else "")
                role_badge = "🙋 사용자" if block.get("auto_checked") else "🤖 AI"
                label = f"{role_badge} | {preview}"
                checked = st.checkbox(label, value=block["auto_checked"], key=f"paste_cb_{i}")
                if checked:
                    selected.append(block["text"])

            if st.button("선택 완료", key="confirm_paste"):
                if selected:
                    st.session_state.prompts = selected
                    st.success(f"✅ {len(selected)}개 프롬프트 수집 완료")
                else:
                    st.warning("하나 이상 선택해주세요.")

    # ── 챗봇 탭
    with tab_chat:
        st.caption("AI에 대해 자유롭게 질문해보세요. 최소 5개 이상 대화 후 분석할 수 있어요.")

        chat_container = st.container(height=220)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("<div style='color:#888480;font-size:13px'>안녕하세요! AI에 대해 궁금한 것을 자유롭게 질문해보세요.</div>", unsafe_allow_html=True)
            for turn in st.session_state.chat_history:
                if turn["role"] == "user":
                    st.chat_message("user").write(turn["text"])
                else:
                    st.chat_message("assistant").write(turn["text"])

        chat_input = st.chat_input("질문을 입력하세요...", key="chat_input")
        if chat_input:
            if not api_key:
                st.warning("API 키를 먼저 입력해주세요.")
            else:
                st.session_state.prompts.append(chat_input)
                st.session_state.chat_history.append({"role": "user", "text": chat_input})
                try:
                    reply = chat_reply(api_key, st.session_state.chat_history[:-1], chat_input)
                    st.session_state.chat_history.append({"role": "model", "text": reply})
                except Exception as e:
                    st.session_state.chat_history.append({"role": "model", "text": f"오류: {e}"})
                st.rerun()

        st.caption(f"대화 {len(st.session_state.prompts)}개 수집됨")

    st.markdown("---")

    # ── STEP 3: 분석 버튼
    st.markdown("**③ 분석 시작**")
    collected = len(st.session_state.prompts)
    st.caption(f"현재 수집된 프롬프트: **{collected}개**")

    if st.button("🔍  프롬프트 습관 분석 시작", type="primary", use_container_width=True, disabled=(collected < 3)):
        if not api_key:
            st.error("API 키를 먼저 입력해주세요.")
        else:
            with st.spinner("분석 중... (30~60초 소요)"):
                try:
                    result = analyze(api_key, st.session_state.prompts)
                    st.session_state.report = result
                    st.success("✅ 분석 완료 — 오른쪽에서 보고서를 확인하세요")
                except json.JSONDecodeError as e:
                    st.error(f"JSON 파싱 실패: {e}\nAPI 응답이 올바른 형식이 아니에요.")
                except Exception as e:
                    st.error(f"분석 실패: {e}")

    if collected < 3:
        st.caption("⚠ 최소 3개 이상의 프롬프트가 필요합니다.")

    # 초기화 버튼
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.prompts = []
        st.session_state.chat_history = []
        st.session_state.report = None
        st.session_state.paste_blocks = []
        st.rerun()

# ════════════════════════════════════════
#  RIGHT: 보고서 패널
# ════════════════════════════════════════
with right:
    st.markdown("**보고서**")

    if st.session_state.report is None:
        st.markdown("""
        <div style='border:1px solid #e8e5e0; padding:80px 40px; text-align:center;
                    background:#f9f7f4; color:#888480; border-radius:4px;'>
          <div style='font-size:40px; margin-bottom:16px; opacity:.3'>📄</div>
          <div style='font-size:13px; line-height:1.7;'>
            프롬프트를 수집하고 분석 버튼을 누르면<br>
            AI 리터러시 피드백 보고서가 여기에 생성됩니다.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        render_report(st.session_state.report)
