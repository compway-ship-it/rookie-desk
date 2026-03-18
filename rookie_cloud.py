"""루키 비서실 — 클라우드 버전 (Groq API + Supabase DB)"""
import streamlit as st
import streamlit.components.v1 as components
from duckduckgo_search import DDGS
from groq import Groq
from supabase import create_client
import os, base64, time, json, re, random
from datetime import datetime, timezone, timedelta

# ── 한국 시간 헬퍼 ─────────────────────────────────────────────
_KST = timezone(timedelta(hours=9))
def _kst_now() -> datetime:
    return datetime.now(_KST)

def _today_str() -> str:
    """예: 2026년 3월 18일 (화요일)"""
    d = _kst_now()
    WEEKDAY_KR = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
    return f"{d.year}년 {d.month}월 {d.day}일 ({WEEKDAY_KR[d.weekday()]})"

def _today_search_str() -> str:
    """검색 쿼리용: 예: 2026년 3월 18일"""
    d = _kst_now()
    return f"{d.year}년 {d.month}월 {d.day}일"

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

/* ══ 모바일 반응형 ════════════════════════════════════════ */
@media (max-width: 768px) {

  /* 히어로 섹션 */
  .hero-wrap { padding: 40px 0 32px; }
  .hero-headline { font-size: 1.9rem !important; letter-spacing: -0.5px; }
  .hero-body { font-size: 0.92rem; margin-bottom: 36px; padding: 0 4px; }
  .hero-eyebrow { font-size: 0.65rem; letter-spacing: 2px; padding: 4px 14px; }

  /* 통계 카드 — 3열 → 3열 유지하되 크기 축소 */
  .stat-row { gap: 10px; margin: 28px 0; }
  .stat-card { padding: 16px 10px; border-radius: 10px; }
  .stat-num { font-size: 1.6rem; }
  .stat-label { font-size: 0.72rem; }

  /* 에이전트 카드 — 3열 → 1열 */
  .agent-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    margin: 0 0 36px;
  }
  .a-card { padding: 24px 20px 20px; border-radius: 16px; }
  .a-icon { font-size: 2rem; margin-bottom: 12px; }
  .a-name { font-size: 1.2rem; }
  .a-desc { font-size: 0.84rem; }
  .a-feature { font-size: 0.8rem; padding: 10px 12px; }

  /* CTA 섹션 */
  .cta-section { padding: 32px 20px; }
  .cta-title { font-size: 1.3rem; }
  .cta-sub { font-size: 0.84rem; }

  /* 개발 노트 */
  .notice-box { padding: 16px 18px; font-size: 0.82rem; }
  .notice-title { font-size: 0.92rem; }

  /* 리포트 제목 */
  .report-title { font-size: 1.05rem; }

  /* 탭 버튼 */
  [data-testid="stTabs"] button[role="tab"] {
    font-size: 0.82rem !important;
    padding: 8px 12px !important;
  }

  /* 슬라이더 패딩 축소 */
  [data-testid="stSlider"] { padding: 10px 12px !important; }

  /* 라디오 버튼 — 모바일에서 세로 정렬 */
  [data-testid="stRadio"] > div {
    flex-direction: column !important;
    gap: 6px !important;
  }
  [data-testid="stRadio"] label {
    width: 100% !important;
    text-align: center !important;
  }

  /* 채팅 입력창 */
  [data-testid="stChatInput"] > div { border-radius: 10px !important; }

  /* 기사 이미지 모바일 꽉차게 */
  [data-testid="stImage"] img { width: 100% !important; max-width: 100% !important; }
}

@media (max-width: 480px) {
  /* 극소형 화면 추가 대응 */
  .hero-headline { font-size: 1.55rem !important; }
  .stat-row { grid-template-columns: repeat(3, 1fr); }
  .stat-num { font-size: 1.3rem; }
  .a-name { font-size: 1.1rem; }
  .hero-body { font-size: 0.85rem; }
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

# ── Supabase 클라이언트 ───────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_KEY"]  # service_role 키 사용
    )

supabase = get_supabase()

# ── 인증 함수 ─────────────────────────────────────────────────
REFERRAL_CODE = "admin9416"  # 추천인 코드
MAX_USERS = 30

def auth_generate_code() -> str:
    """고유 코드 자동 생성 (ROOKIE-XXXX 형태)"""
    import random, string
    while True:
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"ROOKIE-{suffix}"
        # 중복 체크
        try:
            res = supabase.table("users").select("code").eq("code", code).execute()
            if not res.data:
                return code
        except Exception:
            return code

def auth_check_capacity() -> bool:
    """30명 미만인지 확인"""
    try:
        res = supabase.table("users").select("code").execute()
        return len(res.data) < MAX_USERS
    except Exception:
        return True  # 오류 시 가입 허용

def auth_register(name: str):
    """신규 회원 등록 → {code, name} 반환"""
    try:
        code = auth_generate_code()
        supabase.table("users").insert({"code": code, "name": name.strip()}).execute()
        return {"code": code, "name": name.strip()}
    except Exception as e:
        st.error(f"등록 오류 상세: {e}")
        return None

def auth_login(code: str):
    """기등록 유저 로그인"""
    try:
        res = supabase.table("users").select("code, name").eq("code", code.strip().upper()).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

# ── 이용 횟수 제한 (성무진 제외) ─────────────────────────────
UNLIMITED_USERS = {"ROOKIE-APFG13"}   # 무제한 허용 코드 목록
DAILY_LIMIT_KR  = 5                   # 한국 뉴스 1회 분석 = 1카운트
DAILY_LIMIT_OVERSEAS = 3              # 해외/전체 뉴스 1회 분석 = 1카운트

def _usage_key(user_code: str) -> str:
    """오늘 날짜 기반 Supabase 저장 키 — 예: usage_2026-03-18"""
    return f"usage_{_kst_now().strftime('%Y-%m-%d')}"

def db_get_usage(user_code: str) -> dict:
    """오늘 사용 횟수 조회. {"kr": 0, "overseas": 0}"""
    try:
        key = _usage_key(user_code)
        res = supabase.table("users").select(key).eq("code", user_code).execute()
        if res.data and res.data[0].get(key):
            return res.data[0][key]
    except Exception:
        pass
    return {"kr": 0, "overseas": 0}

def db_increment_usage(user_code: str, region_mode: str):
    """분석 1회 완료 시 카운트 +1"""
    try:
        key   = _usage_key(user_code)
        usage = db_get_usage(user_code)
        if region_mode == "한국":
            usage["kr"] = usage.get("kr", 0) + 1
        else:
            usage["overseas"] = usage.get("overseas", 0) + 1
        supabase.table("users").update({key: usage}).eq("code", user_code).execute()
    except Exception:
        pass

def check_usage_limit(user_code: str, region_mode: str) -> tuple[bool, str]:
    """
    (허용 여부, 안내 메시지) 반환.
    무제한 코드면 항상 (True, "").
    """
    if user_code in UNLIMITED_USERS:
        return True, ""
    usage = db_get_usage(user_code)
    if region_mode == "한국":
        used  = usage.get("kr", 0)
        limit = DAILY_LIMIT_KR
        label = "한국 뉴스"
    else:
        used  = usage.get("overseas", 0)
        limit = DAILY_LIMIT_OVERSEAS
        label = "해외/전체 뉴스"
    if used >= limit:
        return False, (
            f"오늘 **{label}** 분석 가능 횟수({limit}회)를 모두 사용했습니다. 🐾\n\n"
            f"내일 자정(KST)에 횟수가 초기화됩니다."
        )
    return True, f"오늘 **{label}** 남은 횟수: {limit - used}회"

