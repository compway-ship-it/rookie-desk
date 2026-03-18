"""루키 비서실 — 클라우드 버전 (Groq API)"""
import streamlit as st
import streamlit.components.v1 as components
from duckduckgo_search import DDGS
from groq import Groq
import os, base64, time

st.set_page_config(page_title="루키 비서실", layout="wide", page_icon="🐾")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

:root {
  --bg: #09090f;
  --bg2: #0f0f1a;
  --bg3: #141423;
  --gold: #c9a84c;
  --gold2: #e8c76a;
  --gold-dim: rgba(201,168,76,0.12);
  --gold-border: rgba(201,168,76,0.22);
  --text: #f0ece2;
  --text2: #9a9180;
  --text3: #5c5648;
  --glass: rgba(255,255,255,0.03);
  --glass-border: rgba(255,255,255,0.07);
}

html, body, [data-testid="stApp"] {
  background-color: var(--bg) !important;
  font-family: 'Noto Sans KR', sans-serif;
  color: var(--text);
}

/* 배경 그리드 텍스처 */
[data-testid="stApp"]::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(201,168,76,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(201,168,76,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--gold-border) !important;
}
[data-testid="stSidebar"] * { color: var(--text2) !important; }
[data-testid="stSidebar"] h1 {
  font-family: 'Playfair Display', serif !important;
  font-size: 1.15rem !important;
  color: var(--gold) !important;
  -webkit-text-fill-color: var(--gold) !important;
  letter-spacing: 0.5px !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
  color: var(--text) !important;
  font-weight: 500;
}

/* ── 탭 ── */
[data-testid="stTabs"] [role="tablist"] {
  background: transparent !important;
  border-bottom: 1px solid var(--glass-border) !important;
  padding-bottom: 0 !important;
  gap: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
  background: transparent !important;
  color: var(--text3) !important;
  border-radius: 0 !important;
  font-family: 'Noto Sans KR', sans-serif !important;
  font-weight: 400 !important;
  font-size: 0.9rem !important;
  padding: 10px 22px !important;
  border-bottom: 2px solid transparent !important;
  transition: all 0.2s !important;
  letter-spacing: 0.3px !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  background: transparent !important;
  color: var(--gold2) !important;
  border-bottom: 2px solid var(--gold) !important;
  font-weight: 500 !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
  color: var(--text) !important;
  background: var(--glass) !important;
}

/* ── 채팅 버블 ── */
div[data-testid="stChatMessage"] {
  background: var(--glass) !important;
  border-radius: 16px !important;
  border: 1px solid var(--glass-border) !important;
  margin-bottom: 10px !important;
  padding: 4px !important;
  backdrop-filter: blur(10px);
}

/* ── 버튼 ── */
.stButton > button {
  background: transparent !important;
  color: var(--text2) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 8px !important;
  height: 3em !important;
  font-size: 0.88rem !important;
  font-weight: 400 !important;
  transition: all 0.2s !important;
  letter-spacing: 0.2px !important;
}
.stButton > button:hover {
  background: var(--gold-dim) !important;
  color: var(--gold2) !important;
  border-color: var(--gold-border) !important;
  transform: translateY(-1px) !important;
}

/* ── 리포트 제목 ── */
.report-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--gold2);
  margin-top: 24px;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--gold-border);
  letter-spacing: -0.3px;
}

/* ── 개발노트 ── */
.notice-box {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-left: 3px solid var(--gold);
  border-radius: 12px;
  padding: 24px 28px;
  font-size: 0.87rem;
  line-height: 2.1;
  color: var(--text2);
  margin: 20px 0;
}
.notice-box a { color: var(--gold2) !important; text-decoration: none; }
.notice-title {
  font-family: 'Playfair Display', serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--gold-border);
  letter-spacing: 0.3px;
}

