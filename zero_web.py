# ==============================================================================
# PROJECT: ZERO NETWORK - LEGION ULTIMA v50.6 (ULTRA STABLE & EXPANDED)
# LINE COUNT TARGET: 580+ FUNCTIONAL LINES
# AUTHOR: LEGION CORE AI
# ==============================================================================

import streamlit as st
import os
import numpy as np
import pandas as pd
import io
import time
import random
import base64
import json
import hashlib
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# ------------------------------------------------------------------------------
# SECTION 1: SYSTEM FILE SYSTEM & DIRECTORY ARCHITECTURE
# ------------------------------------------------------------------------------
def bootstrap_system():
    """Sistemin temel dosya yapısını ve veritabanlarını hazırlar."""
    base = "legion_data_core"
    sub_dirs = ["logs", "vault", "media", "nodes"]
    
    if not os.path.exists(base):
        os.makedirs(base)
    
    for sd in sub_dirs:
        p = os.path.join(base, sd)
        if not os.path.exists(p):
            os.makedirs(p)
            
    return base

CORE_PATH = bootstrap_system()

def generate_db_map():
    """Tüm sistem veritabanlarının yollarını haritalar."""
    return {
        "auth": os.path.join(CORE_PATH, "registry_auth.zero"),
        "global": os.path.join(CORE_PATH, "stream_global.zero"),
        "private": os.path.join(CORE_PATH, "stream_private.zero"),
        "profiles": os.path.join(CORE_PATH, "registry_profiles.zero"),
        "audit": os.path.join(CORE_PATH, "system_audit.log"),
        "intel": os.path.join(CORE_PATH, "intel_broadcast.zero"),
        "config": os.path.join(CORE_PATH, "sys_config.json"),
        "blacklist": os.path.join(CORE_PATH, "blacklisted_nodes.zero")
    }

DB = generate_db_map()

def sync_databases():
    """Eksik dosyaları oluşturur ve sistem bütünlüğünü sağlar."""
    for key, path in DB.items():
        if not os.path.exists(path):
            if path.endswith(".json"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"version": "50.6", "status": "active"}, f)
            else:
                with open(path, "a", encoding="utf-8") as f:
                    pass

sync_databases()

# ------------------------------------------------------------------------------
# SECTION 2: ADVANCED SECURITY & ENCRYPTION ENGINE (A.S.E.E)
# ------------------------------------------------------------------------------
class LegionCrypto:
    """Sistem genelindeki tüm mesajlaşma ve veri saklama kriptografisini yönetir."""
    def __init__(self):
        self.k = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()[]{}@#$%"
        self.v = "!?*#$+%&/=+-_.:;<|>@æß~ΔΩμπ∞≈≠≤≥¶§÷×•¤†‡±√¬°^º¥©®™¿¡øæ∫çαβγδεζηθικλνξοπρστυφχψω"
        self.e_map = dict(zip(self.k, self.v))
        self.d_map = dict(zip(self.v, self.k))

    def encrypt_signal(self, data):
        if not data: return ""
        # Phase 1: Substitution
        sub = "".join([self.e_map.get(c, c) for c in data])
        # Phase 2: Base64 Obfuscation
        b64 = base64.b64encode(sub.encode("utf-8")).decode("utf-8")
        # Phase 3: Bit Reverse
        return b64[::-1]

    def decrypt_signal(self, data):
        if not data: return ""
        try:
            # Phase 1: Reverse Bit
            rev = data[::-1]
            # Phase 2: Base64 Decode
            dec_b64 = base64.b64decode(rev).decode("utf-8")
            # Phase 3: Inverse Substitution
            return "".join([self.d_map.get(c, c) for c in dec_b64])
        except Exception:
            return "[DECRYPTION_FAILED_INTEGRITY_COMPROMISED]"

    def hash_key(self, key):
        return hashlib.sha256(key.encode()).hexdigest()

crypto = LegionCrypto()

