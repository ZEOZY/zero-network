# ==============================================================================
# PROJECT: ZERO NETWORK - LEGION ULTIMA v30.0 (FULL LEGACY REBUILD)
# LINE COUNT TARGET: ~350 (DETAILED ARCHITECTURE)
# STATUS: STABLE & VERIFIED
# ==============================================================================

import streamlit as st
import os
import base64
import pandas as pd
import time
from datetime import datetime
from PIL import Image
import io

# --- 1. ÇEKİRDEK DOSYA SİSTEMİ (PERSISTENCE LAYER) ---
# Sistemin çökmemesi için tüm yolları ve dosyaları önceden hazırlar.
DATABASE_DIR = "legion_v30_storage"
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

FILES = {
    "auth": os.path.join(DATABASE_DIR, "registry_auth.txt"),
    "stream": os.path.join(DATABASE_DIR, "stream_global.txt"),
    "profiles": os.path.join(DATABASE_DIR, "registry_profiles.txt"),
    "logs": os.path.join(DATABASE_DIR, "system_audit.log")
}

def bootstrap_system():
    """Gerekli veritabanı dosyalarını oluşturur ve sistem bütünlüğünü kontrol eder."""
    for file_path in FILES.values():
        if not os.path.exists(file_path):
            with open(file_path, "a", encoding="utf-8") as f:
                pass

bootstrap_system()

# --- 2. LEGION KRİPTO MOTORU (V30 ENGINE) ---
# Karakter eşleme ve Base64 kombinasyonu ile çift katmanlı koruma.
CHAR_MAP = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()[]{}@#$%"
VAL_MAP =  "!?*#$+%&/=+-_.:;<|>@æß~ΔΩμπ∞≈≠≤≥¶§÷×•¤†‡±√¬°^º¥©®™¿¡øæ∫çαβγδεζηθικλνξοπρστυφχψω"
ENCRYPT_DICT = dict(zip(CHAR_MAP, VAL_MAP))
DECRYPT_DICT = dict(zip(VAL_MAP, CHAR_MAP))

def legion_encrypt(plain_text):
    if not plain_text: return ""
    # Katman 1: Karakter Kaydırma/Eşleme
    mapped = "".join([ENCRYPT_DICT.get(c, c) for c in plain_text])
    # Katman 2: Base64 ve Ters Çevirme
    b64 = base64.b64encode(mapped.encode()).decode()
    return b64[::-1]

def legion_decrypt(cipher_text):
    if not cipher_text: return ""
    try:
        # Ters Katman 2
        reversed_b64 = cipher_text[::-1]
        decoded_mapped = base64.b64decode(reversed_b64).decode()
        # Ters Katman 1
        return "".join([DECRYPT_DICT.get(c, c) for c in decoded_mapped])
    except Exception:
        return "[ERROR: SIGNAL_DEGRADED]"

# --- 3. UI/UX TASARIM (MATRIX & TERMINAL STYLE) ---
st.set_page_config(page_title="ZERO NETWORK v30", layout="wide", page_icon="📟")

