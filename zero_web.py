# ==============================================================================
# PROJE: ZERO NETWORK - SHADOW PROTOCOL v40.0
# YETKİ: SADECE ÜST DÜZEY AJANLAR İÇİNDİR
# SATIR HEDEFİ: 560+ (Mekanik ve Fonksiyonel Doluluk)
# ==============================================================================

import streamlit as st
import os
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import io
import time
import random
import base64

# --- SİSTEM SABİTLERİ VE DOSYA YAPILANDIRMASI ---
DB_ROOT = "db_system"
if not os.path.exists(DB_ROOT):
    os.makedirs(DB_ROOT)

FILES = {
    "users": f"{DB_ROOT}/core_users.txt",
    "global": f"{DB_ROOT}/stream_global.txt",
    "priv": f"{DB_ROOT}/stream_private.txt",
    "groups": f"{DB_ROOT}/core_groups.txt",
    "profs": f"{DB_ROOT}/core_profiles.txt",
    "logs": f"{DB_ROOT}/system_logs.txt",
    "lock": f"{DB_ROOT}/sys_lock.bin",
    "intel": f"{DB_ROOT}/intel_feed.txt"
}

# Başlangıçta tüm dosyaları güvenli modda oluştur
for key, path in FILES.items():
    if not os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f:
            pass

# Rütbe Hiyerarşisi (Sayısal Güç Seviyeleri)
RANKS = {
    "MEMBER": {"lvl": 1, "color": "#7ee787", "desc": "Saha Elemanı"},
    "SHADOW": {"lvl": 2, "color": "#d299ff", "desc": "Gölge Ajan"},
    "ELITE": {"lvl": 3, "color": "#58a6ff", "desc": "Seçkin Birim"},
    "GHOST": {"lvl": 4, "color": "#ff7b72", "desc": "Hayalet İstihbaratçı"}
}