# ------------------------------------------------------------------------------
# SECTION 3: IMAGE STEGANOGRAPHY & LSB MASKING MODULE
# ------------------------------------------------------------------------------
def apply_lsb_mask(input_img, secret_text):
    """Görüntü içerisine LSB yöntemiyle veri gizler."""
    try:
        img = input_img.convert("RGB")
        encoded_text = secret_text + "###END###"
        binary_msg = ''.join([format(ord(i), '08b') for i in encoded_text])
        
        pixels = np.array(img)
        flat_pixels = pixels.flatten()
        
        if len(binary_msg) > len(flat_pixels):
            return None, "Data too large for this image."
            
        for i in range(len(binary_msg)):
            flat_pixels[i] = (flat_pixels[i] & ~1) | int(binary_msg[i])
            
        new_pixels = flat_pixels.reshape(pixels.shape)
        masked_img = Image.fromarray(new_pixels.astype('uint8'), 'RGB')
        
        # Add visual noise for obfuscation
        draw = ImageDraw.Draw(masked_img)
        for _ in range(15):
            x, y = random.randint(0, img.width-10), random.randint(0, img.height-10)
            draw.point((x, y), fill=(random.randint(0,255), 0, 0))
            
        return masked_img, "SUCCESS"
    except Exception as e:
        return None, str(e)

def extract_lsb_mask(input_img):
    """Gizlenmiş veriyi görüntüden çıkarır."""
    try:
        img = input_img.convert("RGB")
        pixels = np.array(img)
        flat_pixels = pixels.flatten()
        
        bits = [str(flat_pixels[i] & 1) for i in range(len(flat_pixels))]
        byte_chunks = [bits[i:i+8] for i in range(0, len(bits), 8)]
        
        decoded_chars = []
        for byte in byte_chunks:
            char = chr(int("".join(byte), 2))
            decoded_chars.append(char)
            if "".join(decoded_chars).endswith("###END###"):
                break
                
        full_string = "".join(decoded_chars)
        return full_string.replace("###END###", "") if "###END###" in full_string else "NO_CARRIER"
    except Exception:
        return "READ_ERROR"

# ------------------------------------------------------------------------------
# SECTION 4: AGENT PROFILE & RANKING SYSTEM
# ------------------------------------------------------------------------------
RANK_LEVELS = {
    "MEMBER": {"lvl": 1, "color": "#00FF41", "access": ["global", "tech"]},
    "SHADOW": {"lvl": 2, "color": "#BC13FE", "access": ["global", "private", "tech", "mask"]},
    "ELITE":  {"lvl": 3, "color": "#00D4FF", "access": ["global", "private", "tech", "mask", "vault"]},
    "GHOST":  {"lvl": 4, "color": "#FF3131", "access": ["all"]}
}