/* ── 채팅 입력 ── */
[data-testid="stChatInput"] textarea { background: var(--bg3) !important; color: var(--text) !important; }
[data-testid="stChatInput"] > div {
  border: 1px solid var(--glass-border) !important;
  border-radius: 12px !important;
  background: var(--bg3) !important;
  transition: border-color 0.2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 0 3px rgba(201,168,76,0.08) !important;
}

/* ── 텍스트 입력 ── */
.stTextInput > div > div > input {
  background: var(--bg3) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
}

/* ── 슬라이더 ── */
[data-testid="stSlider"] {
  background: var(--glass) !important;
  border-radius: 10px !important;
  padding: 14px 18px !important;
  border: 1px solid var(--glass-border) !important;
}
[data-testid="stSlider"] > div > div > div > div {
  background: linear-gradient(90deg, var(--gold), var(--gold2)) !important;
}
[data-testid="stSlider"] > div > div > div > div > div {
  background: var(--gold2) !important;
  border: 2px solid var(--bg) !important;
  box-shadow: 0 0 10px rgba(201,168,76,0.5) !important;
}

/* ── 라디오 ── */
[data-testid="stRadio"] > div { gap: 8px !important; }
[data-testid="stRadio"] label {
  background: var(--glass) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  font-size: 0.88rem !important;
  color: var(--text2) !important;
}
[data-testid="stRadio"] label:has(input:checked) {
  border-color: var(--gold-border) !important;
  background: var(--gold-dim) !important;
  color: var(--gold2) !important;
}

hr { border-color: var(--glass-border) !important; }
.stAlert { border-radius: 10px !important; }
p, li, label { color: var(--text2) !important; }
.stCaption { color: var(--text3) !important; font-size: 0.8rem !important; }

/* ══ 소개 페이지 ══════════════════════════════════════════ */
.hero-wrap {
  text-align: center;
  padding: 80px 0 56px;
  position: relative;
}
.hero-eyebrow {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--gold);
  background: var(--gold-dim);
  border: 1px solid var(--gold-border);
  border-radius: 100px;
  padding: 5px 18px;
  margin-bottom: 28px;
}
.hero-headline {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 900;
  line-height: 1.2;
  color: var(--text);
  margin-bottom: 20px;
  letter-spacing: -1px;
}
.hero-headline span {
  background: linear-gradient(135deg, var(--gold2) 0%, #f5e6a3 50%, var(--gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-body {
  font-size: 1.05rem;
  color: var(--text2);
  line-height: 1.9;
  max-width: 520px;
  margin: 0 auto 64px;
  font-weight: 300;
}
.agent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 0 0 64px;
}
.a-card {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 36px 28px 32px;
  text-align: left;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s, transform 0.3s;
}
.a-card:hover {
  border-color: var(--gold-border);
  transform: translateY(-4px);
}
.a-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  opacity: 0.6;
}
.a-icon {
  font-size: 2.4rem;
  margin-bottom: 20px;
  display: block;
  filter: grayscale(20%);
}
.a-pill {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  padding: 3px 12px;
  border-radius: 100px;
  margin-bottom: 18px;
}
.a-pill.beta { background: rgba(201,168,76,0.12); color: var(--gold); border: 1px solid rgba(201,168,76,0.3); }
.a-pill.soon { background: rgba(92,196,122,0.1); color: #5cc47a; border: 1px solid rgba(92,196,122,0.25); }
.a-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 10px;
  letter-spacing: -0.3px;
}
.a-tagline {
  font-size: 0.82rem;
  color: var(--gold);
  font-weight: 500;
  letter-spacing: 0.3px;
  margin-bottom: 16px;
}
.a-desc {
  font-size: 0.88rem;
  color: var(--text2);
  line-height: 1.8;
  margin-bottom: 24px;
  font-weight: 300;
}
.a-feature {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 0.84rem;
  color: var(--text2);
  line-height: 1.6;
}
.a-feature::before {
  content: "—";
  color: var(--gold);
  flex-shrink: 0;
  font-weight: 300;
  margin-top: 1px;
}
.divider-gold {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--gold-border) 30%, var(--gold-border) 70%, transparent 100%);
  margin: 56px 0;
}
.cta-section {
  text-align: center;
  padding: 56px 40px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}
