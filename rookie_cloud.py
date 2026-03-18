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
MODEL_NAME = "qwen/qwen3-32b"

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
    "경제/증시": [
        "국내 증시 전망", "금리 환율 동향", "코스피 코스닥 시황",
        "주요 기업 실적", "한국은행 기준금리", "원달러 환율",
        "코스피 급등 급락", "기업 IPO 상장", "주식 투자 트렌드",
        "채권 금융시장", "무역수지 경상수지", "소비자물가 인플레이션",
        "기업 인수합병 M&A", "벤처 투자 VC", "외국인 기관 매매동향"
    ],
    "AI/미래기술": [
        "AI 기술 트렌드", "반도체 산업 전망", "LLM 인공지능 혁신",
        "엔비디아 빅테크 소식", "AI 스타트업", "챗GPT 클로드 최신",
        "자율주행 로봇 기술", "양자컴퓨터 기술", "AI 반도체 칩",
        "메타버스 XR 기술", "사이버보안 해킹", "핀테크 블록체인",
        "드론 UAM 기술", "바이오 AI 헬스케어", "스마트팩토리 자동화"
    ],
    "정치/외교": [
        "국회 법안 통과", "정부 정책 발표", "대통령실 동향",
        "한미 외교 관계", "여야 정치 쟁점", "선거 여론조사",
        "한중 한일 외교", "유엔 국제기구 동향", "국방 안보 정책",
        "북한 도발 동향", "장관 인사 내각", "검찰 사법 이슈",
        "지방자치 행정", "헌법재판소 판결", "외교부 조약 협정"
    ],
    "산업/부동산": [
        "부동산 시장 전망", "아파트 매매 시황", "건설 산업 동향",
        "공급망 이슈", "전세 월세 시장", "재건축 재개발",
        "제조업 수출 동향", "중소기업 스타트업 소식", "자동차 산업",
        "조선 철강 산업", "유통 물류 이커머스", "식품 농업 수산",
        "에너지 석유 가스", "호텔 관광 항공 산업", "바이오 제약 산업"
    ],
    "글로벌 뉴스": [
        "국제 정세", "미국 경제 동향", "글로벌 시장 이슈",
        "해외 주요 뉴스", "중국 경제 무역", "유럽 경제 위기",
        "중동 전쟁 분쟁", "G7 G20 정상회담", "러시아 우크라이나",
        "아세안 동남아 경제", "일본 엔화 경제", "인도 신흥국 성장",
        "세계은행 IMF 전망", "글로벌 공급망 재편", "미중 무역 갈등"
    ],
    "과학/환경": [
        "최신 과학 기술", "기후 변화 정책", "에너지 산업",
        "우주 항공 뉴스", "탄소중립 환경 규제", "신재생에너지 태양광",
        "노벨상 과학 연구", "바이오 헬스케어 기술", "핵융합 원자력",
        "해양 수질 오염", "생물 다양성 멸종", "전기차 배터리",
        "수소에너지 연료전지", "나사 스페이스X 우주탐사", "기상 이상기후"
    ],
    "사회/이슈": [
        "사회적 주요 현안", "오늘의 이슈", "인구 및 통계 조사",
        "교육 정책 입시", "저출생 고령화", "범죄 사건 사고",
        "노동 임금 근로", "복지 의료 정책", "젠더 다양성 이슈",
        "청년 취업 실업", "주거 빈곤 격차", "언론 미디어 이슈",
        "종교 갈등 사회", "이민 다문화 정책", "재난 안전 사고"
    ],
    "문화/라이프": [
        "문화 트렌드", "라이프스타일", "소비 동향",
        "예술 전시 소식", "한류 K팝 드라마", "스포츠 경기 결과",
        "음식 여행 관광", "패션 뷰티 트렌드", "영화 OTT 콘텐츠",
        "게임 e스포츠", "웹툰 출판 문학", "건강 운동 피트니스",
        "반려동물 펫 시장", "명품 럭셔리 소비", "힐링 웰니스 트렌드"
    ],
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
            messages=[
                {
                    "role": "system",
                    "content": "당신은 한국어 AI 비서 루키입니다. 반드시 한국어로만 답변하세요. 중국어, 일본어, 영어 등 다른 언어는 절대 사용하지 마세요."
                },
                {"role": "user", "content": prompt}
            ],
            stream=True,
            max_tokens=2048,
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
            import os
            video_path = os.path.join(os.path.dirname(__file__), "Video Project.mp4")
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            import base64
            import streamlit.components.v1 as components
            video_path = os.path.join(os.path.dirname(__file__), "Video Project.mp4")
            with open(video_path, "rb") as f:
                video_b64 = base64.b64encode(f.read()).decode()
            components.html(f"""
<video width="100%" autoplay  playsinline loop>
    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
</video>
""", height=400)

        # ── 영상 끝날 때까지 대기 (영상 길이에 맞게 초 조정) ──
        import time
        time.sleep(7)  # ← 영상 길이(초)로 바꿔주세요

        # ── 뉴스 수집 ──
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
prompt = f"""아래 뉴스 기사를 분석하여 반드시 한국어로만 작성하세요.

[기사 정보]
제목: {item['title']}
내용: {item['summary']}

[작성 형식]
핵심 요약: 이 기사의 핵심을 2~3문장으로 간결하게 요약

심층 분석
- 발생 배경: 이 사건/이슈가 왜 발생했는지
- 전개 과정: 현재까지 어떻게 진행됐는지
- 향후 전망: 앞으로 어떻게 될 것으로 예상되는지

루키의 단어 사전
- 용어1: 쉬운 설명
- 용어2: 쉬운 설명

주의사항: 반드시 한국어로만 작성, 중국어 일본어 영어 절대 사용 금지, 대표님께 조언 금지"""
                

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