# ── DB 헬퍼 함수 (user_code 기반 개인별 분리) ────────────────
def db_load_vocab(user_code: str) -> dict:
    try:
        res = supabase.table("vocab_store").select("word, definition").eq("user_code", user_code).order("created_at").execute()
        return {row["word"]: row["definition"] for row in res.data}
    except Exception:
        return {}

def db_save_vocab(user_code: str, word: str, definition: str):
    try:
        exists = supabase.table("vocab_store").select("id").eq("user_code", user_code).eq("word", word).execute()
        if exists.data:
            supabase.table("vocab_store").update({"definition": definition}).eq("user_code", user_code).eq("word", word).execute()
        else:
            supabase.table("vocab_store").insert({"user_code": user_code, "word": word, "definition": definition}).execute()
    except Exception as e:
        st.toast(f"저장 오류: {e}", icon="🔴")

def db_delete_vocab(user_code: str, word: str):
    try:
        supabase.table("vocab_store").delete().eq("user_code", user_code).eq("word", word).execute()
    except Exception as e:
        st.toast(f"삭제 오류: {e}", icon="🔴")

def db_load_bookmarks(user_code: str) -> list:
    try:
        res = supabase.table("bookmarks").select("*").eq("user_code", user_code).order("created_at", desc=True).execute()
        return res.data
    except Exception:
        return []

def db_save_bookmark(user_code: str, item: dict) -> bool:
    try:
        exists = supabase.table("bookmarks").select("id").eq("user_code", user_code).eq("link", item["link"]).execute()
        if exists.data:
            return False
        supabase.table("bookmarks").insert({
            "user_code": user_code,
            "title":   item["title"],
            "link":    item["link"],
            "source":  item.get("source", ""),
            "date":    item.get("date", ""),
            "summary": item.get("summary", "")[:300],
        }).execute()
        return True
    except Exception as e:
        st.toast(f"북마크 오류: {e}", icon="🔴")
        return False

def db_delete_bookmark(bookmark_id: str):
    try:
        supabase.table("bookmarks").delete().eq("id", bookmark_id).execute()
    except Exception as e:
        st.toast(f"삭제 오류: {e}", icon="🔴")

if "messages"     not in st.session_state: st.session_state.messages     = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "news_context" not in st.session_state: st.session_state.news_context = ""
if "pending_news" not in st.session_state: st.session_state.pending_news = []
if "filtered_news_cache"  not in st.session_state: st.session_state.filtered_news_cache  = []
if "analyzed_results"     not in st.session_state: st.session_state.analyzed_results     = []
if "current_user" not in st.session_state: st.session_state.current_user = None
if "show_category_ui"     not in st.session_state: st.session_state.show_category_ui     = True

# ── URL 쿼리 파라미터로 로그인 유지 ──────────────────────────
# ?code=ROOKIE-XXXXXX 가 URL에 있으면 자동 로그인
if st.session_state.current_user is None:
    params = st.query_params
    url_code = params.get("code", None)
    if url_code:
        user = auth_login(url_code)
        if user:
            st.session_state.current_user = user
            st.session_state.vocab_dict   = db_load_vocab(user["code"])
            st.session_state.bookmarks    = db_load_bookmarks(user["code"])

