import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURATION & SECRETS SETUP ---
st.set_page_config(page_title="Forest Witch Potion Shop", layout="centered")

# Streamlit Secrets'tan API anahtarını çekme
# Not: Lokal çalışırken projenin ana dizininde .streamlit/secrets.toml dosyası oluşturmalısın
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("Lütfen .streamlit/secrets.toml dosyasında 'GEMINI_API_KEY' tanımlayın!")
    st.stop()

# --- 2. ASSETS (GitHub Raw Linklerini Buraya Yapıştır) ---
# Önemli: Linklerin 'raw.githubusercontent.com' ile başladığından emin ol!
BG_URL = "https://raw.githubusercontent.com/KULLANICI/REPO/main/BG_1.png"
BODY_URL = "https://raw.githubusercontent.com/KULLANICI/REPO/main/faceless_body.png"
FACE_NORMAL = "https://raw.githubusercontent.com/KULLANICI/REPO/main/normal_face.png"

# --- 3. PIXEL PERFECT CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Genel Pixel Art Ayarları */
    html, body, [class*="st-"] {{
        font-family: 'VT323', monospace;
        font-size: 22px;
        image-rendering: pixelated;
        image-rendering: -moz-crisp-edges;
        image-rendering: crisp-edges;
    }}

    /* Oyun Ekranı Kutusu */
    .game-container {{
        position: relative;
        width: 100%;
        height: 450px;
        background-image: url('{BG_URL}');
        background-size: cover;
        background-position: center;
        border: 4px solid #3d5a44;
        overflow: hidden;
    }}

    /* Cadı Katmanları */
    .layer {{
        position: absolute;
        bottom: 10%;
        left: 15%;
        width: 280px;
    }}

    /* Floating Animation (Nefes Alma) */
    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
        100% {{ transform: translateY(0px); }}
    }}

    .witch-animated {{
        animation: float 4s ease-in-out infinite;
    }}

    /* Asa Parlama Efekti */
    .staff-glow {{
        filter: drop-shadow(0 0 12px rgba(255, 223, 0, 0.7));
    }}

    /* Chat Kutusu Stili */
    .stChatMessage {{
        background-color: rgba(25, 35, 25, 0.9) !important;
        border-radius: 0px !important;
        border-left: 5px solid #6b8e23 !important;
        color: #f0f0f0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATE (Hafıza) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "witch_face" not in st.session_state:
    st.session_state.witch_face = FACE_NORMAL

# --- 5. AI ENGINE (Gemini) ---
def get_witch_response(user_text):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # Cadı'nın Karakter Tanımı (System Instruction)
    system_instruction = (
        "Sen bir Ghibli filmi cadısısın. Nazik, neşeli ama biraz da çatlak bir karakterin var. "
        "Müşterilerin orman hayvanları ve dertleri çok absürt. "
        "Örneğin bir sincap 'palamutlarımın tadı brokoliye döndü' diyebilir. "
        "Onlara bahçendeki hayali bitkilerle (Giggle-Spore, Static-Fern, Whistling Hemlock) "
        "komik çözümler öner. Kısa, büyülü ve pixel-art RPG oyununa uygun konuş."
    )
    
    # Geçmişi de dahil ederek konuşmayı sürdür
    chat = model.start_chat(history=[])
    full_prompt = f"{system_instruction}\n\nKullanıcı (Hayvan): {user_text}"
    
    try:
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"Amanın! Kazan patladı galiba, bir hata oluştu: {str(e)}"

# --- 6. UI RENDER (Görsel Alan) ---
st.title("🌿 İksir Bahçesi: Doğa Cadısı")

# Oyun Ekranı: Katmanlar Üst Üste
st.markdown(f"""
    <div class="game-container">
        <img src="{BODY_URL}" class="layer witch-animated staff-glow">
        <img src="{st.session_state.witch_face}" class="layer witch-animated">
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# Sohbet Geçmişi
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Derdini fısılda küçük dostum..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Cadı'nın Yanıtı
    with st.chat_message("assistant"):
        with st.spinner("İksiri karıştırıyorum..."):
            response = get_witch_response(prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
