"""
루키 비서실 — 클라우드 버전 (Groq API)
배포: Streamlit Community Cloud
"""
import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq
import json

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(page_title="루키 비서실", layout="wide", page_icon="🐾")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500&display=swap');

/* ── 전체 배경 ── */
html, body, [data-testid="stApp"] {
    background-color: #121c30;
    font-family: 'Noto Sans KR', sans-serif;
}

/* ── 배경 패턴 (발바닥 느낌 dot) ── */
[data-testid="stApp"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(245,180,90,0.06) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
    z-index: 0;
}

/* ── 메인 타이틀 ── */
h1 {
    font-family: 'Noto Serif KR', serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #f5c842, #f5a623);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1928 0%, #162035 100%) !important;
    border-right: 1px solid rgba(245,166,35,0.2) !important;
}
[data-testid="stSidebar"] * { color: #e8dfc8 !important; }
[data-testid="stSidebar"] h1 {
    font-family: 'Noto Serif KR', serif !important;
    font-size: 1.2rem !important;
    color: #f5c842 !important;
    -webkit-text-fill-color: #f5c842 !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: #f5a623 !important;
}

/* ── 채팅 말풍선 ── */
div[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, #1c2d4a 0%, #1a2840 100%) !important;
    border-radius: 18px !important;
    border: 1px solid rgba(245,166,35,0.15) !important;
    margin-bottom: 12px !important;
    padding: 4px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}

/* ── 버튼 (카테고리) ── */
.stButton > button {
    background: linear-gradient(135deg, #1c2d4a, #243455) !important;
    color: #e8dfc8 !important;
    border: 1px solid rgba(245,166,35,0.35) !important;
    border-radius: 50px !important;
    height: 3.2em !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #f5a623, #f5c842) !important;
    color: #121c30 !important;
    border-color: transparent !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(245,166,35,0.3) !important;
}

/* ── 리포트 카드 제목 ── */
.report-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f5c842;
    margin-top: 20px;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(245,166,35,0.25);
}

/* ── 리포트 본문 ── */
.report-content {
    line-height: 2.0;
    font-size: 1.0rem;
    color: #d4c9b0;
    margin-bottom: 20px;
    font-family: 'Noto Sans KR', sans-serif;
}

/* ── 공지 박스 ── */
.notice-box {
    background: linear-gradient(135deg, rgba(245,166,35,0.08), rgba(245,166,35,0.03));
    border: 1px solid rgba(245,166,35,0.25);
    border-left: 3px solid #f5a623;
    border-radius: 12px;
    padding: 16px 18px;
    font-size: 0.82rem;
    line-height: 1.9;
    color: #b8a98a;
    margin: 12px 0;
}
.notice-box a { color: #f5c842 !important; text-decoration: none; }
.notice-box a:hover { text-decoration: underline; }
.notice-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #f5a623;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── 채팅 입력창 ── */
[data-testid="stChatInput"] textarea {
    background: #1c2d4a !important;
    color: #e8dfc8 !important;
    border-radius: 50px !important;
}
[data-testid="stChatInput"] > div {
    border: 1px solid rgba(245,166,35,0.3) !important;
    border-radius: 50px !important;
    background: #1c2d4a !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #f5a623 !important;
    box-shadow: 0 0 0 2px rgba(245,166,35,0.15) !important;
}

/* ── 텍스트 입력 ── */
.stTextInput > div > div > input {
    background: #1c2d4a !important;
    border: 1px solid rgba(245,166,35,0.25) !important;
    border-radius: 10px !important;
    color: #e8dfc8 !important;
}

/* ── 구분선 ── */
hr { border-color: rgba(245,166,35,0.15) !important; }

/* ── 경고/에러 ── */
.stAlert { border-radius: 12px !important; }

/* ── 일반 텍스트 ── */
p, li, span, label { color: #c8bfa8 !important; }
</style>
""", unsafe_allow_html=True)

ROOKIE_IMG = "image_2fc863.jpg"
MODEL_NAME = "llama-3.3-70b-versatile"

# ── Groq 클라이언트 ───────────────────────────────────────────
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ GROQ_API_KEY가 설정되지 않았습니다.")
    st.stop()

# ── 세션 초기화 ───────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "news_context" not in st.session_state: st.session_state.news_context = ""
if "vocab_dict"   not in st.session_state: st.session_state.vocab_dict   = {}

# ── 키워드 ────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "경제/증시":   ["국내 증시 전망", "금리 환율 동향", "코스피 코스닥 시황", "주요 기업 실적"],
    "AI/미래기술": ["AI 기술 트렌드", "반도체 산업 전망", "LLM 인공지능 혁신", "엔비디아 빅테크 소식"],
    "정치/외교":   ["국회 법안 통과", "정부 정책 발표", "대통령실 동향", "한미 외교 관계"],
    "산업/부동산": ["부동산 시장 전망", "아파트 매매 시황", "건설 산업 동향", "공급망 이슈"],
    "글로벌 뉴스": ["국제 정세", "미국 경제 동향", "글로벌 시장 이슈", "해외 주요 뉴스"],
    "과학/환경":   ["최신 과학 기술", "기후 변화 정책", "에너지 산업", "우주 항공 뉴스"],
    "사회/이슈":   ["사회적 주요 현안", "오늘의 이슈", "인구 및 통계 조사"],
    "문화/라이프": ["문화 트렌드", "라이프스타일", "소비 동향", "예술 전시 소식"],
}

@st.cache_data(ttl=600)
def fetch_news(category: str, count: int, days: int) -> list:
    queries, results = CATEGORY_KEYWORDS.get(category, [category]), []
    try:
        with DDGS() as ddgs:
            for q in queries:
                for r in ddgs.news(q, region="kr-kr", safesearch="off", timelimit=f"d{days}"):
                    results.append({
                        "source": r.get("source",""), "title": r.get("title",""),
                        "link": r.get("url",""), "summary": r.get("body",""),
                        "date": r.get("date","최근"), "image": r.get("image"),
                    })
                    if len(results) >= 20: break
                if len(results) >= 20: break
    except Exception as e:
        st.error(f"🔴 검색 오류: {e}"); return []
    return list({r["title"]: r for r in results}.values())[:count]

def stream_groq(prompt: str) -> str:
    def _gen():
        stream = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=True, max_tokens=2048,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta: yield delta
    return st.write_stream(_gen())

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    try: st.image(ROOKIE_IMG, use_container_width=True)
    except: pass

    st.markdown("<h1>🐾 루키 비서실</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📅 검색 기간**")
    days_range = st.slider("", 1, 14, 7, label_visibility="collapsed")
    st.caption(f"최근 **{days_range}일** 뉴스를 검색합니다.")
    st.markdown("---")

    st.markdown("**📒 지식 저장소**")
    if st.session_state.vocab_dict:
        for word, defn in list(st.session_state.vocab_dict.items()):
            with st.expander(f"💎 {word}"):
                new_defn = st.text_area("수정", value=defn, key=f"e_{word}")
                if new_defn != defn:
                    st.session_state.vocab_dict[word] = new_defn
                if st.button("🗑️ 삭제", key=f"d_{word}"):
                    del st.session_state.vocab_dict[word]; st.rerun()
    else:
        st.caption("저장된 단어가 없습니다.")

    st.markdown("---")

    # ── 공지사항 ──
    st.markdown("""
<div class='notice-box'>
<div class='notice-title'>🐶 서비스 안내</div>
<div style='font-size:0.82rem; line-height:1.8; color:#aaaaaa; padding: 8px 0;'>
ⓐ 현재 이 AI Rookie는 우리가 개발중인 모델의 일부를 떼어낸 것에 불과하며, 완전히 구현되지 않았으므로 오류가 많습니다.<br><br>
ⓑ 현재 구현되지 않는 기능은 지식저장소, 1:1 채팅 기능의 부자연스러움, 단어저장이 대표적입니다.<br><br>
ⓒ 현재 사용자께서 보시는 환경은 <b>'신문 및 시사 뉴스 스크랩 기능'</b> 용도로 만들어진 것입니다.<br><br>
ⓓ 개발 시작일이 3월 초순인 만큼, 실시간으로 업데이트가 되고 있다는 점을 양해 바랍니다.<br><br>
ⓔ 현재 1:1 대화 및 신문 및 스크랩 생성에 다수의 사용자가 사용 시 생성 제한 및 오류가 발생할 수 있습니다.<br><br>
ⓕ 현재 클라우드 서버를 이용중이므로 배포에 불완전성이 우려됩니다.<br><br>
ⓖ PC 환경 사용을 권장합니다.<br><br>
※ 이 외 오류 및 개선사항이 있다면<br>
<a href='mailto:compway@yu.ac.kr' style='color:#89b4fa;'>compway@yu.ac.kr</a> 로 메일 전송해 주시면 적극 반영토록 하겠습니다.<br><br>
— 개발자 —<br>
성무진, 강연화, 박현수 드림<br>
<span style='color:#666;'>1차 업데이트: 2026/03/17 오후 10:40</span><br><br>
<span style='color:#666;'>2차 업데이트(디자인 및 UI수정): 2026/03/17 오후 11:25</span><br><br>
※ 오른쪽 위 <b>Dark모드</b> 사용을 권장합니다.
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 대화 초기화"):
        st.session_state.update(messages=[], vocab_dict={}, news_context=""); st.rerun()

# ── 메인 ──────────────────────────────────────────────────────
st.markdown("# 🐾 Rookie — 팀 비서실")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=ROOKIE_IMG if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        st.markdown(f"안녕하십니까! **최근 {days_range}일**간의 뉴스를 분석해 드리겠습니다. 아래에서 분야를 선택해 주세요 🐾")
        count = st.select_slider("조사할 기사 개수", options=[1,2,3,4,5], value=3)
        cats = list(CATEGORY_KEYWORDS.keys())
        for row in [cats[i:i+4] for i in range(0, len(cats), 4)]:
            for col, cat in zip(st.columns(4), row):
                if col.button(cat):
                    st.session_state.update(selected_category=cat, selected_count=count)
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"[{cat}] 최근 {days_range}일 뉴스 {count}개 스크랩해 줘."
                    })
                    st.rerun()

if "selected_category" in st.session_state:
    cat, cnt = st.session_state.pop("selected_category"), st.session_state.pop("selected_count")
    with st.chat_message("assistant", avatar=ROOKIE_IMG):

# ── 로딩 영상 표시 ──
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown("""
<div style='text-align:center; padding: 20px 0;'>
    <div style='font-family:Noto Serif KR, serif; font-size:1.4rem;
                color:#f5c842; font-weight:700; margin-bottom:12px;'>
        🐾 루키가 정리중이에요...
    </div>
    <div style='font-size:0.9rem; color:#b8a98a;'>
        잠시만 기다려 주십시오
    </div>
</div>
""", unsafe_allow_html=True)
            with open("Video Project.mp4", "rb") as f:
                video_bytes = f.read()
            st.video(video_bytes)

        # ── 뉴스 수집 (영상 띄워둔 채로 실행) ──
        news_data = fetch_news(cat, cnt, days_range)

        # ── 로딩 영상 제거 ──
        loading_placeholder.empty()
        if not news_data:
            st.warning("검색 결과가 없습니다. 다른 분야를 선택해 주세요.")
        else:
            parts = []
            for i, item in enumerate(news_data):
                st.markdown(f"<div class='report-title'>📌 {i+1}. {item['title']}</div>", unsafe_allow_html=True)
                if item["image"]: st.image(item["image"], width=700)
                prompt = f"""수석 비서 루키로서 보고서를 작성하세요.
제목: {item['title']}
내용: {item['summary']}
1. [심층 보고]: 발생 배경, 전개 과정, 향후 전망을 유려한 문장으로 상세히 기술하세요.
2. [루키의 단어 사전]: 어려운 용어 2개를 쉽게 풀이해 주세요.
※ 반드시 한국어로 작성하세요."""
                try:
                    analysis = stream_groq(prompt)
                except Exception as e:
                    analysis = f"⚠️ 오류: {e}"; st.error(analysis)

                c1, c2, c3 = st.columns([2, 2, 1])
                w = c1.text_input("단어", key=f"w_{i}")
                d = c2.text_input("정의", key=f"d_{i}")
                if c3.button("💾 저장", key=f"b_{i}") and w:
                    st.session_state.vocab_dict[w] = d
                    st.toast(f"✅ '{w}' 저장 완료!")

                st.markdown(f"🔗 [기사 원문]({item['link']}) | {item['source']} | {item['date']}")
                st.markdown("---")
                st.session_state.news_context += f"\n{analysis}"
                parts.append(f"**{i+1}. {item['title']}**\n{analysis}")
            st.session_state.messages.append({"role": "assistant", "content": "\n\n".join(parts)})

if user_input := st.chat_input("💬 궁금한 점을 물어보세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        try:
            res = stream_groq(f"""수석 비서 루키입니다. 문맥을 바탕으로 답변해 주세요.
[스크랩 문맥]\n{st.session_state.news_context or '아직 스크랩된 내용이 없습니다.'}
[질문]\n{user_input}
※ 반드시 한국어로 답변하세요.""")
            st.session_state.messages.append({"role": "assistant", "content": res})
        except Exception as e:
            st.error(f"⚠️ 오류: {e}")
