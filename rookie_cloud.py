"""
루키 비서실 — 클라우드 버전 (Groq API)
배포: Streamlit Community Cloud (https://share.streamlit.io)
Groq API 키: https://console.groq.com  →  st.secrets["GROQ_API_KEY"]
"""
import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq
import json

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(page_title="루키 비서실 (팀용)", layout="wide", page_icon="👔")
st.markdown("""
<style>
div[data-testid="stChatMessage"] { background-color: #1e1e2e; border-radius: 14px; margin-bottom: 10px; }
.report-title { font-size:1.4rem; font-weight:bold; color:#89b4fa; margin-top:15px; }
.report-content { line-height:1.9; font-size:1.05rem; color:#cdd6f4; margin-bottom:25px; }
.stButton>button { border-radius:10px; height:3.2em; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

ROOKIE_IMG = "image_2fc863.jpg"
MODEL_NAME = "llama-3.3-70b-versatile"  # Groq 무료 최고 성능 모델

# ── Groq 클라이언트 ───────────────────────────────────────────
# Streamlit Cloud: Settings → Secrets 에 GROQ_API_KEY 등록
# 로컬 테스트: .streamlit/secrets.toml 에 GROQ_API_KEY = "gsk_..." 추가
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ GROQ_API_KEY가 설정되지 않았습니다. Streamlit Secrets를 확인하세요.")
    st.stop()

# ── 세션 초기화 (클라우드: 사용자별 세션, JSON 저장 없음) ─────
# 클라우드는 서버가 재시작되면 파일이 사라지므로 세션 기반으로만 관리
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
                    results.append({"source": r.get("source",""), "title": r.get("title",""),
                                    "link": r.get("url",""), "summary": r.get("body",""),
                                    "date": r.get("date","최근"), "image": r.get("image")})
                    if len(results) >= 20: break
                if len(results) >= 20: break
    except Exception as e:
        st.error(f"🔴 검색 오류: {e}"); return []
    return list({r["title"]: r for r in results}.values())[:count]

def stream_groq(prompt: str) -> str:
    """Groq 스트리밍 출력 — 토큰이 실시간으로 화면에 출력됨"""
    def _gen():
        stream = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=2048,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    return st.write_stream(_gen())

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    try: st.image(ROOKIE_IMG, use_container_width=True)
    except: pass
    st.title("👔 루키 비서실 (팀용)")
    st.caption(f"🤖 모델: `{MODEL_NAME}` (Groq)")
    st.write("---")
    days_range = st.slider("검색 기간 (일)", 1, 14, 7)
    st.write("---")
    st.subheader("📒 지식 저장소")
    st.caption("ℹ️ 팀용은 세션 기반 저장 (탭 닫으면 초기화)")
    if st.session_state.vocab_dict:
        for word, defn in list(st.session_state.vocab_dict.items()):
            with st.expander(f"💎 {word}"):
                new_defn = st.text_area("수정", value=defn, key=f"e_{word}")
                if new_defn != defn:
                    st.session_state.vocab_dict[word] = new_defn
                if st.button("🗑️ 삭제", key=f"d_{word}"):
                    del st.session_state.vocab_dict[word]; st.rerun()
    else:
        st.caption("저장된 단어 없음")
    st.write("---")
    if st.button("🔄 초기화"):
        st.session_state.update(messages=[], vocab_dict={}, news_context=""); st.rerun()

# ── 메인 ──────────────────────────────────────────────────────
st.title("👔 Rookie — 팀 비서실")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=ROOKIE_IMG if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        st.markdown(f"안녕하십니까. **최근 {days_range}일** 뉴스를 분석해 드리겠습니다.")
        count = st.select_slider("기사 개수", options=[1,2,3,4,5], value=3)
        cats = list(CATEGORY_KEYWORDS.keys())
        for row in [cats[i:i+4] for i in range(0,len(cats),4)]:
            for idx, cat in zip(st.columns(4), row):
                if idx.button(cat):
                    st.session_state.update(selected_category=cat, selected_count=count)
                    st.session_state.messages.append({"role":"user","content":f"[{cat}] 최근 {days_range}일 뉴스 {count}개 스크랩."})
                    st.rerun()

if "selected_category" in st.session_state:
    cat, cnt = st.session_state.pop("selected_category"), st.session_state.pop("selected_count")
    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        st.write(f"🔍 **[{cat}]** 검색 중...")
        news_data = fetch_news(cat, cnt, days_range)
        if not news_data:
            st.warning("검색 결과 없음")
        else:
            parts = []
            for i, item in enumerate(news_data):
                st.markdown(f"<div class='report-title'>📌 {i+1}. {item['title']}</div>", unsafe_allow_html=True)
                if item["image"]: st.image(item["image"], width=700)
                prompt = f"""수석 비서 루키로서 보고서를 작성하세요.
제목: {item['title']}
내용: {item['summary']}
1. [심층 보고]: 배경, 전개, 전망을 유려하게 기술
2. [루키의 단어 사전]: 어려운 용어 2개 쉽게 풀이
※ 반드시 한국어로 작성"""
                try:
                    analysis = stream_groq(prompt)
                except Exception as e:
                    analysis = f"⚠️ 오류: {e}"; st.error(analysis)

                c1,c2,c3 = st.columns([2,2,1])
                w = c1.text_input("단어", key=f"w_{i}")
                d = c2.text_input("정의", key=f"d_{i}")
                if c3.button("💾 저장", key=f"b_{i}") and w:
                    st.session_state.vocab_dict[w] = d
                    st.toast(f"✅ '{w}' 저장!")

                st.markdown(f"🔗 [원문]({item['link']}) | {item['source']} | {item['date']}")
                st.markdown("---")
                st.session_state.news_context += f"\n{analysis}"
                parts.append(f"**{i+1}. {item['title']}**\n{analysis}")
            st.session_state.messages.append({"role":"assistant","content":"\n\n".join(parts)})

if user_input := st.chat_input("궁금한 점을 물어보세요"):
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        try:
            res = stream_groq(f"""수석 비서 루키입니다. 문맥을 바탕으로 답하세요.
[문맥]\n{st.session_state.news_context or '스크랩 없음'}
[질문]\n{user_input}
※ 반드시 한국어로""")
            st.session_state.messages.append({"role":"assistant","content":res})
        except Exception as e:
            st.error(f"⚠️ 오류: {e}")