# ── 로그인 / 회원가입 화면 ────────────────────────────────────
if st.session_state.current_user is None:
    st.markdown("""
<div style='max-width:420px; margin:80px auto 0; text-align:center;'>
  <div style='font-family:Playfair Display,serif; font-size:2.2rem; font-weight:900;
              background:linear-gradient(135deg,#e8c76a,#c9a84c);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent;
              margin-bottom:8px;'>🐾 Rookie</div>
  <div style='font-size:0.9rem; color:#5c5648; margin-bottom:40px;'>
      AI 비서 시리즈 — 0차 비공개 베타
  </div>
</div>
""", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
            border-radius:16px; padding:32px 28px;'>
""", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["로그인", "첫 방문 (회원가입)"])

        # ── 로그인 탭 ──
        with tab_login:
            st.caption("발급받은 코드로 로그인하세요.")
            login_code = st.text_input(
                "접근 코드",
                placeholder="ROOKIE-XXXXXX",
                key="login_code_input"
            ).strip().upper()
            if st.button("로그인", use_container_width=True, type="primary", key="btn_login"):
                if not login_code:
                    st.warning("접근 코드를 입력해 주세요.")
                else:
                    user = auth_login(login_code)
                    if user:
                        st.session_state.current_user = user
                        st.session_state.vocab_dict   = db_load_vocab(user["code"])
                        st.session_state.bookmarks    = db_load_bookmarks(user["code"])
                        st.query_params["code"] = user["code"]
                        st.rerun()
                    else:
                        st.error("등록된 코드가 아닙니다. 첫 방문이라면 회원가입 탭을 이용해 주세요.")

        # ── 회원가입 탭 ──
        with tab_signup:
            st.caption("추천인 코드 확인 후 이름을 입력하면 고유 코드가 발급됩니다.")

            referral = st.text_input(
                "누구에게 추천을 받으셨나요?",
                placeholder="추천인 코드 입력",
                key="referral_input"
            ).strip()

            referral_ok = referral == REFERRAL_CODE
            if referral and not referral_ok:
                st.error("올바르지 않은 추천인 코드입니다.")
            if referral_ok:
                st.success("추천인 확인 완료! 이름을 입력해 주세요.")

            name_input = st.text_input(
                "이름 (꼭 실명을 입력하세요!)",
                placeholder="예: 홍길동",
                key="signup_name_input",
                disabled=not referral_ok,
                help="베타 테스트 관리를 위해 실명이 필요합니다."
            )

            if st.button("가입하고 코드 발급받기", use_container_width=True,
                         type="primary", key="btn_signup", disabled=not referral_ok):
                if not name_input.strip():
                    st.warning("이름을 입력해 주세요.")
                elif not auth_check_capacity():
                    st.error(f"베타 테스터 정원({MAX_USERS}명)이 초과되었습니다.")
                else:
                    user = auth_register(name_input.strip())
                    if user:
                        st.session_state.current_user = user
                        st.session_state.vocab_dict   = {}
                        st.session_state.bookmarks    = []
                        st.session_state.new_code     = user["code"]
                        st.query_params["code"] = user["code"]
                        st.rerun()
                    else:
                        st.error("등록 중 오류가 발생했습니다. 다시 시도해 주세요.")

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ── 로그인 후 세션 데이터 초기화 ──────────────────────────────
user_code = st.session_state.current_user["code"]
user_name = st.session_state.current_user["name"]
if "vocab_dict"  not in st.session_state: st.session_state.vocab_dict  = db_load_vocab(user_code)
if "bookmarks"   not in st.session_state: st.session_state.bookmarks   = db_load_bookmarks(user_code)

# ── 신규 가입 코드 안내 배너 (한 번만 표시) ────────────────────
if st.session_state.get("new_code"):
    st.success(f"환영합니다, {user_name}님! 🐾")
    st.warning(f"""⚠️ **이 코드는 꼭 기억해 두세요!**

📋 **내 접근 코드: `{st.session_state.new_code}`**

이 코드는 다음 로그인 시 반드시 필요합니다.
코드를 분실하면 재발급이 어려우니 메모장, 카카오톡 나에게 보내기 등에 저장해 두세요.""")
    if st.button("코드를 저장했어요 ✓"):
        del st.session_state["new_code"]
        st.rerun()

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
    time_limit  = f"d{days}"
    today_label = _today_search_str()   # 예: "2026년 3월 18일"

    # ── 키워드 샘플링 ────────────────────────────────────────────
    # 전체 키워드 풀에서 매번 다른 조합을 뽑아 다양성 확보
    # days=1(오늘)이면 날짜를 쿼리에 직접 붙여 최신성 강화
    def _sample(pool: list, n: int = 4) -> list:
        sampled = random.sample(pool, min(n, len(pool)))
        if days <= 1:
            # 오늘 날짜를 키워드에 붙여 당일 기사 우선 노출
            sampled = [f"{q} {today_label}" for q in sampled]
        return sampled

    kr_queries = _sample(CATEGORY_KEYWORDS.get(category, [category]))
    en_queries = _sample(CATEGORY_KEYWORDS_EN.get(category, [category]))

    if region_mode == "한국":
        search_plan = [("kr-kr", kr_queries)]
    elif region_mode == "해외":
        search_plan = [("us-en", en_queries), ("en-ww", en_queries)]
    else:
        search_plan = [("kr-kr", kr_queries), ("us-en", en_queries)]

    results = []; seen_titles = set()
    try:
        with DDGS() as ddgs:
            for region, queries in search_plan:
                for q in queries:
                    for r in ddgs.news(q, region=region, safesearch="off", timelimit=time_limit, max_results=5):
                        title = r.get("title", "")
                        if title and title not in seen_titles:
                            seen_titles.add(title)
                            results.append({
                                "source":  r.get("source", ""),
                                "title":   title,
                                "link":    r.get("url", ""),
                                "summary": r.get("body", ""),
                                "date":    r.get("date", "최근"),
                                "image":   r.get("image"),
                            })
                    if len(results) >= 30: break
                if len(results) >= 30: break
    except Exception as e:
        st.error(f"검색 오류: {e}"); return []
    return results[:count]

def stream_groq(prompt: str, history: list = None) -> str:
    system_msg = {
        "role": "system",
        "content": (
            f"당신은 한국어 전용 AI 비서 루키입니다. "
            f"오늘은 {_today_str()}입니다. 한국 표준시(KST) 기준입니다. "
            "날짜나 시점이 언급되면 이 날짜를 기준으로 판단하세요. "
            "모든 답변은 100% 한국어로만 작성합니다. "
            "영어, 중국어, 일본어 등 외국어 단어를 절대 사용하지 않습니다. "
            "외래어가 필요하면 한국어로 풀어서 설명합니다. "
            "이 규칙을 어기는 것은 절대 허용되지 않습니다."
        )
    }
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
    return st.write_stream(_gen()) or ""

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    try: st.image(ROOKIE_IMG, use_container_width=True)
    except: pass
    st.markdown("<h1>🐾 루키 비서실</h1>", unsafe_allow_html=True)

    st.markdown(f"""
<div style='background:rgba(201,168,76,0.08); border:1px solid rgba(201,168,76,0.2);
            border-radius:10px; padding:10px 14px; margin-bottom:12px;
            font-size:0.85rem; color:#c9a84c;'>
  🐾 &nbsp;<b>{user_name}</b>
  <span style='color:#5c5648; font-size:0.75rem; margin-left:6px;'>{user_code}</span>
</div>
""", unsafe_allow_html=True)

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
                if new_defn != defn:
                    st.session_state.vocab_dict[word] = new_defn
                    db_save_vocab(user_code, word, new_defn)
                if st.button("삭제", key=f"d_{word}"):
                    db_delete_vocab(user_code, word)
                    del st.session_state.vocab_dict[word]
                    st.rerun()
    else:
        st.caption("저장된 단어가 없습니다.")
    st.markdown("---")

    st.markdown("**🔖 북마크**")
    if st.session_state.bookmarks:
        for bm in list(st.session_state.bookmarks):
            with st.expander(f"📌 {bm['title'][:22]}..."):
                st.caption(f"{bm['source']} · {bm['date']}")
                st.markdown(f"[원문 보기]({bm['link']})")
                if st.button("삭제", key=f"bm_del_{bm['id']}"):
                    db_delete_bookmark(bm["id"])
                    st.session_state.bookmarks = db_load_bookmarks(user_code)
                    st.rerun()
    else:
        st.caption("저장된 북마크가 없습니다.")
    st.markdown("---")

    col_reset, col_logout = st.columns(2)
    if col_reset.button("🔄 초기화"):
        st.session_state.update(
            messages=[], news_context="",
            chat_history=[], pending_news=[],
            filtered_news_cache=[], analyzed_results=[]
        )
        st.rerun()
    if col_logout.button("🚪 로그아웃"):
        st.query_params.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── 메인 ──────────────────────────────────────────────────────
st.markdown("# 🐾 Rookie")
tab1, tab2, tab3 = st.tabs(["우리는 이런걸 만듭니다", "📖 루키 사용법", "🐶 루키 비서실"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — 서비스 소개
# ══════════════════════════════════════════════════════════════
with tab1:

    st.markdown("""
<div class='hero-wrap'>
  <div class='hero-eyebrow'>AI Secretary Series</div>
  <div class='hero-headline'>
    작은 화면 안에서<br>
    <span>당신만의 전문가를</span>
  </div>
  <div class='hero-body'>
    투자, 업무, 시사. 세 개의 영역에서 세 명의 AI 비서가<br>
    당신 옆에 24시간 대기합니다.<br>
    더 이상 혼자 모든 걸 할 필요가 없습니다.
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
    <span class='a-icon'>🐱</span>
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
    <div class='a-pill soon'>0차 비공개 베타</div>
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
    <div style='margin-top:20px; padding:12px 16px; background:rgba(92,196,122,0.07); border:1px solid rgba(92,196,122,0.2); border-radius:10px; font-size:0.8rem; color:#5cc47a; line-height:1.7;'>
      🎁 &nbsp;<b>정식 배포 시 루키는 무료로 이용 가능합니다.</b><br>
      <span style='color:#3a7a4a; font-size:0.75rem;'>현재는 비공개 테스트 단계입니다.</span>
    </div>
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
# TAB 2 — 루키 사용법
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
<div style='max-width:760px; margin:0 auto;'>

<div style='text-align:center; padding:56px 0 40px;'>
  <div style='font-size:3.2rem; margin-bottom:16px;'>🐶</div>
  <div style='font-family:Playfair Display,serif; font-size:clamp(1.8rem,4vw,2.6rem); font-weight:900;
              background:linear-gradient(135deg,#e8c76a,#c9a84c);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent;
              margin-bottom:12px; letter-spacing:-0.5px;'>안녕하세요, 저는 루키예요!</div>
  <div style='font-size:1rem; color:#9a9180; line-height:1.9; font-weight:300;'>
    시사 뉴스 전담 AI 비서입니다.<br>
    제가 무엇을 할 수 있는지, 어떻게 쓰시면 되는지 직접 안내해 드릴게요.
  </div>
</div>

<div style='height:1px; background:linear-gradient(90deg,transparent,rgba(201,168,76,0.3),transparent); margin:8px 0 40px;'></div>

<!-- 기능 소개 카드 1 -->
<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:28px 32px; margin-bottom:20px;'>
  <div style='font-size:1.5rem; margin-bottom:10px;'>📰</div>
  <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:#e8c76a; margin-bottom:10px;'>① 카테고리 버튼으로 뉴스 스크랩</div>
  <div style='font-size:0.9rem; color:#9a9180; line-height:2.0;'>
    <b style='color:#f0ece2;'>루키 비서실</b> 탭에 들어오면 처음에 8개 분야 버튼이 보여요.<br>
    <span style='color:#c9a84c;'>경제/증시, AI/미래기술, 정치/외교, 산업/부동산, 글로벌 뉴스, 과학/환경, 사회/이슈, 문화/라이프</span><br><br>
    원하는 분야를 누르면 제가 최신 기사를 자동으로 모아와요.<br>
    그 다음엔 수집된 기사 목록이 나타나고, <b style='color:#f0ece2;'>심층 분석할 기사를 체크</b>한 뒤<br>
    <b style='color:#c9a84c;'>「🔍 선택한 기사 심층 분석 시작」</b> 버튼을 눌러주세요.<br><br>
    저는 각 기사마다 <b style='color:#f0ece2;'>기본 내용 → 핵심 요약 → 심층 분석 → 단어 사전</b> 순서로 분석해 드립니다.
  </div>
</div>

<!-- 기능 소개 카드 2 -->
<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:28px 32px; margin-bottom:20px;'>
  <div style='font-size:1.5rem; margin-bottom:10px;'>💬</div>
  <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:#e8c76a; margin-bottom:10px;'>② 채팅창에서 자유롭게 요청하세요</div>
  <div style='font-size:0.9rem; color:#9a9180; line-height:2.0;'>
    버튼 없이도 아래 채팅창에 자유롭게 입력하면 돼요.<br>
    뉴스 관련 요청이면 자동으로 뉴스 검색 모드로 전환되고,<br>
    궁금한 점을 물어보면 일반 대화로 답해드려요.<br><br>
    <b style='color:#c9a84c;'>이런 표현들을 쓰면 잘 알아들어요 👇</b><br>
    <span style='background:rgba(201,168,76,0.08); border:1px solid rgba(201,168,76,0.2); border-radius:8px; padding:14px 18px; display:block; margin-top:10px; line-height:2.2; font-size:0.86rem; color:#c9a84c;'>
      "오늘 반도체 뉴스 보여줘"<br>
      "미국 금리 최신 소식 2개만"<br>
      "이번 주 부동산 동향 알려줘"<br>
      "AI 관련 해외 기사 찾아줘"<br>
      "방금 본 기사에서 PER이 뭐야?" <span style='color:#5c5648;'>(← 일반 질문)</span>
    </span>
  </div>
</div>

<!-- 기능 소개 카드 3 -->
<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:28px 32px; margin-bottom:20px;'>
  <div style='font-size:1.5rem; margin-bottom:10px;'>💎</div>
  <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:#e8c76a; margin-bottom:10px;'>③ 단어 저장 — 지식 저장소</div>
  <div style='font-size:0.9rem; color:#9a9180; line-height:2.0;'>
    기사 분석이 끝난 뒤, 각 기사 아래에 <b style='color:#f0ece2;'>단어 입력창</b>이 나와요.<br>
    생소한 용어나 기억하고 싶은 단어를 입력하고 <b style='color:#c9a84c;'>「저장」</b> 버튼을 누르면<br>
    왼쪽 사이드바 <b style='color:#f0ece2;'>📒 지식 저장소</b>에 영구 보관돼요.<br><br>
    저장된 단어는 언제든 수정하거나 삭제할 수 있어요.<br>
    다음에 다시 로그인해도 그대로 남아 있으니 걱정 마세요!
  </div>
</div>

<!-- 기능 소개 카드 4 -->
<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:28px 32px; margin-bottom:20px;'>
  <div style='font-size:1.5rem; margin-bottom:10px;'>🔖</div>
  <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:#e8c76a; margin-bottom:10px;'>④ 북마크 — 기사 저장</div>
  <div style='font-size:0.9rem; color:#9a9180; line-height:2.0;'>
    마음에 드는 기사는 <b style='color:#c9a84c;'>「🔖」 버튼</b>으로 저장할 수 있어요.<br>
    저장된 기사는 왼쪽 사이드바 <b style='color:#f0ece2;'>🔖 북마크</b> 목록에서 확인하고<br>
    언제든 원문 링크로 다시 읽을 수 있어요.<br>
    같은 기사를 두 번 저장해도 중복 저장은 되지 않으니 안심하세요.
  </div>
</div>

<!-- 기능 소개 카드 5 -->
<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:28px 32px; margin-bottom:20px;'>
  <div style='font-size:1.5rem; margin-bottom:10px;'>⚙️</div>
  <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:#e8c76a; margin-bottom:10px;'>⑤ 사이드바 설정 활용하기</div>
  <div style='font-size:0.9rem; color:#9a9180; line-height:2.0;'>
    왼쪽 사이드바에서 <b style='color:#c9a84c;'>📅 검색 기간</b> 슬라이더로 1~14일 사이로 조절할 수 있어요.<br>
    "오늘 뉴스"만 보고 싶으면 1일, 최근 2주 동향이 궁금하면 14일로 설정하세요.<br><br>
    뉴스 비서실 첫 화면에서는 <b style='color:#f0ece2;'>🇰🇷 한국 / 🌐 해외 / 🗺️ 전체</b> 중<br>
    원하는 뉴스 수급 지역도 선택할 수 있어요.
  </div>
</div>

<!-- 팁 박스 -->
<div style='background:rgba(92,196,122,0.05); border:1px solid rgba(92,196,122,0.2); border-left:3px solid #5cc47a; border-radius:12px; padding:22px 26px; margin-bottom:20px;'>
  <div style='font-size:0.88rem; font-weight:700; color:#5cc47a; margin-bottom:12px; letter-spacing:0.3px;'>🐾 루키의 TIP</div>
  <div style='font-size:0.87rem; color:#9a9180; line-height:2.0;'>
    • 분석 후 채팅창에서 <b style='color:#f0ece2;'>"이 기사에서 ~가 뭐야?"</b>처럼 물어보면 내용 기반으로 답해드려요.<br>
    • 여러 기사를 한 번에 선택해서 분석하면 흐름을 한눈에 파악할 수 있어요.<br>
    • <b style='color:#f0ece2;'>PC + 다크 모드</b> 환경에서 가장 예쁘게 보여요 🌙<br>
    • 오류나 불편한 점은 <a href='mailto:compway@yu.ac.kr' style='color:#5cc47a;'>compway@yu.ac.kr</a>로 언제든 보내주세요.
  </div>
</div>

<div style='text-align:center; padding:32px 0 48px; font-size:0.88rem; color:#5c5648;'>
  준비되셨으면 위 <b style='color:#c9a84c;'>🐶 루키 비서실</b> 탭으로 이동해서 시작해보세요!
</div>

</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — 뉴스 비서실
# ══════════════════════════════════════════════════════════════
with tab3:

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=ROOKIE_IMG if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    if not st.session_state.messages:
        with st.chat_message("assistant", avatar=ROOKIE_IMG):
            st.markdown("""
<div class='notice-box'>
<div class='notice-title'>개발 노트</div>
<div style='font-size:0.88rem; line-height:2.1; color:#9a9180; padding:4px 0;'>
<b style='color:#c9a84c;'>안녕하세요 테스터님! </b><br>
ⓐ 현재 AI Rookie는 개발 중인 모델의 일부이며, 완전히 구현되지 않아 오류가 발생할 수 있습니다.<br><br>
ⓑ 미구현 기능: 지식저장소 영구보존, 1:1 채팅의 자연스러운 흐름, 단어 저장 기능(*3월 18일 기준 일부 구현)<br><br>
ⓒ 현재 환경은 <b style='color:#c9a84c;'>신문 및 시사 뉴스 스크랩</b> 전용으로 제작되었습니다.<br><br>
ⓓ 현재 Rookie 모델은 3월 초순부터 개발이 시작되었으며, 실시간으로 업데이트 중입니다.<br><br>
ⓔ 다수 사용자 동시 접속 시 생성 제한 및 오류가 발생할 수 있습니다.<br><br>
ⓕ 클라우드 서버 특성상 배포 안정성에 일부 한계가 있을 수 있습니다.<br><br>
ⓖ PC 환경 및 Dark 모드 사용을 권장합니다.<br><br>
<b style='color:#c9a84c;'>테스터분들께:</b> 현재 뉴스는 인기·조회수 기반 알고리즘으로 선별됩니다. 이 방식이 좋은지, 혹은 더 다양한 뉴스 노출이 필요한지 피드백 주시면 적극 반영하겠습니다.<br><br>
오류·개선사항: <a href='mailto:compway@yu.ac.kr'>compway@yu.ac.kr</a><br><br>
<span style='color:#5c5648; font-size:0.8rem;'>
1차: 2026/03/17 22:40 · 2차(UI): 2026/03/17 23:25 · 3차(채팅 개선): 2026/03/18 07:23 · 4차(언어·지역 선택): 2026/03/18 11:32 · 5차(UI전면개편,로그인 기능, 북마크 저장기능의 일부): 2026/03/18 16:04<br>
· 6차(데이터베이스 수정, 보안 로그 수정, 지식 저장소 기능의 일부, 새로고침 시 로그인 화면으로 넘어가는 버그 수정(보안 재검토 필요): 2026/03/18 16:11<br>
· 7차(저장/북마크 None 버그 수정, 루키 사용법 탭 추가, 분석 완료 후 뒤로가기 버튼 추가): 2026/03/18<br>
· 8차(KST 날짜 인식, system prompt 날짜 주입, 검색 키워드 랜덤 샘플링 + 당일 날짜 쿼리 강화): 2026/03/18<br>
· 9차(뒤로가기 후 카테고리 UI 재표시 버그 수정, 이용 횟수 제한): 2026/03/18
</span>
</div>
</div>
""", unsafe_allow_html=True)

    # ── 카테고리 선택 UI (첫 진입 또는 뒤로가기 후) ─────────────
    if st.session_state.show_category_ui:
        with st.chat_message("assistant", avatar=ROOKIE_IMG):
            st.markdown(f"안녕하십니까. 최근 **{days_range}일**간의 뉴스를 분석해 드립니다.")

            # ── 잔여 횟수 안내 (무제한 유저 제외) ──────────────────
            if user_code not in UNLIMITED_USERS:
                usage   = db_get_usage(user_code)
                kr_left = max(0, DAILY_LIMIT_KR - usage.get("kr", 0))
                ov_left = max(0, DAILY_LIMIT_OVERSEAS - usage.get("overseas", 0))
                if kr_left == 0 and ov_left == 0:
                    st.markdown(f"""
<div style='background:rgba(255,100,100,0.07); border:1px solid rgba(255,100,100,0.2);
            border-left:3px solid #ff6464; border-radius:10px; padding:14px 18px;
            font-size:0.88rem; color:#ff9a9a; line-height:1.9; margin-bottom:8px;'>
  😴 &nbsp;오늘 스크랩 횟수를 모두 사용했어요.<br>
  <span style='color:#5c5648; font-size:0.82rem;'>내일 자정(KST)에 횟수가 초기화됩니다.</span>
</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
<div style='background:rgba(201,168,76,0.07); border:1px solid rgba(201,168,76,0.18);
            border-left:3px solid var(--gold); border-radius:10px; padding:14px 18px;
            font-size:0.88rem; color:#c9a84c; line-height:2.0; margin-bottom:8px;'>
  🐾 &nbsp;오늘 만들 수 있는 스크랩이 &nbsp;<b style='color:#e8c76a; font-size:1rem;'>한국 {kr_left}개 · 해외 {ov_left}개</b>&nbsp; 남았어요.<br>
  <span style='color:#5c5648; font-size:0.8rem;'>한국 뉴스 최대 {DAILY_LIMIT_KR}회 · 해외/전체 최대 {DAILY_LIMIT_OVERSEAS}회 / 매일 자정 초기화</span>
</div>""", unsafe_allow_html=True)

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

            # ── 카테고리 버튼 (모바일 2열 / 데스크탑 4열) ──
            st.markdown("""
<style>
/* 모바일에서 카테고리 버튼 2열 */
@media (max-width: 768px) {
  div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 0 !important;
    width: 100% !important;
  }
}
</style>
""", unsafe_allow_html=True)
            cats = list(CATEGORY_KEYWORDS.keys())
            for row in [cats[i:i+4] for i in range(0, len(cats), 4)]:
                for col, cat in zip(st.columns(4), row):
                    if col.button(cat):
                        st.session_state.show_category_ui  = False
                        st.session_state._last_region_mode = selected_region
                        st.session_state.update(selected_category=cat, selected_count=count, selected_region=selected_region)
                        st.session_state.messages.append({"role": "user", "content": f"[{cat}] 최근 {days_range}일 {region_choice} 뉴스 {count}개 스크랩"})
                        st.rerun()

    if "selected_category" in st.session_state:
        cat = st.session_state.pop("selected_category")
        cnt = st.session_state.pop("selected_count")
        region_mode = st.session_state.pop("selected_region", "한국")

        # ── 이용 횟수 사전 체크 ────────────────────────────────────
        allowed, msg = check_usage_limit(user_code, region_mode)
        if not allowed:
            with st.chat_message("assistant", avatar=ROOKIE_IMG):
                st.warning(msg)
            st.session_state.show_category_ui = True
        else:
            if msg:
                st.info(msg)   # 남은 횟수 안내

            with st.chat_message("assistant", avatar=ROOKIE_IMG):
                loading_placeholder = st.empty()
                loading_placeholder.markdown(f"🔍 **[{cat}]** 뉴스를 수집하고 품질을 확인하는 중...")
                raw_news = fetch_news(cat, cnt * 3, days_range, region_mode)
                loading_placeholder.empty()

                if not raw_news:
                    st.warning("검색 결과가 없습니다. 다른 분야를 선택해 주세요.")
                else:
                    # ── ① 품질 필터링 ──────────────────────────────────
                    titles_text = "\n".join([f"{i+1}. {r['title']}" for i, r in enumerate(raw_news)])
                    filter_prompt = f"""아래 뉴스 제목 목록에서 다음 기준으로 상위 {cnt}개를 선택하세요.
기준: 중복 사건 제거(같은 사건은 1개만), 낚시성·광고성 제거, 다양한 주제 포함
뉴스 목록:\n{titles_text}
선택한 기사 번호만 JSON 배열로 응답. 예시: [1, 3, 5]
JSON:"""
                    selected_indices = list(range(min(cnt, len(raw_news))))
                    try:
                        resp = groq_client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[{"role": "user", "content": filter_prompt}],
                            max_tokens=60, stream=False
                        )
                        raw_r = resp.choices[0].message.content.strip()
                        if "</think>" in raw_r: raw_r = raw_r.split("</think>")[-1].strip()
                        arr_match = re.search(r'\[.*?\]', raw_r, re.DOTALL)
                        if arr_match:
                            parsed = json.loads(arr_match.group())
                            selected_indices = [int(x)-1 for x in parsed if 0 < int(x) <= len(raw_news)][:cnt]
                    except Exception:
                        pass

                    filtered = [raw_news[i] for i in selected_indices if i < len(raw_news)]
                    # ★ session_state에 저장 → 체크박스 클릭 시 리런해도 유지됨
                    st.session_state.filtered_news_cache = filtered

    # ── ③ 헤드라인 카드 + 체크박스 ────────────────────────────────
    # selected_category 블록과 분리 → 체크박스 변경 시 리런해도 이 블록만 재렌더링
    if st.session_state.get("filtered_news_cache") and not st.session_state.pending_news:
        filtered = st.session_state.filtered_news_cache
        with st.chat_message("assistant", avatar=ROOKIE_IMG):
            st.markdown("**📋 수집된 기사 — 심층 분석할 기사를 선택하세요**")
            st.caption(f"총 {len(filtered)}개 기사 수집 완료 (중복·낚시성 필터 적용)")

            selected_flags = []
            for i, item in enumerate(filtered):
                col_chk, col_info = st.columns([0.08, 0.92])
                chk = col_chk.checkbox("", value=True, key=f"sel_{i}_{item['title'][:10]}")
                selected_flags.append(chk)
                col_info.markdown(
                    f"**{item['title']}**  \n"
                    f"<span style='font-size:0.78rem;color:var(--text3);'>{item['source']} · {item['date']}</span>",
                    unsafe_allow_html=True
                )

            if st.button("🔍 선택한 기사 심층 분석 시작", type="primary"):
                chosen = [item for item, flag in zip(filtered, selected_flags) if flag]
                if not chosen:
                    st.warning("최소 1개 이상 선택해 주세요.")
                else:
                    st.session_state.pending_news   = chosen
                    st.session_state.pending_region = st.session_state.get("_last_region_mode", "한국")
                    st.session_state.filtered_news_cache = []  # 카드 제거
                    st.rerun()

    # ── ③ 선택된 기사 심층 분석 실행 ─────────────────────────────
    if st.session_state.pending_news:
        news_to_analyze = st.session_state.pending_news
        st.session_state.pending_news = []
        st.session_state.analyzed_results = []  # 분석 결과 캐시 초기화

        with st.chat_message("assistant", avatar=ROOKIE_IMG):
            parts = []
            for i, item in enumerate(news_to_analyze):
                st.markdown(f"<div class='report-title'>— {i+1}. {item['title']}</div>", unsafe_allow_html=True)
                if item["image"]: st.image(item["image"], use_container_width=True)

                prompt = f"""아래 뉴스 기사를 분석하여 반드시 한국어로만 작성하세요.
기사가 영어인 경우, 먼저 한국어로 완전히 번역한 뒤 분석을 진행하세요.

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

                # ★ 분석 결과 캐시 저장
                st.session_state.analyzed_results.append({"item": item, "analysis": analysis or ""})

                st.markdown(f"[기사 원문]({item['link']}) · {item['source']} · {item['date']}")
                st.markdown("---")
                st.session_state.news_context += f"\n{analysis}"
                parts.append(f"**{i+1}. {item['title']}**\n{analysis}")

            st.session_state.messages.append({"role": "assistant", "content": "\n\n".join(parts)})
            # ── 이용 횟수 +1 ──────────────────────────────────────
            _region_used = st.session_state.pop("pending_region", "한국")
            db_increment_usage(user_code, _region_used)

    # ── 분석 완료 후 저장/북마크 UI (session_state 기반으로 항상 렌더링) ──
    if st.session_state.get("analyzed_results"):
        for i, result in enumerate(st.session_state.analyzed_results):
            item     = result["item"]
            analysis = result["analysis"]
            act1, act2, act3, act4 = st.columns([2, 2, 1, 1])
            w = act1.text_input("단어", key=f"w_{i}_r")
            d = act2.text_input("정의", key=f"d_{i}_r")
            if act3.button("저장", key=f"b_{i}_r") and w:
                st.session_state.vocab_dict[w] = d
                db_save_vocab(st.session_state.current_user["code"], w, d)
                st.toast(f"'{w}' 저장 완료!")
            if act4.button("🔖", key=f"bm_{i}_r", help="북마크에 저장"):
                uc = st.session_state.current_user["code"]
                saved = db_save_bookmark(uc, {
                    "title": item["title"], "link": item["link"],
                    "source": item["source"], "date": item["date"],
                    "summary": (analysis or "")[:300]
                })
                if saved:
                    st.session_state.bookmarks = db_load_bookmarks(uc)
                    st.toast("🔖 북마크 저장!")
                else:
                    st.toast("이미 북마크된 기사입니다.")

        # ── 뒤로가기 버튼 ──────────────────────────────────────────
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        col_back, col_spacer = st.columns([1, 3])
        if col_back.button("← 새 뉴스 검색", key="btn_back_to_search"):
            st.session_state.analyzed_results    = []
            st.session_state.filtered_news_cache = []
            st.session_state.pending_news        = []
            st.session_state.news_context        = ""
            st.session_state.show_category_ui    = True
            st.rerun()

# ── 스마트 채팅: 의도 분류 + 파라미터 추출 파이프라인 ─────────
def classify_intent(user_input: str) -> dict:
    """
    1단계: 사용자 입력이 뉴스 요청인지 일반 질문인지 분류.
    퓨샷 예시로 추론 정확도 강화.
    """
    # ── 코드 레벨 1차 판단 (빠른 키워드 매칭) ──────────────────
    NEWS_KEYWORDS = [
        "뉴스","기사","소식","이슈","시황","동향","트렌드","현황","상황","근황",
        "최신","최근","요즘","요새","요즈음","오늘","어제","이번주","이번달",
        "보여줘","찾아줘","알려줘","알려봐","검색해","가져와","스크랩","정리해줘",
        "어때","어떻게 돼","어떻게 됐","궁금해","뭐 있어","뭐가 있","뭐 나왔",
        "관련","관련해서","관련된","분야","섹터","업계",
        "주가","증시","코스피","코스닥","나스닥","주식","환율","금리","물가","부동산",
        "아파트","전세","청약","반도체","엔비디아","삼성","애플","테슬라",
        "전쟁","분쟁","선거","정치","외교","대통령","국회","법안","정책",
        "AI","인공지능","챗GPT","클로드","로봇","자율주행","양자","우주","기후","환경"
    ]
    NON_NEWS_KEYWORDS = [
        "설명해줘","무슨 뜻","의미가","뭐야","이게 뭐","어떻게 하","방법","알려줘 어떻게",
        "아까","방금","위에서","앞에서","이전에","그 기사","그 뉴스","내용에서",
        "안녕","반가워","고마워","감사","수고","잘 부탁","처음 뵙","루키야",
        "점심","저녁","날씨","오늘 뭐","심심","재미있","웃긴","농담"
    ]
    lower_input = user_input.lower()
    # 명확히 뉴스 아닌 것 먼저 필터
    if any(kw in user_input for kw in NON_NEWS_KEYWORDS):
        # 단, 뉴스 키워드가 같이 있으면 뉴스 요청일 수 있음
        has_news_kw = any(kw in user_input for kw in NEWS_KEYWORDS[:20])
        if not has_news_kw:
            return {"is_news_request": False}
    # 명확히 뉴스인 것 바로 반환
    if any(kw in user_input for kw in NEWS_KEYWORDS):
        return {"is_news_request": True}

    # ── LLM 2차 판단 (애매한 경우만) ────────────────────────────
    prompt = f"""사용자 메시지가 뉴스/시사 검색 요청인지 판단하여 JSON만 출력하세요.

규칙:
- 새로운 정보나 현재 상황을 알고 싶어하면 true
- 이미 읽은 내용에 대한 질문이거나 일반 대화면 false

예시 (true — 뉴스 요청):
"반도체 최신 동향" → {{"is_news_request":true}}
"미국 금리 어떻게 됐어" → {{"is_news_request":true}}
"요즘 부동산 시장 상황" → {{"is_news_request":true}}
"글로벌 경제 위기 관련해서" → {{"is_news_request":true}}
"K팝 최근 소식" → {{"is_news_request":true}}
"주식 시장 지금 어때" → {{"is_news_request":true}}
"AI 스타트업 투자 현황" → {{"is_news_request":true}}
"북한 요즘 뭐해" → {{"is_news_request":true}}
"테슬라 근황" → {{"is_news_request":true}}
"유럽 에너지 위기 상황" → {{"is_news_request":true}}
"중국 경제 어떻게 되고 있어" → {{"is_news_request":true}}
"국내 증시 분위기" → {{"is_news_request":true}}

예시 (false — 일반 대화/질문):
"아까 기사에서 PER이 뭐야" → {{"is_news_request":false}}
"방금 본 뉴스 다시 설명해줘" → {{"is_news_request":false}}
"금리 인상이 주식에 미치는 영향" → {{"is_news_request":false}}
"안녕 루키" → {{"is_news_request":false}}
"위 내용 요약해줘" → {{"is_news_request":false}}
"그게 무슨 의미야" → {{"is_news_request":false}}
"ESG가 뭐야" → {{"is_news_request":false}}
"이전에 읽은 기사 기억해?" → {{"is_news_request":false}}

입력: "{user_input}"
JSON:"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            stream=False,
        )
        raw = response.choices[0].message.content.strip()
        if "</think>" in raw:
            raw = raw.split("</think>")[-1].strip()
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"is_news_request": False}


