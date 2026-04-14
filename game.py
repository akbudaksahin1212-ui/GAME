import streamlit as st
import google.generativeai as genai
import base64
import os

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="Forest Witch", layout="centered")

# API Anahtarı Kontrolü
try:
    # Streamlit Cloud'da secrets.toml dosyasını kullanır
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("Lütfen Streamlit Cloud Secrets veya lokal .streamlit/secrets.toml dosyasında GEMINI_API_KEY tanımlayın!")
    st.stop()
except Exception as e:
    st.error(f"API konfigürasyonu sırasında bir hata oluştu: {str(e)}")
    st.stop()

# --- 2. GÖRSEL İŞLEME (BASE64) ---
# Görselleri lokal klasörden Base64 formatında okur
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# image_30.png'deki dosya isimlerine göre asset'leri yüklüyoruz
bg_64 = get_base64("BG_1.png")
body_64 = get_base64("faceless_body.png")
face_64 = get_base64("normal_face.png")

# --- 3. PIXEL PERFECT CSS (Diyalog Kutusu Dahil) ---
# unsafe_allow_html=True parametresi bu CSS'in çalışmasını sağlar
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    html, body, [class*="st-"] {{
        font-family: 'VT323', monospace;
        font-size: 24px;
        image-rendering: pixelated; /* Piksellerin keskin kalmasını sağlar */
        background-color: #1a1c1a;
    }}

    .game-container {{
        position: relative;
        width: 100%;
        height: 520px; /* Arka plan görselinin yüksekliğine göre ayarlandı */
        background-image: url("data:image/png;base64,{bg_64}");
        background-size: cover;
        background-position: center;
        border: 6px solid #3d5a44; /* Orman yeşili çerçeve */
        overflow: hidden;
        margin-bottom: 10px;
    }}

    .layer {{
        position: absolute;
        bottom: 20%; /* Cadıyı patikanın üzerine yerleştirir */
        left: 50%;
        transform: translateX(-50%);
        width: 300px;
    }}

    /* RPG Diyalog Kutusu (Alt Kısma Sabit) */
    .dialogue-box {{
        position: absolute;
        bottom: 15px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        height: 120px;
        background-color: rgba(20, 35, 20, 0.95); /* Yarı şeffaf koyu yeşil */
        border: 4px solid #789d78; /* Açık yeşil çerçeve */
        padding: 15px;
        color: white;
        z-index: 100;
        box-shadow: 0 0 10px black; /* Hafif bir gölge */
    }}

    .witch-name {{
        color: #f1c40f; /* Sarı isim etiketi */
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 20px;
        text-transform: uppercase;
    }}

    /* Cadı Animasyonları */
    @keyframes float {{
        0% {{ transform: translate(-50%, 0px); }}
        50% {{ transform: translate(-50%, -10px); }}
        100% {{ transform: translate(-50%, 0px); }}
    }}

    .witch-animated {{
        animation: float 4s ease-in-out infinite;
    }}

    /* Asa Parlama Efekti */
    .staff-glow {{
        filter: drop-shadow(0 0 15px rgba(255, 223, 0, 0.8));
    }}
    </style>
    """, unsafe_allow_html=True) # <-- BU SATIR ÇOK ÖNEMLİ

# --- 4. SESSION STATE (Anlık metin hafızası) ---
if "current_text" not in st.session_state:
    st.session_state.current_text = "Hoş geldin küçük dostum... Bugün dükkanımda ne arıyorsun?"

# --- 5. AI ENGINE (Gemini API) ---
def get_witch_response(user_text):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    system_instruction = (
        "Sen Studio Ghibli dünyasından, neşeli ve çatlak bir doğa cadısısın. "
        "Müşterilerin orman hayvanları ve dertleri çok absürt. "
        "Cevapların maksimum 2 kısa cümle olsun. Bir pixel art RPG oyunundayız."
    )
    try:
        response = model.generate_content(f"{system_instruction}\n\nHayvan Dostun: {user_text}")
        return response.text
    except Exception as e:
        return f"Amanın! Kazan biraz fazla fokurdadı galiba... (Hata: {str(e)})"

# --- 6. UI RENDER (Görsel ve Diyalog Kutusu) ---
st.title("🌿 The Enchanted Potion Garden")

# Oyun Ekranı ve İçindeki Diyalog Kutusu
# Koddaki HTML'i Streamlit'in işlemesi için unsafe_allow_html=True kullanıyoruz.
st.markdown(f"""
    <div class="game-container">
        <img src="data:image/png;base64,{body_64}" class="layer witch-animated staff-glow">
        <img src="data:image/png;base64,{face_64}" class="layer witch-animated">
        
        <div class="dialogue-box">
            <div class="witch-name">Orman Cadısı</div>
            <div class="dialogue-text">{st.session_state.current_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True) # <-- BU SATIR ÇOK ÖNEMLİ

# Kullanıcı Girişi (Sayfanın en altında sabit durur)
prompt = st.chat_input("Derdini fısılda küçük dostum...")

if prompt:
    # 1. AI'dan cevap al
    new_response = get_witch_response(prompt)
    # 2. State'i güncelle (Eski mesaj silinir, yenisi gelir)
    st.session_state.current_text = new_response
    # 3. Ekranı yenile
    st.rerun()
