import streamlit as st
import google.generativeai as genai
import base64
import os

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="Forest Witch Potion Shop", layout="centered")

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

# Görselleri Base64'e çeviriyoruz
bg_64 = get_base64("BG_1.png")
body_64 = get_base64("faceless_body.png")
face_64 = get_base64("normal_face.png")

# --- 3. PIXEL PERFECT CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    html, body, [class*="st-"] {{
        font-family: 'VT323', monospace;
        font-size: 22px;
        image-rendering: pixelated;
    }}

    .game-container {{
        position: relative;
        width: 100%;
        height: 500px;
        background-image: url("data:image/png;base64,{bg_64}");
        background-size: cover;
        background-position: center;
        border: 4px solid #3d5a44;
        overflow: hidden;
    }}

    .layer {{
        position: absolute;
        bottom: 5%;
        left: 50%;
        transform: translateX(-50%);
        width: 320px;
    }}

    /* Floating & Glow Animations */
    @keyframes float {{
        0% {{ transform: translate(-50%, 0px); }}
        50% {{ transform: translate(-50%, -10px); }}
        100% {{ transform: translate(-50%, 0px); }}
    }}

    .witch-animated {{
        animation: float 4s ease-in-out infinite;
    }}

    .staff-glow {{
        filter: drop-shadow(0 0 15px rgba(255, 223, 0, 0.8));
    }}

    .stChatMessage {{
        background-color: rgba(20, 35, 20, 0.9) !important;
        border-radius: 0px !important;
        border-left: 5px solid #6b8e23 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. AI ENGINE (Gemini) ---
def get_witch_response(user_text):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    system_instruction = (
        "Sen neşeli ve biraz çatlak bir doğa cadısısın. Müşterilerin orman hayvanları "
        "ve dertleri çok absürt. Onlara bahçendeki hayali bitkilerle komik çözümler öner. "
        "Kısa ve pixel-art bir RPG'ye uygun konuş."
    )
    chat = model.start_chat(history=[])
    try:
        response = chat.send_message(f"{system_instruction}\n\nHayvan Dostun: {user_text}")
        return response.text
    except:
        return "Oh canım, kazanı karıştırırken bir şeyler ters gitti!"

# --- 6. UI RENDER ---
st.title("🌿 İksir Bahçesi: Doğa Cadısı")

# Oyun Ekranı
st.markdown(f"""
    <div class="game-container">
        <img src="data:image/png;base64,{body_64}" class="layer witch-animated staff-glow">
        <img src="data:image/png;base64,{face_64}" class="layer witch-animated">
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# Chat Akışı
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Derdini fısılda küçük dostum..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("İksiri hazırlıyorum..."):
            response = get_witch_response(prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