# ==============================================================================
# --- 1. GÜVENLİK VE KRİPTO MOTORU (V30 ENHANCED) ---
# ==============================================================================
# Klasik sembolik yer değiştirme + Base64 katmanı
ABC = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()[]{}@"
SYM = ['!', '?', '*', '#', '$', '%', '&', '/', '=', '+', '-', '_', '.', ',', ':', ';', '<', '>', '|', '@', 'æ', 'ß', '~', 'Δ', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç', 'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'ν', 'ξ', 'ο', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

ENC_KEY = dict(zip(ABC, SYM))
DEC_KEY = dict(zip(SYM, ABC))

def shadow_encode(text):
    if not text: return ""
    res = "".join([ENC_KEY.get(c, c) for c in text])
    return base64.b64encode(res.encode()).decode()

def shadow_decode(coded):
    if not coded: return ""
    try:
        decoded_b64 = base64.b64decode(coded).decode()
        return "".join([DEC_KEY.get(c, c) for c in decoded_b64])
    except:
        return "⚠️ VERİ BOZULMASI"

# ==============================================================================
# --- 2. SANSÜR VE FOTO-İSTİHBARAT MOTORU (GLITCH-LSB) ---
# ==============================================================================
def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', 'ignore')

def apply_glitch_censorship(img, secret_text):
    """Fotoğrafın üstüne parazit ekler ve altına veri gizler."""
    img = img.convert("RGB")
    width, height = img.size
    img_array = np.array(img, dtype=np.uint8)
    
    # 1. Görsel Sansür (Glitch Efekti)
    draw = ImageDraw.Draw(img)
    for _ in range(15): # Rastgele 15 sansür şeridi
        y = random.randint(0, height-20)
        h_line = random.randint(5, 25)
        draw.rectangle([0, y, width, y+h_line], fill=(random.randint(0,50), 0, 0))
    
    # 2. LSB Enjeksiyonu
    # Bitiş bayrağı ekle
    secret_text += " [END_SIG]"
    binary_secret = "".join([format(ord(i), '08b') for i in secret_text])
    
    flat = img_array.flatten()
    if len(binary_secret) > len(flat):
        return None, "❌ HATA: Fotoğraf verisi bu mesaj için çok küçük."
    
    for i in range(len(binary_secret)):
        flat[i] = (flat[i] & ~1) | int(binary_secret[i])
        
    final_array = flat.reshape(img_array.shape)
    return Image.fromarray(final_array), "✅ Sinyal Glitch altına gizlendi."

def reveal_glitch_data(img):
    """Glitchli fotoğraftan veriyi çeker."""
    img_array = np.array(img, dtype=np.uint8)
    flat = img_array.flatten()
    
    bits = ""
    for i in range(len(flat)):
        bits += str(flat[i] & 1)
        if len(bits) % 8 == 0:
            last_char_bin = bits[-8:]
            try:
                char = chr(int(last_char_bin, 2))
                # Veri sonu kontrolü
                if bits.endswith("01011101"): # ']' karakteri kontrolü (basit hızlandırma)
                    test_str = ""
                    for j in range(0, len(bits), 8):
                        test_str += chr(int(bits[j:j+8], 2))
                    if "[END_SIG]" in test_str:
                        return test_str.replace(" [END_SIG]", "")
            except: continue
    return "❌ Gizli veri bulunamadı veya bozuk."

# ==============================================================================
# --- 3. VERİ YÖNETİM FONKSİYONLARI ---
# ==============================================================================
def get_all_users():
    with open(FILES["users"], "r", encoding="utf-8") as f:
        return [l.strip().split(":")[0] for l in f if ":" in l]

def get_user_profile(nick):
    # Varsayılan profil
    profile = {"nick": nick, "rank": "MEMBER", "bio": "ZERO Aktif Birim", "avatar": "https://i.imgur.com/v6S6asL.png"}
    if nick == "admin": profile["rank"] = "GHOST"
    
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    parts = line.strip().split("|")
                    if len(parts) >= 4:
                        profile.update({"rank": parts[1], "bio": parts[2], "avatar": parts[3]})
    return profile

def save_profile(nick, rank, bio, avatar):
    lines = []
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    updated = False
    with open(FILES["profs"], "w", encoding="utf-8") as f:
        for l in lines:
            if l.startswith(f"{nick}|"):
                f.write(f"{nick}|{rank}|{bio}|{avatar}\n")
                updated = True
            else:
                f.write(l)
        if not updated:
            f.write(f"{nick}|{rank}|{bio}|{avatar}\n")

def log_event(user, action):
    with open(FILES["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user.upper()} >> {action}\n")

# ==============================================================================
# --- 4. STREAMLIT ARAYÜZ TASARIMI (CSS) ---
# ==============================================================================
st.set_page_config(page_title="ZERO NETWORK v40", page_icon="🕵️", layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;500&display=swap');
    
    .stApp {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Fira Code', monospace; }}
    .stSidebar {{ background-color: #161b22 !important; border-right: 1px solid #30363d; }}
    
    .msg-box {{ 
        background: #1c2128; padding: 15px; border-radius: 10px; 
        border: 1px solid #30363d; margin-bottom: 10px; 
        border-left: 5px solid #58a6ff;
    }}
    .intel-card {{
        background: #3d1a1a; padding: 10px; border: 1px solid #ff7b72;
        border-radius: 5px; color: #ffa198; font-weight: bold;
    }}
    .rank-badge {{
        padding: 3px 8px; border-radius: 20px; font-size: 0.75em;
        text-transform: uppercase; font-weight: bold; border: 1px solid;
    }}
    .stButton>button {{
        width: 100%; background-color: #238636; color: white; border: none;
    }}
    .stTextInput>div>div>input {{ background-color: #0d1117; color: #58a6ff; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 5. OTURUM KONTROLÜ VE GİRİŞ SİSTEMİ ---
# ==============================================================================
if 'session' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'page': 'DASHBOARD', 'target': None})

if not st.session_state['auth']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📡 ZERO NETWORK v40.0")
        st.caption("SHADOW PROTOCOL | TERMINAL ACCESS")
        
        mode = st.tabs(["🔐 ACCESS", "📝 REGISTER"])
        
        with mode[0]:
            u = st.text_input("Agent ID")
            p = st.text_input("Password", type="password")
            if st.button("INITIATE CONNECTION"):
                if (u == "admin" and p == "1234") or (f"{u}:{p}" in open(FILES["users"]).read()):
                    st.session_state.update({'auth': True, 'user': u})
                    log_event(u, "Terminal bağlantısı kuruldu.")
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Invalid Credentials")
        
        with mode[1]:
            nu = st.text_input("New Agent ID")
            np = st.text_input("Set Password", type="password")
            if st.button("CREATE PROTOCOL"):
                if nu and np and nu not in get_all_users():
                    with open(FILES["users"], "a", encoding="utf-8") as f:
                        f.write(f"{nu}:{np}\n")
                    save_profile(nu, "MEMBER", "Yeni Katılan Ajan", "https://i.imgur.com/v6S6asL.png")
                    log_event(nu, "Yeni ajan kaydı oluşturuldu.")
                    st.success("PROTOCOL CREATED. Proceed to Access.")
                else:
                    st.warning("ID already exists or invalid.")

else:
    # --- ANA PANEL ---
    me = st.session_state['user']
    prof = get_user_profile(me)
    lvl = RANKS[prof['rank']]['lvl']
    
    # Sidebar
    st.sidebar.image(prof['avatar'], width=100)
    st.sidebar.title(f"AGENT: {me}")
    st.sidebar.markdown(f"<span class='rank-badge' style='color:{RANKS[prof['rank']]['color']}; border-color:{RANKS[prof['rank']]['color']}'>{prof['rank']}</span>", unsafe_allow_html=True)
    st.sidebar.write(f"_{prof['desc']}_")
    st.sidebar.divider()
    
    menu = st.sidebar.radio("COMMAND CENTER", [
        "🌐 GLOBAL FLOW", 
        "🔒 PRIV CHANNELS", 
        "👥 GROUP NODES", 
        "🖼️ SHADOW MASK (LSB)", 
        "🛠️ TECH TOOLS",
        "🛡️ ROOT CENTRAL"
    ])
    
    if st.sidebar.button("🔌 DISCONNECT"):
        log_event(me, "Bağlantı kesildi.")
        st.session_state['auth'] = False
        st.rerun()

    # --- 1. GLOBAL FLOW (FRAGMENT) ---
    if menu == "🌐 GLOBAL FLOW":
        st.subheader("🌐 Küresel Veri Akışı")
        
        # Intel Feed (Admin Mesajları)
        if os.path.exists(FILES["intel"]):
            intel_data = open(FILES["intel"], "r", encoding="utf-8").readlines()
            if intel_data:
                st.markdown(f"<div class='intel-card'>FLASH INTEL: {intel_data[-1]}</div>", unsafe_allow_html=True)
        
        chat_container = st.container(height=450, border=True)
        with chat_container:
            if os.path.exists(FILES["global"]):
                for line in open(FILES["global"], "r", encoding="utf-8").readlines():
                    p = line.strip().split("|")
                    if len(p) == 3:
                        u, m, t = p
                        u_prof = get_user_profile(u)
                        st.markdown(f"""
                        <div class='msg-box'>
                            <b style='color:{RANKS[u_prof['rank']]['color']}'>{u}</b> 
                            <small style='float:right; opacity:0.5;'>{t}</small><br>
                            {shadow_decode(m)}
                        </div>
                        """, unsafe_allow_html=True)

        with st.form("global_send", clear_on_submit=True):
            g_msg = st.text_input("Mesaj Enjekte Et...")
            if st.form_submit_button("SEND") and g_msg:
                with open(FILES["global"], "a", encoding="utf-8") as f:
                    f.write(f"{me}|{shadow_encode(g_msg)}|{datetime.now().strftime('%H:%M')}\n")
                st.rerun()

    # --- 2. PRIVATE CHANNELS ---
    elif menu == "🔒 PRIV CHANNELS":
        st.subheader("🔒 Özel Sinyal Hattı")
        target = st.selectbox("Hedef Seç", [u for u in get_all_users() if u != me] + (["admin"] if me != "admin" else []))
        
        priv_container = st.container(height=400, border=True)
        with priv_container:
            if os.path.exists(FILES["priv"]):
                for line in open(FILES["priv"], "r", encoding="utf-8").readlines():
                    p = line.strip().split("|")
                    if len(p) == 4:
                        frm, to, m, t = p
                        if (frm == me and to == target) or (frm == target and to == me):
                            st.write(f"**{frm}:** {shadow_decode(m)}")

        with st.form("priv_send", clear_on_submit=True):
            p_msg = st.text_input("Gizli Fısıltı...")
            if st.form_submit_button("TRANSMIT") and p_msg:
                with open(FILES["priv"], "a", encoding="utf-8") as f:
                    f.write(f"{me}|{target}|{shadow_encode(p_msg)}|{datetime.now().strftime('%H:%M')}\n")
                st.rerun()

    # --- 3. GROUP NODES (RÜTBE KORUMALI) ---
    elif menu == "👥 GROUP NODES":
        st.subheader("👥 Grup Düğümleri")
        group_list = {
            "GÖLGE KANTİN": 1,
            "OPERASYON MERKEZİ": 2,
            "ELİTE KONSEY": 3,
            "HAYALET ODASI": 4
        }
        
        sel_group = st.selectbox("Düğüm Seç", list(group_list.keys()))
        req_lvl = group_list[sel_group]
        
        if lvl >= req_lvl:
            st.success(f"{sel_group} Erişim Yetkisi Onaylandı.")
            g_file = f"{DB_ROOT}/group_{sel_group.replace(' ', '_')}.txt"
            if not os.path.exists(g_file): open(g_file, "a").close()
            
            g_container = st.container(height=350, border=True)
            with g_container:
                for line in open(g_file, "r", encoding="utf-8").readlines():
                    p = line.strip().split("|")
                    if len(p) == 3:
                        st.write(f"**{p[0]}**: {shadow_decode(p[1])} _({p[2]})_")
            
            with st.form("group_form", clear_on_submit=True):
                g_in = st.text_input("Grup Sinyali...")
                if st.form_submit_button("BROADCAST") and g_in:
                    with open(g_file, "a", encoding="utf-8") as f:
                        f.write(f"{me}|{shadow_encode(g_in)}|{datetime.now().strftime('%H:%M')}\n")
                    st.rerun()
        else:
            st.error(f"ERİŞİM REDDEDİLDİ: Bu düğüm için en az {list(RANKS.keys())[req_lvl-1]} rütbesi gerekir.")

    # --- 4. SHADOW MASK (LSB STENANOGRAFİ) ---
    elif menu == "🖼️ SHADOW MASK (LSB)":
        st.subheader("🖼️ Gölge Maskeleme Sistemi")
        st.info("Bu sistem, veriyi görsel parazitlerin (glitch) içine ve piksel bitlerine gizler.")
        
        t1, t2 = st.tabs(["🔒 MASKING", "🔓 UNMASKING"])
        
        with t1:
            if lvl >= 2:
                up_img = st.file_uploader("Ana Fotoğrafı Seç", type=['png', 'jpg'])
                secret = st.text_area("Gizlenecek İstihbarat")
                if up_img and secret and st.button("SANSÜRLE VE ENJEKTE ET"):
                    input_img = Image.open(up_img)
                    res_img, status = apply_glitch_censorship(input_img, secret)
                    if res_img:
                        st.image(res_img, caption="Şifrelenmiş Sinyal")
                        buf = io.BytesIO()
                        res_img.save(buf, format="PNG")
                        st.download_button("GÖLGE DOSYAYI İNDİR", buf.getvalue(), f"shadow_{int(time.time())}.png")
                        log_event(me, "Bir fotoğrafa veri gizledi.")
                    else: st.error(status)
            else:
                st.error("SHADOW MASK kullanmak için en az SHADOW rütbesi gerekir.")

        with t2:
            if lvl >= 2:
                down_img = st.file_uploader("Şifreli Fotoğrafı Yükle", type=['png'])
                if down_img and st.button("DEŞİFRE ET"):
                    raw = Image.open(down_img)
                    decoded = reveal_glitch_data(raw)
                    st.success(f"ÇÖZÜLEN VERİ: {decoded}")
                    log_event(me, f"{down_img.name} dosyasını deşifre etti.")
            else:
                st.error("Deşifre araçları SHADOW+ rütbesine açıktır.")

    # --- 5. TECH TOOLS ---
    elif menu == "🛠️ TECH TOOLS":
        st.subheader("🛠️ Teknik Ekipman")
        if lvl >= 2:
            st.write("Manuel Sinyal Kodlayıcı/Çözücü")
            tc1, tc2 = st.columns(2)
            raw_text = tc1.text_area("Ham Metin")
            if tc1.button("ENCODE"): tc1.code(shadow_encode(raw_text))
            
            coded_text = tc2.text_area("Kodlanmış Sinyal")
            if tc2.button("DECODE"): tc2.info(shadow_decode(coded_text))
            
            st.divider()
            st.write("Sistem Durumu")
            st.json({
                "Core": "v40.0-Shadow",
                "Files": len(os.listdir(DB_ROOT)),
                "Logs": sum(1 for _ in open(FILES["logs"])),
                "Status": "ONLINE"
            })
        else:
            st.error("Teknik araçlar MEMBER rütbesine kapalıdır.")

    # --- 6. ROOT CENTRAL ---
    elif menu == "🛡️ ROOT CENTRAL":
        if lvl >= 4 or me == "admin":
            st.subheader("🛡️ Ana Kontrol Merkezi")
            
            if me == "admin":
                adm_t1, adm_t2, adm_t3 = st.tabs(["👤 AGENT MANAGEMENT", "📣 INTEL FEED", "📜 SYSTEM LOGS"])
                
                with adm_t1:
                    for agent in get_all_users():
                        a_p = get_user_profile(agent)
                        with st.expander(f"Agent: {agent}"):
                            new_r = st.selectbox("Rank", list(RANKS.keys()), index=list(RANKS.keys()).index(a_p['rank']), key=f"r_{agent}")
                            new_bio = st.text_input("Bio", a_p['bio'], key=f"b_{agent}")
                            if st.button("UPDATE AGENT", key=f"btn_{agent}"):
                                save_profile(agent, new_r, new_bio, a_p['avatar'])
                                st.success(f"{agent} güncellendi.")
                
                with adm_t2:
                    news = st.text_input("Acil İstihbarat Geç...")
                    if st.button("YAYINLA"):
                        with open(FILES["intel"], "w", encoding="utf-8") as f:
                            f.write(news)
                        st.success("Haber yayında.")
                
                with adm_t3:
                    log_content = open(FILES["logs"], "r", encoding="utf-8").readlines()
                    st.code("".join(log_content[-50:]))
                    if st.button("LOGLARI SIFIRLA"):
                        open(FILES["logs"], "w").close()
                        st.rerun()
            else:
                st.info("GHOST YETKİSİ: Sistem loglarını izleme yetkisine sahipsiniz.")
                log_content = open(FILES["logs"], "r", encoding="utf-8").readlines()
                st.code("".join(log_content[-30:]))
        else:
            st.error("ACCESS DENIED: ROOT yetkisi gerekli.")

# ==============================================================================
# PROJE SONU - ZERO NETWORK v40.0
# ==============================================================================