def extract_news_params(user_input: str) -> dict:
    """
    2단계: 뉴스 요청에서 카테고리·지역·기간·개수를 추출.
    코드 레벨 키워드 매핑 + 퓨샷 강화 LLM으로 정확도 극대화.
    """
    defaults = {"category": "글로벌 뉴스", "region": "한국", "days": 7, "count": 3}

    # ── 코드 레벨 1차 추출 (키워드 매핑) ────────────────────────
    CATEGORY_MAP = {
        "경제/증시": [
            "주가","증시","코스피","코스닥","나스닥","주식","환율","금리","물가",
            "인플레이션","경제","펀드","채권","IPO","상장","배당","투자","매출",
            "실적","무역","수출","수입","달러","엔화","원화","GDP","기준금리",
            "한국은행","M&A","인수합병","벤처","스타트업 투자","VC"
        ],
        "AI/미래기술": [
            "AI","인공지능","챗GPT","GPT","클로드","제미나이","LLM","반도체",
            "엔비디아","TSMC","삼성전자","SK하이닉스","자율주행","로봇","드론",
            "양자컴퓨터","메타버스","블록체인","NFT","핀테크","사이버보안","해킹",
            "딥러닝","머신러닝","빅데이터","클라우드","5G","6G","우주","위성"
        ],
        "정치/외교": [
            "대통령","국회","정치","선거","여당","야당","외교","대사","조약",
            "북한","김정은","트럼프","바이든","시진핑","푸틴","총리","장관",
            "청와대","정부","법안","헌법","검찰","법원","탄핵","정책","외무"
        ],
        "산업/부동산": [
            "부동산","아파트","전세","월세","청약","재건축","분양","건설","공사",
            "자동차","현대차","기아","테슬라","조선","철강","포스코","화학","석유화학",
            "유통","이커머스","쿠팡","네이버쇼핑","물류","항공","여행","관광","호텔"
        ],
        "글로벌 뉴스": [
            "미국","중국","일본","유럽","러시아","우크라이나","중동","이스라엘",
            "이란","사우디","인도","브라질","G7","G20","UN","NATO","IMF","세계은행",
            "전쟁","분쟁","테러","난민","국제","글로벌","해외","외국"
        ],
        "과학/환경": [
            "기후","환경","탄소","온난화","태양광","풍력","수소","원자력","핵융합",
            "우주","나사","스페이스X","로켓","위성","화성","달","노벨","과학",
            "바이오","헬스케어","신약","백신","전기차","배터리","ESS","ESG"
        ],
        "사회/이슈": [
            "교육","입시","수능","대학","취업","청년","저출생","고령화","인구",
            "노동","임금","최저임금","복지","의료","건강보험","사회","범죄","사건",
            "사고","재난","지진","홍수","화재","언론","미디어","젠더","다문화"
        ],
        "문화/라이프": [
            "K팝","아이돌","드라마","영화","OTT","넷플릭스","유튜브","게임","e스포츠",
            "스포츠","축구","야구","농구","올림픽","패션","뷰티","음식","맛집",
            "여행","캠핑","반려동물","웰니스","힐링","라이프스타일","소비","트렌드"
        ],
    }
    REGION_MAP = {
        "해외": ["미국","중국","일본","유럽","영국","러시아","인도","해외","외국",
                 "글로벌","international","overseas","abroad","us ","usa","uk "],
        "전체": ["전세계","전체","모두","국내외","한국과 해외","해외도","국내도"],
    }
    COUNT_MAP = {
        1: ["하나","1개","한 개","한개","하나만","1건","한 건"],
        2: ["둘","2개","두 개","두개","2건","두 건"],
        3: ["셋","3개","세 개","세개","3건"],
        4: ["넷","4개","네 개","네개","4건"],
        5: ["다섯","5개","다섯 개","다섯개","5건","최대"],
    }
    DAYS_MAP = {
        1:  ["오늘","방금","최신","방금 나온","지금 막","지금 바로","실시간"],
        3:  ["3일","사흘","최근 3일"],
        7:  ["이번 주","일주일","7일","한 주"],
        14: ["이번 달","한 달","14일","2주"],
    }

    result = dict(defaults)

    # 카테고리 매칭
    best_cat, best_score = defaults["category"], 0
    for cat, keywords in CATEGORY_MAP.items():
        score = sum(1 for kw in keywords if kw.lower() in user_input.lower())
        if score > best_score:
            best_score, best_cat = score, cat
    if best_score > 0:
        result["category"] = best_cat

    # 지역 매칭
    for region, keywords in REGION_MAP.items():
        if any(kw.lower() in user_input.lower() for kw in keywords):
            result["region"] = region
            break

    # 개수 매칭
    for count, keywords in COUNT_MAP.items():
        if any(kw in user_input for kw in keywords):
            result["count"] = count
            break

    # 기간 매칭
    for days, keywords in DAYS_MAP.items():
        if any(kw in user_input for kw in keywords):
            result["days"] = days
            break

    # 해외/전체면 최대 2개
    if result["region"] in ["해외", "전체"]:
        result["count"] = min(result["count"], 2)

    # 키워드 매칭으로 카테고리가 명확히 잡혔으면 LLM 스킵
    if best_score >= 2:
        return result

    # ── LLM 2차 추출 (키워드 매칭 불확실한 경우만) ──────────────
    prompt = f"""사용자 뉴스 요청에서 파라미터를 추출하여 JSON만 출력하세요.

카테고리 목록: 경제/증시, AI/미래기술, 정치/외교, 산업/부동산, 글로벌 뉴스, 과학/환경, 사회/이슈, 문화/라이프

지역: 한국(기본), 해외(외국/미국/영어권 언급시), 전체(둘다 원할때)
기간(days): 오늘/최신=1, 이번주=7(기본), 이번달=14
개수(count): 기본3, 해외/전체면 기본2, 최대5

퓨샷 예시:
"반도체 동향" → {{"category":"AI/미래기술","region":"한국","days":7,"count":3}}
"미국 연준 금리 결정" → {{"category":"경제/증시","region":"해외","days":7,"count":2}}
"오늘 부동산 소식" → {{"category":"산업/부동산","region":"한국","days":1,"count":3}}
"러시아 우크라이나 전쟁 최신" → {{"category":"글로벌 뉴스","region":"전체","days":1,"count":2}}
"K팝 아이돌 소식 3개" → {{"category":"문화/라이프","region":"한국","days":7,"count":3}}
"기후변화 국제 협약" → {{"category":"과학/환경","region":"전체","days":7,"count":2}}
"대통령 지지율" → {{"category":"정치/외교","region":"한국","days":7,"count":3}}
"취업 청년 실업 현황" → {{"category":"사회/이슈","region":"한국","days":7,"count":3}}
"삼성전자 실적 발표" → {{"category":"경제/증시","region":"한국","days":3,"count":3}}
"테슬라 자율주행 해외 기사" → {{"category":"AI/미래기술","region":"해외","days":7,"count":2}}
"중동 분쟁 2개만" → {{"category":"글로벌 뉴스","region":"해외","days":7,"count":2}}
"이번 주 코스피" → {{"category":"경제/증시","region":"한국","days":7,"count":3}}
"AI 반도체 엔비디아" → {{"category":"AI/미래기술","region":"전체","days":7,"count":2}}
"아파트 청약 경쟁률" → {{"category":"산업/부동산","region":"한국","days":7,"count":3}}
"노벨상 과학" → {{"category":"과학/환경","region":"전체","days":14,"count":2}}

현재 입력: "{user_input}"
JSON:"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            stream=False,
        )
        raw = response.choices[0].message.content.strip()
        if "</think>" in raw:
            raw = raw.split("</think>")[-1].strip()
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            valid_categories = list(CATEGORY_KEYWORDS.keys())
            if parsed.get("category") in valid_categories:
                result["category"] = parsed["category"]
            if parsed.get("region") in ["한국", "해외", "전체"]:
                result["region"] = parsed["region"]
            result["days"]  = max(1, min(14, int(parsed.get("days", result["days"]))))
            result["count"] = max(1, min(5, int(parsed.get("count", result["count"]))))
            if result["region"] in ["해외", "전체"]:
                result["count"] = min(result["count"], 2)
    except Exception:
        pass
    return result


def run_news_from_chat(params: dict):
    """파라미터로 뉴스 수집 후 채팅창에 바로 출력."""
    cat         = params["category"]
    cnt         = params["count"]
    days        = params["days"]
    region_mode = params["region"]

    region_label = {"한국": "🇰🇷 한국", "해외": "🌐 해외", "전체": "🗺️ 전체"}[region_mode]
    st.markdown(f"🔍 **[{cat}]** {region_label} 뉴스 {cnt}개를 찾고 있습니다... _(최근 {days}일)_")

    news_data = fetch_news(cat, cnt, days, region_mode)
    if not news_data:
        st.warning("검색 결과가 없습니다.")
        return "검색 결과가 없었습니다."

    parts = []
    for i, item in enumerate(news_data):
        st.markdown(f"<div class='report-title'>— {i+1}. {item['title']}</div>", unsafe_allow_html=True)
        if item["image"]: st.image(item["image"], width=700)
        prompt = f"""아래 뉴스 기사를 분석하여 반드시 한국어로만 작성하세요.