.cta-section::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.cta-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 14px;
  letter-spacing: -0.5px;
}
.cta-sub {
  font-size: 0.92rem;
  color: var(--text2);
  line-height: 1.8;
  margin-bottom: 8px;
}
.stat-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 48px 0;
}
.stat-card {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 24px 20px;
  text-align: center;
}
.stat-num {
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, var(--gold2), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
  letter-spacing: -1px;
}
.stat-label {
  font-size: 0.8rem;
  color: var(--text3);
  font-weight: 400;
  letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

ROOKIE_IMG = "image_2fc863.jpg"
MODEL_NAME = "qwen/qwen3-32b"

try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY가 설정되지 않았습니다.")
    st.stop()

if "messages"     not in st.session_state: st.session_state.messages     = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "news_context" not in st.session_state: st.session_state.news_context = ""
if "vocab_dict"   not in st.session_state: st.session_state.vocab_dict   = {}

CATEGORY_KEYWORDS = {
    "경제/증시":   ["국내 증시 전망","금리 환율 동향","코스피 코스닥 시황","주요 기업 실적","한국은행 기준금리","원달러 환율","코스피 급등 급락","기업 IPO 상장","주식 투자 트렌드","채권 금융시장","무역수지 경상수지","소비자물가 인플레이션","기업 인수합병 M&A","벤처 투자 VC","외국인 기관 매매동향"],
    "AI/미래기술": ["AI 기술 트렌드","반도체 산업 전망","LLM 인공지능 혁신","엔비디아 빅테크 소식","AI 스타트업","챗GPT 클로드 최신","자율주행 로봇 기술","양자컴퓨터 기술","AI 반도체 칩","메타버스 XR 기술","사이버보안 해킹","핀테크 블록체인","드론 UAM 기술","바이오 AI 헬스케어","스마트팩토리 자동화"],
    "정치/외교":   ["국회 법안 통과","정부 정책 발표","대통령실 동향","한미 외교 관계","여야 정치 쟁점","선거 여론조사","한중 한일 외교","유엔 국제기구 동향","국방 안보 정책","북한 도발 동향","장관 인사 내각","검찰 사법 이슈","지방자치 행정","헌법재판소 판결","외교부 조약 협정"],
    "산업/부동산": ["부동산 시장 전망","아파트 매매 시황","건설 산업 동향","공급망 이슈","전세 월세 시장","재건축 재개발","제조업 수출 동향","중소기업 스타트업 소식","자동차 산업","조선 철강 산업","유통 물류 이커머스","식품 농업 수산","에너지 석유 가스","호텔 관광 항공 산업","바이오 제약 산업"],
    "글로벌 뉴스": ["국제 정세","미국 경제 동향","글로벌 시장 이슈","해외 주요 뉴스","중국 경제 무역","유럽 경제 위기","중동 전쟁 분쟁","G7 G20 정상회담","러시아 우크라이나","아세안 동남아 경제","일본 엔화 경제","인도 신흥국 성장","세계은행 IMF 전망","글로벌 공급망 재편","미중 무역 갈등"],
    "과학/환경":   ["최신 과학 기술","기후 변화 정책","에너지 산업","우주 항공 뉴스","탄소중립 환경 규제","신재생에너지 태양광","노벨상 과학 연구","바이오 헬스케어 기술","핵융합 원자력","해양 수질 오염","생물 다양성 멸종","전기차 배터리","수소에너지 연료전지","나사 스페이스X 우주탐사","기상 이상기후"],
    "사회/이슈":   ["사회적 주요 현안","오늘의 이슈","인구 및 통계 조사","교육 정책 입시","저출생 고령화","범죄 사건 사고","노동 임금 근로","복지 의료 정책","젠더 다양성 이슈","청년 취업 실업","주거 빈곤 격차","언론 미디어 이슈","종교 갈등 사회","이민 다문화 정책","재난 안전 사고"],
    "문화/라이프": ["문화 트렌드","라이프스타일","소비 동향","예술 전시 소식","한류 K팝 드라마","스포츠 경기 결과","음식 여행 관광","패션 뷰티 트렌드","영화 OTT 콘텐츠","게임 e스포츠","웹툰 출판 문학","건강 운동 피트니스","반려동물 펫 시장","명품 럭셔리 소비","힐링 웰니스 트렌드"],
}

CATEGORY_KEYWORDS_EN = {
    "경제/증시":   ["stock market outlook","interest rate currency trend","US market stocks","corporate earnings results","Fed rate decision","inflation CPI data","S&P500 nasdaq dow","IPO listing stock","investment trend 2026","trade balance deficit","M&A acquisition deal","venture capital funding","foreign investor flows","bond market yield","GDP economic growth"],
    "AI/미래기술": ["AI technology trend 2026","semiconductor industry outlook","LLM large language model","Nvidia big tech news","AI startup funding","ChatGPT Claude Gemini latest","autonomous vehicle robotics news","quantum computing breakthrough","AI chip hardware","metaverse XR technology","cybersecurity hacking news","fintech blockchain crypto","drone UAM aviation","biotech AI healthcare","smart factory automation"],
    "정치/외교":   ["US legislation bill congress","government policy announcement","White House news","US Korea Japan diplomacy","political conflict election","election poll survey results","US China Japan relations","UN international organization","defense security policy","North Korea provocation news","cabinet reshuffle minister","justice court ruling","local government policy","supreme court decision","international treaty agreement"],
    "산업/부동산": ["real estate market outlook","housing market trend 2026","construction industry news","supply chain disruption","rental housing market","urban redevelopment renewal","manufacturing export trend","SME startup news funding","automobile EV industry","steel shipbuilding industry","logistics e-commerce news","food agriculture commodity","energy oil gas price","hotel tourism aviation industry","biotech pharma industry news"],
    "글로벌 뉴스": ["international affairs news","US economy latest news","global market issue today","world news breaking","China economy trade war","Europe economic crisis","Middle East conflict war","G7 G20 summit meeting","Russia Ukraine war update","ASEAN Southeast Asia economy","Japan yen economy news","India emerging market growth","World Bank IMF forecast","global supply chain reshaping","US China trade tariff"],
    "과학/환경":   ["science technology breakthrough","climate change policy COP","energy industry transition","space aerospace NASA news","carbon neutral green deal","renewable solar wind energy","Nobel Prize science discovery","biotech healthcare innovation","nuclear fusion energy","ocean pollution environment","biodiversity species extinction","electric vehicle battery EV","hydrogen fuel cell energy","SpaceX space exploration","extreme weather climate disaster"],
    "사회/이슈":   ["social issue news today","major issue controversy","population demographics statistics","education policy reform","birth rate aging population","crime incident breaking news","labor wage workers strike","welfare healthcare policy","gender diversity equality","youth employment jobs","housing poverty inequality","media press freedom","religion conflict society","immigration multicultural policy","natural disaster safety"],
    "문화/라이프": ["culture lifestyle trend","consumer trend spending","art exhibition museum","K-pop Korean wave hallyu","sports game result score","food travel tourism news","fashion beauty trend","movie OTT streaming content","gaming esports news","book publishing literature","health fitness wellness","pet market animal","luxury brand consumption","wellness mental health trend","entertainment celebrity news"],
}

@st.cache_data(ttl=300)
def fetch_news(category: str, count: int, days: int, region_mode: str = "한국") -> list:
    time_limit = f"d{days}"
    if region_mode == "한국":
        search_plan = [("kr-kr", CATEGORY_KEYWORDS.get(category, [category]))]
    elif region_mode == "해외":
        en_q = CATEGORY_KEYWORDS_EN.get(category, [category])
        search_plan = [("us-en", en_q), ("en-ww", en_q)]
    else:
        search_plan = [("kr-kr", CATEGORY_KEYWORDS.get(category, [category])), ("us-en", CATEGORY_KEYWORDS_EN.get(category, [category]))]
    results = []; seen_titles = set()
    try:
        with DDGS() as ddgs:
            for region, queries in search_plan:
                for q in queries:
                    for r in ddgs.news(q, region=region, safesearch="off", timelimit=time_limit, max_results=5):
                        title = r.get("title", "")
                        if title and title not in seen_titles:
                            seen_titles.add(title)
                            results.append({"source": r.get("source",""), "title": title, "link": r.get("url",""), "summary": r.get("body",""), "date": r.get("date","최근"), "image": r.get("image")})
                    if len(results) >= 30: break
                if len(results) >= 30: break
    except Exception as e:
        st.error(f"검색 오류: {e}"); return []
    return results[:count]

def stream_groq(prompt: str, history: list = None) -> str:
    system_msg = {"role": "system", "content": "당신은 한국어 전용 AI 비서 루키입니다. 모든 답변은 100% 한국어로만 작성합니다. 영어, 중국어, 일본어 등 외국어 단어를 절대 사용하지 않습니다. 외래어가 필요하면 한국어로 풀어서 설명합니다. 이 규칙을 어기는 것은 절대 허용되지 않습니다."}
    messages = [system_msg] + (history or []) + [{"role": "user", "content": prompt}]
    def _gen():
        stream = groq_client.chat.completions.create(model=MODEL_NAME, messages=messages, stream=True, max_tokens=3000)
        buffer = ""; in_think = False
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if not delta: continue
            buffer += delta
            if "<think>" in buffer: in_think = True
            if "</think>" in buffer and in_think:
                in_think = False; buffer = buffer.split("</think>")[-1]
            if not in_think and "</think>" in buffer or not in_think and "<think>" not in buffer:
                yield buffer; buffer = ""
    return st.write_stream(_gen())

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    try: st.image(ROOKIE_IMG, use_container_width=True)
    except: pass
    st.markdown("<h1>🐾 루키 비서실</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**📅 검색 기간**")
    days_range = st.slider("", 1, 14, 7, label_visibility="collapsed")
    st.caption(f"최근 {days_range}일 기준으로 검색합니다.")
    st.markdown("---")
    st.markdown("**📒 지식 저장소**")
    if st.session_state.vocab_dict:
        for word, defn in list(st.session_state.vocab_dict.items()):
            with st.expander(f"💎 {word}"):
                new_defn = st.text_area("수정", value=defn, key=f"e_{word}")
                if new_defn != defn: st.session_state.vocab_dict[word] = new_defn
                if st.button("삭제", key=f"d_{word}"):
                    del st.session_state.vocab_dict[word]; st.rerun()
    else:
        st.caption("저장된 단어가 없습니다.")
    st.markdown("---")
    if st.button("🔄 대화 초기화"):
        st.session_state.update(messages=[], vocab_dict={}, news_context="", chat_history=[])
        st.rerun()

# ── 메인 ──────────────────────────────────────────────────────
st.markdown("# 🐾 Rookie")
tab1, tab2 = st.tabs(["서비스 소개", "뉴스 비서실"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — 서비스 소개
# ══════════════════════════════════════════════════════════════
with tab1:

    st.markdown("""
<div class='hero-wrap'>
  <div class='hero-eyebrow'>AI Secretary Series</div>
  <div class='hero-headline'>
    정보의 홍수 속에서<br>
    <span>당신만의 전문가를</span>
  </div>
  <div class='hero-body'>
    투자, 업무, 시사. 세 개의 영역에서 세 명의 AI 비서가<br>
    당신 옆에 24시간 대기합니다.<br>
    더 이상 혼자 모든 걸 알 필요가 없습니다.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class='stat-row'>
  <div class='stat-card'>
    <div class='stat-num'>3</div>
    <div class='stat-label'>전문 AI 비서</div>
  </div>
  <div class='stat-card'>
    <div class='stat-num'>8</div>
    <div class='stat-label'>뉴스 분야 커버리지</div>
  </div>
  <div class='stat-card'>
    <div class='stat-num'>24h</div>
    <div class='stat-label'>실시간 정보 수집</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class='agent-grid'>

  <div class='a-card'>
    <span class='a-icon'>💎</span>
    <div class='a-pill beta'>Beta 3</div>
    <div class='a-name'>루비</div>
    <div class='a-tagline'>수석 투자 비서</div>
    <div class='a-desc'>
      PER, PBR, EV/EBITDA… 수십 개의 지표 앞에서 막막했던 경험, 있으시죠? 
      루비는 숫자 뒤에 숨겨진 기업의 이야기를 읽어드립니다. 
      초보 투자자도, 베테랑도 — 누구에게나 명확한 언어로.
    </div>
    <div class='a-feature'>원하는 종목 하나로 기술·가치 지표 전체 한눈에</div>
    <div class='a-feature'>지표별 의미 해설 + 함께 봐야 할 관련 지표 안내</div>
    <div class='a-feature'>해당 기업을 둘러싼 시장 감성까지 실시간 분석</div>
  </div>

  <div class='a-card'>
    <span class='a-icon'>🦊</span>
    <div class='a-pill beta'>Beta 4</div>
    <div class='a-name'>루시</div>
    <div class='a-tagline'>업무 전담 비서</div>
    <div class='a-desc'>
      마우스도, 키보드도 필요 없습니다. 루시는 당신의 얼굴과 손을 읽고, 
      말 한마디에 회의실을 장악합니다. 이메일부터 일정까지 — 
      루시가 있으면 업무의 속도가 달라집니다.
    </div>
    <div class='a-feature'>얼굴·손 동작 인식으로 PPT 발표 완전 자동 제어</div>
    <div class='a-feature'>손 모션 하나로 멀티 창 즉시 개폐</div>
    <div class='a-feature'>이메일·캘린더·할일 — 1:1 음성 대화로 전부 관리</div>
  </div>

  <div class='a-card'>
    <span class='a-icon'>🐶</span>
    <div class='a-pill soon'>Coming Soon</div>
    <div class='a-name'>루키</div>
    <div class='a-tagline'>시사 전문 비서</div>
    <div class='a-desc'>
      매일 쏟아지는 수천 개의 뉴스. 루키는 그 중에서 당신에게 
      진짜 중요한 것만 골라 깊이 있게 분석합니다. 
      읽는 것이 아니라 이해하는 뉴스를 경험해보세요.
    </div>
    <div class='a-feature'>경제·정치·과학 등 8대 분야 자동 수집 및 분류</div>
    <div class='a-feature'>단순 요약을 넘어선 심층 배경 분석과 전망 제공</div>
    <div class='a-feature'>스크랩 내용 기반 AI와의 1:1 심층 토론 지원</div>
  </div>

</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='divider-gold'></div>", unsafe_allow_html=True)

    st.markdown("""
<div class='cta-section'>
  <div class='cta-title'>지금 루키를 직접 경험해보세요</div>
  <div class='cta-sub'>
    위 탭 <b style='color:#c9a84c;'>뉴스 비서실</b>에서 시사 전문 비서 루키의 베타 버전을 바로 사용해보실 수 있습니다.<br>
    사용 중 불편한 점이나 개선 아이디어는 언제든 메일로 보내주세요. 빠르게 반영하겠습니다.
  </div>
  <div style='font-size:0.82rem; color:#5c5648; margin-top:12px;'>
    <a href='mailto:compway@yu.ac.kr' style='color:#c9a84c;'>compway@yu.ac.kr</a>
    &nbsp;·&nbsp; 개발: 성무진 · 강연화 · 박현수
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — 뉴스 비서실
# ══════════════════════════════════════════════════════════════
with tab2:

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=ROOKIE_IMG if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    if not st.session_state.messages:
        with st.chat_message("assistant", avatar=ROOKIE_IMG):
            st.markdown("""
<div class='notice-box'>
<div class='notice-title'>개발 노트</div>
<div style='font-size:0.88rem; line-height:2.1; color:#9a9180; padding:4px 0;'>
ⓐ 현재 AI Rookie는 개발 중인 모델의 일부이며, 완전히 구현되지 않아 오류가 발생할 수 있습니다.<br><br>
ⓑ 미구현 기능: 지식저장소 영구보존, 1:1 채팅의 자연스러운 흐름, 단어 저장 기능<br><br>
ⓒ 현재 환경은 <b style='color:#c9a84c;'>신문 및 시사 뉴스 스크랩</b> 전용으로 제작되었습니다.<br><br>
ⓓ 3월 초순부터 개발이 시작되었으며, 실시간으로 업데이트 중입니다.<br><br>
ⓔ 다수 사용자 동시 접속 시 생성 제한 및 오류가 발생할 수 있습니다.<br><br>
ⓕ 클라우드 서버 특성상 배포 안정성에 일부 한계가 있을 수 있습니다.<br><br>
ⓖ PC 환경 및 Dark 모드 사용을 권장합니다.<br><br>
<b style='color:#c9a84c;'>테스터분들께:</b> 현재 뉴스는 인기·조회수 기반 알고리즘으로 선별됩니다. 이 방식이 좋은지, 혹은 더 다양한 뉴스 노출이 필요한지 피드백 주시면 적극 반영하겠습니다.<br><br>
오류·개선사항: <a href='mailto:compway@yu.ac.kr'>compway@yu.ac.kr</a><br><br>
<span style='color:#5c5648; font-size:0.8rem;'>
1차: 2026/03/17 22:40 · 2차(UI): 2026/03/17 23:25 · 3차(채팅 개선): 2026/03/18 07:23 · 4차(언어·지역 선택): 2026/03/18 11:32
</span>
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"안녕하십니까. 최근 **{days_range}일**간의 뉴스를 분석해 드립니다.")
            st.markdown("**🌍 뉴스 수급 지역**")
            region_choice = st.radio("", options=["🇰🇷 한국 신문", "🌐 해외 신문", "🗺️ 전체 (한국 + 해외)"], horizontal=True, label_visibility="collapsed")
            region_map_ui = {"🇰🇷 한국 신문": "한국", "🌐 해외 신문": "해외", "🗺️ 전체 (한국 + 해외)": "전체"}
            selected_region = region_map_ui[region_choice]
            if selected_region in ["해외", "전체"]:
                st.caption({"해외": "BBC, Reuters, Bloomberg 등 영어권 언론을 검색합니다.", "전체": "한국 + 해외 언론을 동시에 검색합니다. 시간이 다소 걸릴 수 있습니다."}[selected_region])
                st.warning("해외 뉴스는 번역 처리로 인해 최대 2개까지 선택 가능합니다.")
                count = st.select_slider("기사 개수", options=[1, 2], value=2)
            else:
                st.caption("한국 언론사 기사만 검색합니다.")
                count = st.select_slider("기사 개수", options=[1, 2, 3, 4, 5], value=3)
            st.markdown("---")
            cats = list(CATEGORY_KEYWORDS.keys())
            for row in [cats[i:i+4] for i in range(0, len(cats), 4)]:
                for col, cat in zip(st.columns(4), row):
                    if col.button(cat):
                        st.session_state.update(selected_category=cat, selected_count=count, selected_region=selected_region)
                        st.session_state.messages.append({"role": "user", "content": f"[{cat}] 최근 {days_range}일 {region_choice} 뉴스 {count}개 스크랩"})
                        st.rerun()

    if "selected_category" in st.session_state:
        cat = st.session_state.pop("selected_category")
        cnt = st.session_state.pop("selected_count")
        region_mode = st.session_state.pop("selected_region", "한국")
        with st.chat_message("assistant", avatar=ROOKIE_IMG):
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown("<div style='text-align:center;padding:24px 0;'><div style='font-family:Playfair Display,serif;font-size:1.3rem;color:#c9a84c;font-weight:700;margin-bottom:10px;'>루키가 정리중이에요</div><div style='font-size:0.85rem;color:#5c5648;'>잠시만 기다려 주십시오</div></div>", unsafe_allow_html=True)
                video_path = os.path.join(os.path.dirname(__file__), "Video Project.mp4")
                with open(video_path, "rb") as f:
                    video_b64 = base64.b64encode(f.read()).decode()
                components.html(f'<video width="100%" autoplay playsinline loop><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>', height=400)
            news_data = fetch_news(cat, cnt, days_range, region_mode)
            time.sleep(7)
            loading_placeholder.empty()
            if not news_data:
                st.warning("검색 결과가 없습니다. 다른 분야를 선택해 주세요.")
            else:
                parts = []
                for i, item in enumerate(news_data):
                    st.markdown(f"<div class='report-title'>— {i+1}. {item['title']}</div>", unsafe_allow_html=True)
                    if item["image"]: st.image(item["image"], width=700)
                    prompt = f"""아래 뉴스 기사를 분석하여 반드시 한국어로만 작성하세요.
기사가 영어인 경우, 먼저 한국어로 완전히 번역한 뒤 아래 형식으로 분석을 진행하세요.

[기사 정보]
제목: {item['title']}
내용: {item['summary']}

[작성 형식]
기본 내용: 이 기사의 전반적인 내용을 15~20문장으로 자연스럽고 풍부하게 서술하세요.
핵심 요약: 이 기사의 핵심을 3~5문장으로 간결하게 요약
심층 분석
- 발생 배경: 이 사건/이슈가 왜 발생했는지
- 전개 과정: 현재까지 어떻게 진행됐는지
- 향후 전망: 앞으로 어떻게 될 것으로 예상되는지
루키의 단어 사전
- 용어1: 쉬운 설명
- 용어2: 쉬운 설명
주의사항: 반드시 한국어로만 작성, 외국어 절대 사용 금지, 대표님께 조언 금지"""
                    try:
                        analysis = stream_groq(prompt)
                    except Exception as e:
                        analysis = f"오류: {e}"; st.error(analysis)
                    c1, c2, c3 = st.columns([2, 2, 1])
                    w = c1.text_input("단어", key=f"w_{i}")
                    d = c2.text_input("정의", key=f"d_{i}")
                    if c3.button("저장", key=f"b_{i}") and w:
                        st.session_state.vocab_dict[w] = d; st.toast(f"'{w}' 저장 완료!")
                    st.markdown(f"[기사 원문]({item['link']}) · {item['source']} · {item['date']}")
                    st.markdown("---")
                    st.session_state.news_context += f"\n{analysis}"
                    parts.append(f"**{i+1}. {item['title']}**\n{analysis}")
                st.session_state.messages.append({"role": "assistant", "content": "\n\n".join(parts)})

if user_input := st.chat_input("루키에게 무엇이든 물어보세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        try:
            if st.session_state.news_context and not st.session_state.chat_history:
                st.session_state.chat_history.append({"role": "user", "content": f"[참고 스크랩 내용]\n{st.session_state.news_context}\n\n위 내용을 참고하여 답변해 주세요."})
                st.session_state.chat_history.append({"role": "assistant", "content": "네, 스크랩된 내용을 참고하여 답변드리겠습니다."})
            res = stream_groq(user_input, history=st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": res})
            if len(st.session_state.chat_history) > 20:
                st.session_state.chat_history = st.session_state.chat_history[-20:]
            st.session_state.messages.append({"role": "assistant", "content": res})
        except Exception as e:
            st.error(f"오류: {e}")
