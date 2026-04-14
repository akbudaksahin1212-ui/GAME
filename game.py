import streamlit as st
import google.generativeai as genai
import base64
import os

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="Forest Witch", layout="centered")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Lütfen .streamlit/secrets.toml dosyasına GEMINI_API_KEY ekleyin!")
    st.stop()

# --- 2. GÖRSEL İŞLEME (BASE64) ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

bg_64 = get_base64("BG_1.png")
body_64 = get_base64("faceless_body.png")
face_64 = get_base64("normal_face.png")

# --- 3. PIXEL PERFECT CSS (Diyalog Kutusu İçeride) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    html, body, [class*="st-"] {{
        font-family: 'VT323', monospace;
        font-size: 24px;
        image-rendering: pixelated;
        background-color: #1a1c1a;
    }}

    .game-container {{
        position: relative;
        width: 100%;
        height: 520px;
        background-image: url("data:image/png;base64,{bg_64}");
        background-size: cover;
        background-position: center;
        border: 6px solid #3d5a44;
        overflow: hidden;
    }}

    .layer {{
        position: absolute;
        bottom: 20%;
        left: 50%;
        transform: translateX(-50%);
        width: 300px;
    }}

    /* RPG Diyalog Kutusu (Alt Kısma Sabit) */
    .dialogue-box {{
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        height: 120px;
        background-color: rgba(20, 35, 20, 0.95);
        border: 4px solid #789d78;
        padding: 15px;
        color: white;
        z-index: 100;
        box-shadow: 0 0 10px black;
    }}

    .witch-name {{
        color: #f1c40f;
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 20px;
        text-transform: uppercase;
    }}

    @keyframes float {{
        0% {{ transform: translate(-50%, 0px); }}
        50% {{ transform: translate(-50%, -10px); }}
        100% {{ transform: translate(-50%, 0px); }}
    }}

    .witch-animated {{ animation: float 4s ease-in-out infinite; }}
    .staff-glow {{ filter: drop-shadow(0 0 15px rgba(255, 223, 0, 0.8)); }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATE (Sadece anlık metin) ---
if "current_text" not in st.session_state:
    st.session_state.current_text = "Hoş geldin küçük dostum... Bugün dükkanımda ne arıyorsun?"

# --- 5. AI ENGINE ---
def get_witch_response(user_text):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    system_instruction = (
        "Sen neşeli ve çatlak bir doğa cadısısın. Müşterilerin hayvanlar ve dertleri absürt. "
        "Cevapların maksimum 2 kısa cümle olsun. Bir RPG oyunundayız."
    )
    try:
        response = model.generate_content(f"{system_instruction}\n\nHayvan: {user_text}")
        return response.text
    except:
        return "Ah, iksir kazanım biraz fokurdayamadı..."

# --- 6. UI RENDER ---
st.title("🌿 The Enchanted Potion Garden")

# Oyun Ekranı ve İçindeki Diyalog Kutusu
st.markdown(f"""
    <div class="game-container">
        <img src="data:image/png;base64,{body_64}" class="layer witch-animated staff-glow">
        <img src="data:image/png;base64,{face_64}" class="layer witch-animated">
        
        <div class="dialogue-box">
            <div class="witch-name">Orman Cadısı</div>
            <div class="dialogue-text">{st.session_state.current_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# İnput alanı en altta
prompt = st.chat_input("Derdini fısılda...")

if prompt:
    # 1. AI'dan cevap al
    new_response = get_witch_response(prompt)
    # 2. State'i güncelle (Eski mesaj silinmiş olur)
    st.session_state.current_text = new_response
    # 3. Ekranı yenile
    st.rerun()