def get_agent_data(username):
    """Ajan bilgilerini veritabanından çeker."""
    default = {
        "name": username, 
        "rank": "GHOST" if username == "admin" else "MEMBER",
        "bio": "SYSTEM_UNIT", 
        "avatar": "https://i.imgur.com/v6S6asL.png",
        "status": "ACTIVE"
    }
    
    if os.path.exists(DB["profiles"]):
        with open(DB["profiles"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{username}|"):
                    p = line.strip().split("|")
                    if len(p) >= 5:
                        return {"name": p[0], "rank": p[1], "bio": p[2], "avatar": p[3], "status": p[4]}
    return default

def save_agent_data(name, rank, bio, avatar, status="ACTIVE"):
    """Ajan bilgilerini günceller."""
    lines = []
    found = False
    if os.path.exists(DB["profiles"]):
        with open(DB["profiles"], "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    with open(DB["profiles"], "w", encoding="utf-8") as f:
        for l in lines:
            if l.startswith(f"{name}|"):
                f.write(f"{name}|{rank}|{bio}|{avatar}|{status}\n")
                found = True
            else:
                f.write(l)
        if not found:
            f.write(f"{name}|{rank}|{bio}|{avatar}|{status}\n")

# ------------------------------------------------------------------------------
# SECTION 5: LOGGING & AUDIT PROTOCOLS
# ------------------------------------------------------------------------------
def system_log(agent, action):
    """Sistem olaylarını kayıt altına alır."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] AGENT_{agent.upper()} >> {action}\n"
    with open(DB["audit"], "a", encoding="utf-8") as f:
        f.write(entry)

def get_recent_logs(n=50):
    """Son kayıtları okur."""
    if not os.path.exists(DB["audit"]): return []
    with open(DB["audit"], "r", encoding="utf-8") as f:
        return f.readlines()[-n:]

# ------------------------------------------------------------------------------
# SECTION 6: STREAMLIT INTERFACE ENGINE
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ZERO LEGION - ULTIMA v50.6",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Legion Theme
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #00FF41; }
    .stTextInput>div>div>input { background-color: #1A1C24; color: #00FF41; border: 1px solid #00FF41; }
    .stButton>button { width: 100%; background-color: #1A1C24; color: #00FF41; border: 1px solid #00FF41; }
    .stButton>button:hover { background-color: #00FF41; color: #0E1117; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'auth_state' not in st.session_state:
    st.session_state.update({
        'auth_state': False,
        'user_id': '',
        'rank': 'MEMBER',
        'terminal_buffer': [],
        'last_sync': datetime.now()
    })

def write_terminal(text):
    t = datetime.now().strftime("%H:%M:%S")
    st.session_state.terminal_buffer.append(f"[{t}] > {text}")
    if len(st.session_state.terminal_buffer) > 12:
        st.session_state.terminal_buffer.pop(0)

# ------------------------------------------------------------------------------
# SECTION 7: CORE MODULES (UI)
# ------------------------------------------------------------------------------

def module_global_chat():
    st.subheader("🌐 GLOBAL BROADCAST STREAM")
    
    # Broadcast Area
    if os.path.exists(DB["intel"]):
        with open(DB["intel"], "r", encoding="utf-8") as f:
            intel_msg = f.read().strip()
            if intel_msg:
                st.info(f"⚡ INTEL: {intel_msg}")

    # Message Display
    chat_container = st.container(height=450, border=True)
    with chat_container:
        if os.path.exists(DB["global"]):
            with open(DB["global"], "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) >= 3:
                        sender, crypt_msg, ts = parts[0], parts[1], parts[2]
                        real_msg = crypto.decrypt_signal(crypt_msg)
                        st.markdown(f"**[{ts}] {sender}:** {real_msg}")

    # Input Area
    with st.form("global_input", clear_on_submit=True):
        col1, col2 = st.columns([0.85, 0.15])
        msg = col1.text_input("Enter Signal...", label_visibility="collapsed")
        if col2.form_submit_button("SEND") and msg:
            ts = datetime.now().strftime("%H:%M")
            encrypted = crypto.encrypt_signal(msg)
            with open(DB["global"], "a", encoding="utf-8") as f:
                f.write(f"{st.session_state.user_id}|{encrypted}|{ts}\n")
            system_log(st.session_state.user_id, "Sent Global Signal")
            st.rerun()

def module_private_node():
    st.subheader("🔒 SECURE PRIVATE NODE")
    
    target_agent = st.text_input("Target Agent ID:", placeholder="Enter ID...")
    
    if target_agent:
        p_chat = st.container(height=350, border=True)
        with p_chat:
            if os.path.exists(DB["private"]):
                with open(DB["private"], "r", encoding="utf-8") as f:
                    for line in f:
                        p = line.strip().split("|")
                        if len(p) == 4:
                            s, r, m, t = p[0], p[1], p[2], p[3]
                            if (s == st.session_state.user_id and r == target_agent) or \
                               (s == target_agent and r == st.session_state.user_id):
                                st.markdown(f"`{t}` **{s}:** {crypto.decrypt_signal(m)}")
        
        with st.form("priv_form", clear_on_submit=True):
            p_msg = st.text_input("Private Message:")
            if st.form_submit_button("LOCK & SEND") and p_msg:
                t_now = datetime.now().strftime("%H:%M")
                enc_p = crypto.encrypt_signal(p_msg)
                with open(DB["private"], "a", encoding="utf-8") as f:
                    f.write(f"{st.session_state.user_id}|{target_agent}|{enc_p}|{t_now}\n")
                st.rerun()
    else:
        st.warning("Establish a connection by entering a Target Agent ID.")

def module_masking_station():
    st.subheader("🎭 SHADOW MASKING STATION")
    
    if RANK_LEVELS[st.session_state.rank]['lvl'] < 2:
        st.error("INSUFFICIENT CLEARANCE: REQUIRES SHADOW RANK OR HIGHER.")
        return

    mode = st.radio("Operation Mode:", ["Inject Data (Hide)", "Extract Data (Reveal)"], horizontal=True)
    
    if mode == "Inject Data (Hide)":
        up_file = st.file_uploader("Source Image:", type=["png", "jpg", "jpeg"])
        secret = st.text_area("Secret Payload:", help="Message to hide inside pixels.")
        
        if st.button("EXECUTE MASKING"):
            if up_file and secret:
                with st.spinner("Modifying pixel structure..."):
                    res_img, status = apply_lsb_mask(Image.open(up_file), secret)
                    if res_img:
                        st.image(res_img, caption="Masked Output")
                        buf = io.BytesIO()
                        res_img.save(buf, format="PNG")
                        st.download_button("Download Masked Node", buf.getvalue(), "shadow_node.png")
                        write_terminal("Steganography completed.")
                        system_log(st.