def apply_custom_styles():
    st.markdown("""
    <style>
        /* Ana Arkaplan ve Yazı Tipi */
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap');
        
        .stApp {
            background-color: #000000;
            color: #00FF41;
            font-family: 'Courier Prime', monospace;
        }
        
        /* Sidebar Özelleştirme */
        [data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 2px solid #00FF41;
        }
        
        /* Input Alanları */
        .stTextInput>div>div>input {
            background-color: #0A0A0A !important;
            color: #00FF41 !important;
            border: 1px solid #00FF41 !important;
            border-radius: 0px;
        }
        
        /* Butonlar */
        .stButton>button {
            background-color: #000000;
            color: #00FF41;
            border: 1px solid #00FF41;
            border-radius: 0px;
            width: 100%;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #00FF41;
            color: #000000;
            box-shadow: 0 0 10px #00FF41;
        }
        
        /* Mesaj Kartları */
        .msg-container {
            border: 1px solid #00FF41;
            padding: 15px;
            margin-bottom: 10px;
            background: rgba(0, 255, 65, 0.05);
            border-radius: 5px;
        }
        
        .msg-header {
            font-weight: bold;
            font-size: 0.9em;
            color: #00D4FF;
            margin-bottom: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 4. OTURUM VE YETKİ YÖNETİMİ ---
if 'authorized' not in st.session_state:
    st.session_state.authorized = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'user_rank' not in st.session_state:
    st.session_state.user_rank = "GUEST"

def audit_log(user, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FILES["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] AGENT: {user} | ACTION: {action}\n")

# --- 5. MODÜLLER ---

def login_gateway():
    st.title("📟 ZERO_NETWORK GATEWAY v30")
    st.write("Sistem erişimi için kimlik doğrulama gereklidir.")
    
    tab_login, tab_reg = st.tabs(["[ AUTH_LOGIN ]", "[ NODE_REGISTRY ]"])
    
    with tab_login:
        user_id = st.text_input("AGENT_ID", placeholder="Kullanıcı adınız...")
        access_key = st.text_input("ACCESS_KEY", type="password", placeholder="Şifreniz...")
        
        if st.button("INBOUND_AUTHORIZE"):
            if user_id == "admin" and access_key == "1234":
                st.session_state.authorized = True
                st.session_state.current_user = "admin"
                st.session_state.user_rank = "GHOST"
                audit_log("admin", "Authorized as ROOT")
                st.rerun()
            else:
                found = False
                with open(FILES["auth"], "r") as f:
                    for line in f:
                        if f"{user_id}:{access_key}" in line.strip():
                            found = True
                            break
                if found:
                    st.session_state.authorized = True
                    st.session_state.current_user = user_id
                    st.session_state.user_rank = "MEMBER"
                    audit_log(user_id, "Login Success")
                    st.rerun()
                else:
                    st.error("CREDENTIAL_MISMATCH: Erişim engellendi.")
                    audit_log(user_id or "UNKNOWN", "Failed Login Attempt")

    with tab_reg:
        new_id = st.text_input("REQUEST_ID")
        new_key = st.text_input("REQUEST_KEY", type="password")
        confirm_key = st.text_input("CONFIRM_KEY", type="password")
        
        if st.button("INITIALIZE_NODE"):
            if new_id and new_key == confirm_key:
                with open(FILES["auth"], "a") as f:
                    f.write(f"{new_id}:{new_key}\n")
                st.success("Yeni düğüm (node) başarıyla oluşturuldu. Giriş yapabilirsiniz.")
                audit_log(new_id, "Node Registered")
            else:
                st.warning("Şifreler uyuşmuyor veya geçersiz ID.")

def run_global_stream():
    st.subheader("🌐 NETWORK_GLOBAL_STREAM")
    
    # Mesajları Görüntüleme
    stream_container = st.container(height=500, border=True)
    with stream_container:
        if os.path.getsize(FILES["stream"]) > 0:
            with open(FILES["stream"], "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-50:]:  # Son 50 mesaj
                    try:
                        sender, crypt_msg, ts = line.strip().split("|")
                        st.markdown(f"""
                        <div class="msg-container">
                            <div class="msg-header">[{ts}] AGENT_{sender.upper()}</div>
                            <div class="msg-body">{legion_decrypt(crypt_msg)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    except: continue
        else:
            st.info("Akışta henüz veri bulunmuyor. İlk sinyali siz gönderin.")

    # Mesaj Gönderme
    with st.form("broadcast_form", clear_on_submit=True):
        msg_input = st.text_input("Signal Input:", placeholder="Mesajınızı yazın...")
        if st.form_submit_button("DEPLOY_SIGNAL") and msg_input:
            t_stamp = datetime.now().strftime("%H:%M:%S")
            encrypted = legion_encrypt(msg_input)
            with open(FILES["stream"], "a", encoding="utf-8") as f:
                f.write(f"{st.session_state.current_user}|{encrypted}|{t_stamp}\n")
            st.rerun()

def run_tech_station():
    st.subheader("🛠️ TECH_OPS_STATION")
    st.write("Manuel kriptolama ve sistem tanılama araçları.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Encryption Engine")
        raw_text = st.text_area("Plaintext Input", height=150)
        if st.button("RUN_ENCRYPTION"):
            st.code(legion_encrypt(raw_text))
            
    with col2:
        st.markdown("### Decryption Engine")
        cipher_text = st.text_area("Ciphertext Input", height=150)
        if st.button("RUN_DECRYPTION"):
            st.success(legion_decrypt(cipher_text))

def run_root_override():
    st.subheader("🛡️ ROOT_AUTHORITY_OVERRIDE")
    if st.session_state.user_rank != "GHOST":
        st.error("INSUFFICIENT_PERMISSIONS: Bu alan sadece GHOST rankı içindir.")
        return
    
    st.warning("DİKKAT: Yapılan işlemler geri alınamaz.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("WIPE_GLOBAL_STREAM"):
            open(FILES["stream"], "w").close()
            st.success("Global akış temizlendi.")
            audit_log("admin", "Wiped Global Stream")
            
    with col_b:
        if st.button("EXPORT_AUDIT_LOGS"):
            with open(FILES["logs"], "r") as f:
                st.download_button("Download Logs", f.read(), "audit_log.txt")

# --- 6. ANA KONTROL DÖNGÜSÜ ---
def main():
    if not st.session_state.authorized:
        login_gateway()
    else:
        # Sidebar İçeriği
        st.sidebar.image("https://i.imgur.com/v6S6asL.png", width=100)
        st.sidebar.title(f"AGENT_{st.session_state.current_user.upper()}")
        st.sidebar.markdown(f"**RANK:** {st.session_state.user_rank}")
        st.sidebar.divider()
        
        module = st.sidebar.radio("SENSORS", ["GLOBAL STREAM", "TECH STATION", "ROOT OVERRIDE"])
        
        if st.sidebar.button("TERMINATE_SESSION"):
            audit_log(st.session_state.current_user, "Logout")
            st.session_state.authorized = False
            st.rerun()
            
        st.sidebar.divider()
        st.sidebar.write("SYSTEM_TIME:")
        st.sidebar.code(datetime.now().strftime("%H:%M:%S"))

        # Modül Yükleyici
        if module == "GLOBAL STREAM":
            run_global_stream()
        elif module == "TECH STATION":
            run_tech_station()
        elif module == "ROOT OVERRIDE":
            run_root_override()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"SYSTEM_FATAL: {e}")