기사가 영어인 경우, 먼저 한국어로 완전히 번역한 뒤 분석을 진행하세요.

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

        # 단어 저장 UI + ② 북마크
        key_suffix = f"chat_{i}_{hash(item['title'])}"
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        w = c1.text_input("단어", key=f"cw_{key_suffix}")
        d = c2.text_input("정의", key=f"cd_{key_suffix}")
        if c3.button("저장", key=f"cb_{key_suffix}") and w:
            st.session_state.vocab_dict[w] = d
            db_save_vocab(user_code, w, d)
            st.toast(f"'{w}' 저장 완료!")
        if c4.button("🔖", key=f"cbm_{key_suffix}", help="북마크 저장"):
            saved = db_save_bookmark(user_code, {
                "title": item["title"], "link": item["link"],
                "source": item["source"], "date": item["date"],
                "summary": (analysis or "")[:300]
            })
            if saved:
                st.session_state.bookmarks = db_load_bookmarks(user_code)
                st.toast("🔖 북마크 저장!")
            else:
                st.toast("이미 북마크된 기사입니다.")

        st.markdown(f"[기사 원문]({item['link']}) · {item['source']} · {item['date']}")
        st.markdown("---")
        st.session_state.news_context += f"\n{analysis}"
        parts.append(f"**{i+1}. {item['title']}**\n{analysis}")

    return "\n\n".join(parts)


