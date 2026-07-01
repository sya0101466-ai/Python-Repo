import streamlit as st
from datetime import datetime
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="다이어리 방명록 ⛵",
    page_icon="⛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 및 CSS 스타일
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    body {
        background: #FFFFFF;
    }
    .main {
        background: #FFFFFF;
    }
    .stApp {
        background: #FFFFFF;
    }
    
    .header-title {
        text-align: center;
        color: #0277BD;
        font-size: 2.8em;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(2, 119, 189, 0.2);
        margin: 30px 0;
        font-family: 'Noto Sans KR', sans-serif;
        letter-spacing: 1px;
    }
    
    .diary-container {
        background: #F5F5F5;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 20px rgba(2, 119, 189, 0.15);
        margin: 20px 0;
        border: 2px solid #E0E0E0;
    }
    
    .comment-box {
        background: #FFFFFF;
        border-left: 4px solid #4FC3F7;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(2, 119, 189, 0.1);
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .wave-container {
        position: relative;
        height: 100px;
        overflow: hidden;
        margin: 20px 0;
        background: linear-gradient(to right, #E3F2FD 0%, #BBDEFB 50%, #E3F2FD 100%);
        border-radius: 10px;
    }
    
    .wave {
        position: absolute;
        bottom: 0;
        width: 200%;
        height: 60px;
        background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg"><path d="M0,64 Q300,0 600,64 T1200,64 L1200,120 L0,120 Z" fill="%23FFB6D9" opacity="0.7"/><path d="M0,74 Q300,20 600,74 T1200,74 L1200,120 L0,120 Z" fill="%23FFC0D9" opacity="0.5"/></svg>') repeat-x;
        animation: wave-animation 10s linear infinite;
    }
    
    @keyframes wave-animation {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    
    .decorative-text {
        text-align: center;
        color: #0277BD;
        font-size: 1.2em;
        margin: 15px 0;
        font-weight: 600;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .stTextInput > label {
        font-family: 'Noto Sans KR', sans-serif !important;
        color: #0277BD !important;
        font-weight: 700 !important;
    }
    
    .stTextArea > label {
        font-family: 'Noto Sans KR', sans-serif !important;
        color: #0277BD !important;
        font-weight: 700 !important;
    }
    
    .stRadio > label {
        font-family: 'Noto Sans KR', sans-serif !important;
        color: #0277BD !important;
        font-weight: 700 !important;
    }
    
    .stButton > button {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #4FC3F7 0%, #0277BD 100%) !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(2, 119, 189, 0.2) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 16px rgba(2, 119, 189, 0.4) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Noto Sans KR', sans-serif !important;
        color: #0277BD !important;
        font-weight: 700 !important;
    }
    
    input, textarea {
        transition: all 0.3s ease !important;
    }
    
    input:focus, textarea:focus {
        transform: scale(1.01) !important;
        box-shadow: 0 0 20px rgba(2, 119, 189, 0.3) !important;
    }
    
    input:hover, textarea:hover {
        box-shadow: 0 0 15px rgba(2, 119, 189, 0.2) !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# 두둥대는 돌고래 이모지 및 드래그 기능
st.markdown("""
    <style>
        .floating-dolphin {
            position: fixed;
            font-size: 4em;
            cursor: grab;
            z-index: 10000;
            animation: float 3s ease-in-out infinite;
            user-select: none;
        }
        
        .floating-dolphin:active {
            cursor: grabbing;
            animation: none !important;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-25px); }
        }
    </style>
    
    <script>
        setTimeout(() => {
            const positions = [
                { x: '5%', y: '10%' },
                { x: '45%', y: '20%' },
                { x: '80%', y: '30%' },
                { x: '25%', y: '50%' },
                { x: '70%', y: '45%' }
            ];
            
            positions.forEach((pos, index) => {
                const dolphin = document.createElement('div');
                dolphin.textContent = '🐬';
                dolphin.className = 'floating-dolphin';
                dolphin.style.left = pos.x;
                dolphin.style.top = pos.y;
                dolphin.style.animationDelay = (index * 0.4) + 's';
                
                let isDragging = false;
                let offsetX = 0;
                let offsetY = 0;
                
                const onMouseDown = (e) => {
                    isDragging = true;
                    const rect = dolphin.getBoundingClientRect();
                    offsetX = e.clientX - rect.left;
                    offsetY = e.clientY - rect.top;
                    dolphin.style.animation = 'none';
                };
                
                const onMouseMove = (e) => {
                    if (isDragging) {
                        const x = e.clientX - offsetX;
                        const y = e.clientY - offsetY;
                        dolphin.style.left = x + 'px';
                        dolphin.style.top = y + 'px';
                    }
                };
                
                const onMouseUp = () => {
                    if (isDragging) {
                        isDragging = false;
                        dolphin.style.animation = 'float 3s ease-in-out infinite';
                        dolphin.style.animationDelay = (index * 0.4) + 's';
                    }
                };
                
                dolphin.addEventListener('mousedown', onMouseDown);
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
                
                document.body.appendChild(dolphin);
            });
        }, 500);
    </script>
""", unsafe_allow_html=True)

# 데이터 저장 경로
DATA_FILE = "diary_comments.json"

def load_comments():
    """저장된 댓글 불러오기"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_comments(comments):
    """댓글 저장하기"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

# 제목
st.markdown('<div class="header-title">⛵ 다이어리 방명록을 꾸며봐요 🐬 ⛵</div>', unsafe_allow_html=True)

# 파도 애니메이션
st.markdown("""
<div class="wave-container">
    <div class="wave"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="decorative-text">⛵ 배와 함께 비나는 단편한 승차 ⛵</div>', unsafe_allow_html=True)

# 마우스 추적 기능
st.markdown("""
    <div style="text-align: center; margin: 20px 0; padding: 20px; background: linear-gradient(135deg, #FFE0F0 0%, #E3F2FD 100%); border-radius: 15px; border: 2px solid #FFB6D9;">
        <p style="font-size: 1.3em; color: #0277BD; font-weight: 700; margin: 0; font-family: 'Noto Sans KR', sans-serif;">
            🐬 핑크 돌고래를 드래그하고 놀려보세요! 🐬
        </p>
        <p style="font-size: 0.95em; color: #FF1493; margin: 5px 0; font-weight: 600; font-family: 'Noto Sans KR', sans-serif;">
            💡 팁: 돌고래를 드래그하면 두둥대면서 따라다닙니다!
            아직 업데이트 중인 기능이니 조금만 기다려주세요! 🐬
        </p>
    </div>
""", unsafe_allow_html=True)

# 메인 다이어리 영역
st.markdown('<div class="diary-container">', unsafe_allow_html=True)

# 탭 나누기
tab1, tab2 = st.tabs(["🐬 방명록 남기기", "📖 모든 메시지 보기"])

with tab1:
    st.markdown("### 🐬 당신의 따뜻한 말씀을 남겨주세요")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name = st.text_input("💝 이름을 적어주세요", placeholder="예: 행복한 선원", key="name_input")
        message = st.text_area("💌 메시지를 남겨주세요", placeholder="예: 배 위에서 본 일몰이 정말 아름다웠어요. 이 순간을 영원히 기억하고 싶습니다.", height=120, key="msg_input")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            submit = st.button("🐬 메시지 등록", use_container_width=True, key="submit_btn")
        with col_btn2:
            st.write("")
    
    with col2:
        st.markdown("### 오늘의 기분")
        emotion = st.radio("어떤 기분이신가요?", ["☀️ 맑음", "⛅ 구름", "🌧️ 비", "❄️ 추움", "🌊 파도 있음"], key="emotion_select")
    
    if submit:
        if name and message:
            comments = load_comments()
            new_comment = {
                "name": name,
                "message": message,
                "emotion": emotion,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "emoji": "⛵"
            }
            comments.append(new_comment)
            save_comments(comments)
            st.success("🐬 메시지가 등록되었습니다! 감사합니다", icon="✅")
            st.balloons()
        else:
            st.warning("⚠️ 이름과 메시지를 모두 입력해주세요!", icon="🔔")

with tab2:
    st.markdown("### 📖 모든 메시지")
    
    comments = load_comments()
    
    if comments:
        # 최근 메시지부터 표시
        for idx, comment in enumerate(reversed(comments), 1):
            st.markdown(f"""
            <div class="comment-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 900; color: #0277BD; font-size: 1.2em; font-family: 'Noto Sans KR', sans-serif;">
                        🐬 {comment['name']} 🐬
                    </span>
                    <span style="color: #4FC3F7; font-size: 0.9em; font-weight: 700; font-family: 'Noto Sans KR', sans-serif;">{comment['date']}</span>
                </div>
                <div style="background: rgba(227, 242, 253, 0.5); padding: 12px; border-radius: 8px; margin: 10px 0; color: #333; font-family: 'Noto Sans KR', sans-serif;">
                    {comment['message']}
                </div>
                <div style="text-align: right; color: #0277BD; font-weight: 700; font-family: 'Noto Sans KR', sans-serif; font-size: 1em;">
                    {comment['emotion']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📝 아직 메시지가 없습니다. 첫 번째 메시지를 남겨보세요!")

st.markdown('</div>', unsafe_allow_html=True)

# 하단 장식
st.markdown("""
    <div style="text-align: center; margin-top: 40px; padding: 30px; color: #0277BD; font-size: 1.5em; font-weight: 700;">
        ⛵ 🌊 � 🌊 ⛵
        <br>
        <span style="font-size: 1.1em; font-family: 'Noto Sans KR', sans-serif; font-weight: 700;">돌고래와 함께 비나는 특별한 추억 기록 🐬</span>
    </div>
""", unsafe_allow_html=True)

# 사이드바 정보
with st.sidebar:
    st.markdown("### 🐬 다이어리 방명록 정보")
    st.write("""
    배와 돌고래와 함께 만드는 특별한 추억의 공간입니다.

    
    **팁:**
    - 🐬 돌고래를 클릭하고 드래그하세요!
    - ✨ 텍스트를 입력할 때 반짝이는 효과가 생겨요!
    - 돌고래는 두둥대면서 떠있습니다!
    - 자유롭게 메시지를 남겨보세요!
    """)
    
    st.markdown("---")
    total_comments = len(load_comments())
    st.metric("📊 총 메시지 수", total_comments)
    
    if st.button("🗑️ 모든 메시지 초기화", key="clear_btn"):
        if st.checkbox("정말 초기화하시겠어요?", key="confirm_clear"):
            save_comments([])
            st.success("모든 메시지가 삭제되었습니다.")