if user_input := st.chat_input("루키에게 무엇이든 물어보세요 — 뉴스 요청도 가능해요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant", avatar=ROOKIE_IMG):
        try:
            # ── 1단계: 의도 분류 ──
            intent = classify_intent(user_input)

            if intent.get("is_news_request"):
                # ── 2단계: 파라미터 추출 ──
                params = extract_news_params(user_input)
                # 뉴스 수집 및 출력
                result = run_news_from_chat(params)
                st.session_state.messages.append({"role": "assistant", "content": result})

                # 채팅 히스토리에도 뉴스 결과 추가 (이후 질문에 참조 가능)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": f"[{params['category']}] 뉴스 {params['count']}개를 정리해 드렸습니다."})

            else:
                # ── 일반 채팅 응답 ──
                if st.session_state.news_context and not st.session_state.chat_history:
                    st.session_state.chat_history.append({"role": "user", "content": f"[참고 스크랩 내용]\n{st.session_state.news_context}\n\n위 내용을 참고하여 답변해 주세요."})
                    st.session_state.chat_history.append({"role": "assistant", "content": "네, 스크랩된 내용을 참고하여 답변드리겠습니다."})

                res = stream_groq(user_input, history=st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": res})
                st.session_state.messages.append({"role": "assistant", "content": res})

            # 히스토리 최대 20턴 유지
            if len(st.session_state.chat_history) > 20:
                st.session_state.chat_history = st.session_state.chat_history[-20:]

        except Exception as e:
            st.error(f"오류: {e}")
