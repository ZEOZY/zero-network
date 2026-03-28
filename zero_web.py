# ==============================================================================
# PROJE: ZERO NETWORK - OMEGA PROTOCOL v45.0
# YETKİ: ROOT / GHOST / ELITE / SHADOW / MEMBER
# NOT: BU KOD 580 SATIR (BOŞLUKSUZ) HEDEFİYLE MODÜLER İNŞA EDİLMİŞTİR.
# ==============================================================================

import streamlit as st
import os
import numpy as np
import pandas as pd
import io
import time
import random
import base64
import binascii
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime

# --- SİSTEM ÇEKİRDEĞİ: DOSYA VE DİZİN YAPILANDIRMASI ---
ROOT_DIR = "zero_core_data"
if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)

CORE_FILES = {
    "auth": f"{ROOT_DIR}/access_control.db",
    "global": f"{ROOT_DIR}/global_relay.db",
    "private": f"{ROOT_DIR}/private_node.db",
    "profiles": f"{ROOT_DIR}/agent_profiles.db",
    "logs": f"{ROOT_DIR}/event_logs.db",
    "groups": f"{ROOT_DIR}/group_clusters.db",
    "intel": f"{ROOT_DIR}/intel_broadcast.db",
    "vault": f"{ROOT_DIR}/secure_vault.db",
    "settings": f"{ROOT_DIR}/sys_config.db"
}

for path in CORE_FILES.values():
    if not os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f: pass

# --- RÜTBE VE YETKİ MATRİSİ ---
RANK_ENGINE = {
    "MEMBER": {"lvl": 1, "color": "#00FF41", "tag": "[UNIT-01]", "power": 10},
    "SHADOW": {"lvl": 2, "color": "#BC13FE", "tag": "[OP-SHADOW]", "power": 25},
    "ELITE": {"lvl": 3, "color": "#00D4FF", "tag": "[ELITE-V]", "power": 50},
    "GHOST": {"lvl": 4, "color": "#FF3131", "tag": "[GHOST-X]", "power": 100}
}

# --- GELİŞMİŞ KRİPTOGRAFİ MOTORU (V45 HYBRID) ---
KEY_MAP = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()[]{}@#$%"
VAL_MAP = "!?*#$+%&/=+-_.:;<|>@æß~ΔΩμπ∞≈≠≤≥¶§÷×•¤†‡±√¬°^º¥©®™¿¡øæ∫çαβγδεζηθικλνξοπρστυφχψω"
SYM_ENC = dict(zip(KEY_MAP, VAL_MAP))
SYM_DEC = dict(zip(VAL_MAP, KEY_MAP))

def protocol_encrypt(raw):
    if not raw: return ""
    step1 = "".join([SYM_ENC.get(c, c) for c in raw])
    step2 = base64.b64encode(step1.encode()).decode()
    return step2[::-1] # Veriyi ters çevirerek ek güvenlik sağlar

def protocol_decrypt(coded):
    if not coded: return ""
    try:
        step2 = coded[::-1]
        step1 = base64.b64decode(step2).decode()
        return "".join([SYM_DEC.get(c, c) for c in step1])
    except Exception as e:
        return f"⚠️ DEŞİFRE HATASI: {str(e)}"

# --- SANSÜR VE STENANOGRAFİ MOTORU (OMEGA-LSB) ---
def hex_to_rgb(h): return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def apply_omega_mask(image, secret_msg, intensity=5):
    """Piksellere veri gizler ve görsel glitch/sansür ekler."""
    img = image.convert("RGB")
    data_bin = "".join([format(ord(i), '08b') for i in secret_msg]) + '1111111111111110'
    arr = np.array(img, dtype=np.uint8)
    flat = arr.flatten()
    if len(data_bin) > len(flat): return None, "Veri sığmıyor."
    for i in range(len(data_bin)):
        flat[i] = (flat[i] & ~1) | int(data_bin[i])
    res_arr = flat.reshape(arr.shape)
    final_img = Image.fromarray(res_arr)
    # Görsel Sansür Blokları Ekle
    draw = ImageDraw.Draw(final_img)
    w, h = final_img.size
    for _ in range(intensity * 3):
        x1 = random.randint(0, w); y1 = random.randint(0, h)
        x2 = x1 + random.randint(20, 100); y2 = y1 + random.randint(2, 10)
        draw.rectangle([x1, y1, x2, y2], fill=(random.randint(0,20), 0, 0))
    return final_img, "Sinyal enjekte edildi."

def extract_omega_mask(image):
    arr = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = arr.flatten()
    bits = ""
    for b in flat:
        bits += str(b & 1)
        if len(bits) >= 16 and bits.endswith('1111111111111110'): break
    chars = [bits[i:i+8] for i in range(0, len(bits)-16, 8)]
    try: return "".join([chr(int(c, 2)) for c in chars])
    except: return "Hata: Veri okunamadı."

# --- VERİ TABANI YÖNETİM MODÜLLERİ ---
def db_read(file_key):
    path = CORE_FILES[file_key]
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f: return f.readlines()

def db_write(file_key, content, mode="a"):
    with open(CORE_FILES[file_key], mode, encoding="utf-8") as f: f.write(content + "\n")

def get_agent_profile(nick):
    prof = {"nick": nick, "rank": "MEMBER", "bio": "ZERO Aktif Birim", "img": "https://i.imgur.com/v6S6asL.png", "status": "ONLINE"}
    if nick == "admin": prof["rank"] = "GHOST"
    lines = db_read("profiles")
    for l in lines:
        if l.startswith(f"{nick}|"):
            p = l.strip().split("|")
            if len(p) >= 4: prof.update({"rank": p[1], "bio": p[2], "img": p[3]})
    return prof

def update_agent_profile(nick, rank, bio, img):
    lines = db_read("profiles")
    with open(CORE_FILES["profiles"], "w", encoding="utf-8") as f:
        exists = False
        for l in lines:
            if l.startswith(f"{nick}|"):
                f.write(f"{nick}|{rank}|{bio}|{img}\n"); exists = True
            else: f.write(l)
        if not exists: f.write(f"{nick}|{rank}|{bio}|{img}\n")

def sys_log(agent, action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_write("logs", f"[{now}] {agent.upper()} >> {action}")

# --- ARAYÜZ VE STİL (NEON MATRIX) ---
st.set_page_config(page_title="ZERO OMEGA v45", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    body { background-color: #050505; color: #00FF41; font-family: 'Share Tech Mono', monospace; }
    .stApp { background-color: #050505; }
    .sidebar .sidebar-content { background-image: linear-gradient(#050505, #101010); border-right: 1px solid #00FF41; }
    .st-emotion-cache-1kyxreq { justify-content: center; }
    .agent-card { border: 1px solid #00FF41; padding: 10px; border-radius: 5px; background: rgba(0, 255, 65, 0.05); margin-bottom: 10px; }
    .intel-feed { background: #1a0000; color: #ff3131; padding: 15px; border: 2px solid #ff3131; border-radius: 8px; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    .msg-received { background: #0a0a0a; border-left: 3px solid #00FF41; padding: 10px; margin: 5px 0; border-radius: 0 5px 5px 0; }
    .msg-sent { background: #111; border-right: 3px solid #BC13FE; padding: 10px; margin: 5px 0; border-radius: 5px 0 0 5px; text-align: right; }
    .stButton>button { width: 100%; border: 1px solid #00FF41; background: transparent; color: #00FF41; transition: 0.3s; }
    .stButton>button:hover { background: #00FF41; color: black; box-shadow: 0 0 15px #00FF41; }
    .stTextInput>div>div>input { background-color: #000; color: #00FF41; border: 1px solid #00FF41; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- OTURUM YÖNETİMİ ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'terminal_msg': [], 'last_sync': time.time()})

def terminal_print(msg):
    st.session_state.terminal_msg.append(f"> {msg}")
    if len(st.session_state.terminal_msg) > 10: st.session_state.terminal_msg.pop(0)

# --- GİRİŞ VE KAYIT PANELİ ---
if not st.session_state.auth:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.title("📟 ZERO OMEGA v45.0")
        st.caption("SECURE NETWORK INTERFACE // STANDBY MODE")
        tab_acc, tab_reg = st.tabs(["[ 🔑 ACCESS ]", "[ 📝 REGISTER ]"])
        
        with tab_acc:
            u_id = st.text_input("AGENT_ID")
            u_pw = st.text_input("AUTH_KEY", type="password")
            if st.button("EXECUTE LOGIN"):
                users = db_read("auth")
                if (u_id == "admin" and u_pw == "1234") or (f"{u_id}:{u_pw}\n" in users):
                    st.session_state.auth = True; st.session_state.user = u_id
                    sys_log(u_id, "Sisteme giriş yaptı."); st.rerun()
                else: st.error("ACCESS DENIED: Credentials mismatch.")
        
        with tab_reg:
            n_id = st.text_input("NEW_AGENT_ID")
            n_pw = st.text_input("NEW_AUTH_KEY", type="password")
            if st.button("CREATE NEW NODE"):
                if n_id and n_pw and n_id not in [l.split(":")[0] for l in db_read("auth")]:
                    db_write("auth", f"{n_id}:{n_pw}")
                    update_agent_profile(n_id, "MEMBER", "Yeni Katılan Birim", "https://i.imgur.com/v6S6asL.png")
                    sys_log(n_id, "Yeni ajan kaydı oluşturuldu.")
                    st.success("NODE CREATED. Login to proceed.")
                else: st.warning("ID invalid or taken.")

else:
    # --- ANA KONTROL PANELİ ---
    me = st.session_state.user
    my_p = get_agent_profile(me)
    my_lvl = RANK_ENGINE[my_p['rank']]['lvl']
    
    # Sidebar: Ajan Bilgileri
    st.sidebar.markdown(f"### 🥷 {me.upper()}")
    st.sidebar.image(my_p['img'], width=150)
    st.sidebar.markdown(f"**RANK:** <span style='color:{RANK_ENGINE[my_p['rank']]['color']}'>{my_p['rank']}</span>", unsafe_allow_html=True)
    st.sidebar.caption(f"_{my_p['bio']}_")
    st.sidebar.divider()
    
    menu_opt = st.sidebar.radio("COMMANDS", [
        "📡 GLOBAL_FEED", 
        "🔒 PRIV_CHANNEL", 
        "👥 GROUP_NODES", 
        "🎭 SHADOW_MASK", 
        "🛠️ TECH_STATION", 
        "🛡️ ROOT_CENTRAL"
    ])
    
    if st.sidebar.button("🔌 TERMINATE_SESSION"):
        sys_log(me, "Oturum kapatıldı."); st.session_state.auth = False; st.rerun()
    
    # Terminal Widget
    st.sidebar.divider()
    st.sidebar.subheader("System Logs")
    for tm in st.session_state.terminal_msg: st.sidebar.code(tm)

    # --- 1. GLOBAL_FEED MODÜLÜ ---
    if menu_opt == "📡 GLOBAL_FEED":
        st.subheader("🌐 Global Veri Akışı")
        intel = db_read("intel")
        if intel: st.markdown(f"<div class='intel-feed'>INTEL: {intel[-1]}</div>", unsafe_allow_html=True)
        
        feed_box = st.container(height=450, border=True)
        with feed_box:
            messages = db_read("global")
            for m in messages:
                parts = m.strip().split("|")
                if len(parts) == 3:
                    u, msg, t = parts
                    u_p = get_agent_profile(u)
                    st.markdown(f"""
                    <div class='msg-received'>
                        <b style='color:{RANK_ENGINE[u_p['rank']]['color']}'>{u}</b> 
                        <small style='float:right; opacity:0.3;'>{t}</small><br>
                        {protocol_decrypt(msg)}
                    </div>
                    """, unsafe_allow_html=True)
        
        with st.form("g_send", clear_on_submit=True):
            raw_msg = st.text_input("Sinyal girişi...")
            if st.form_submit_button("ENJECTE ET") and raw_msg:
                db_write("global", f"{me}|{protocol_encrypt(raw_msg)}|{datetime.now().strftime('%H:%M')}")
                terminal_print("Global sinyal gönderildi."); st.rerun()

    # --- 2. PRIV_CHANNEL MODÜLÜ ---
    elif menu_opt == "🔒 PRIV_CHANNEL":
        st.subheader("🔒 Bire-Bir Güvenli Hat")
        agents = [a for a in [l.split(":")[0] for l in db_read("auth")] if a != me] + (["admin"] if me != "admin" else [])
        target_agent = st.selectbox("Hedef Seç", agents)
        
        p_box = st.container(height=400, border=True)
        with p_box:
            p_messages = db_read("private")
            for pm in p_messages:
                pts = pm.strip().split("|")
                if len(pts) == 4:
                    f, t, m, ts = pts
                    if (f == me and t == target_agent) or (f == target_agent and t == me):
                        cls = "msg-sent" if f == me else "msg-received"
                        st.markdown(f"<div class='{cls}'><b>{f}:</b> {protocol_decrypt(m)}</div>", unsafe_allow_html=True)

        with st.form("p_send", clear_on_submit=True):
            p_raw = st.text_input("Gizli Mesaj...")
            if st.form_submit_button("FISILDA") and p_raw:
                db_write("private", f"{me}|{target_agent}|{protocol_encrypt(p_raw)}|{datetime.now().strftime('%H:%M')}")
                terminal_print(f"{target_agent} birimine fısıldandı."); st.rerun()

    # --- 3. GROUP_NODES MODÜLÜ ---
    elif menu_opt == "👥 GROUP_NODES":
        st.subheader("👥 Grup Sinyal Kümeleri")
        clusters = {"KANTİN": 1, "SAHA_EKİBİ": 2, "ELİTE_BİRİM": 3, "GHOST_COUNCIL": 4}
        sel_c = st.selectbox("Küme Seç", list(clusters.keys()))
        
        if my_lvl >= clusters[sel_c]:
            st.success(f"{sel_c} Erişimi Onaylandı.")
            c_file = f"group_{sel_c}.db"
            c_path = f"{ROOT_DIR}/{c_file}"
            if not os.path.exists(c_path): open(c_path, "a").close()
            
            c_box = st.container(height=350, border=True)
            with c_box:
                for cl in open(c_path, "r", encoding="utf-8").readlines():
                    cp = cl.strip().split("|")
                    if len(cp) == 3: st.write(f"**{cp[0]}**: {protocol_decrypt(cp[1])} _({cp[2]})_")
            
            with st.form("c_send", clear_on_submit=True):
                c_msg = st.text_input("Küme Sinyali...")
                if st.form_submit_button("YAYINLA") and c_msg:
                    with open(c_path, "a", encoding="utf-8") as f:
                        f.write(f"{me}|{protocol_encrypt(c_msg)}|{datetime.now().strftime('%H:%M')}\n")
                    terminal_print(f"{sel_c} kümesine yazıldı."); st.rerun()
        else:
            st.error("YETERSİZ YETKİ SEVİYESİ.")

    # --- 4. SHADOW_MASK (OMEGA-LSB) MODÜLÜ ---
    elif menu_opt == "🎭 SHADOW_MASK":
        st.subheader("🎭 Gölge Maskeleme ve Sansür Ünitesi")
        if my_lvl >= 2:
            st.info("Piksel tabanlı veri gizleme ve görsel sansürleme aktif.")
            m_tab1, m_tab2 = st.tabs(["[ 🔒 MASKING ]", "[ 🔓 UNMASKING ]"])
            
            with m_tab1:
                u_img = st.file_uploader("Görsel Yükle", type=['png', 'jpg'])
                u_txt = st.text_area("Gizlenecek Veri")
                u_int = st.slider("Sansür Şiddeti", 1, 10, 5)
                if u_img and u_txt and st.button("SİNYALİ GİZLE"):
                    res, stat = apply_omega_mask(Image.open(u_img), u_txt, u_int)
                    if res:
                        st.image(res, caption="İşlenmiş Gölge Dosyası")
                        b = io.BytesIO(); res.save(b, format="PNG")
                        st.download_button("GÖLGE DOSYAYI AL", b.getvalue(), "shadow_omega.png")
                        sys_log(me, "Görsel maskeleme yaptı."); terminal_print("Maskeleme tamamlandı.")
                    else: st.error(stat)
            
            with m_tab2:
                d_img = st.file_uploader("Deşifre Edilecek Görsel", type=['png'])
                if d_img and st.button("DEŞİFRE ET"):
                    dec_txt = extract_omega_mask(Image.open(d_img))
                    st.success(f"Çözülen Sinyal: {dec_txt}")
                    sys_log(me, "Görsel deşifre etti."); terminal_print("Deşifre işlemi başarılı.")
        else:
            st.error("SHADOW+ Rütbesi Gerekli.")

    # --- 5. TECH_STATION MODÜLÜ ---
    elif menu_opt == "🛠️ TECH_STATION":
        st.subheader("🛠️ Teknik Servis İstasyonu")
        if my_lvl >= 2:
            st.write("Sinyal Kodlama/Çözme Terminali")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                r_t = st.text_area("Ham Veri")
                if st.button("KODLA"): st.code(protocol_encrypt(r_t))
            with col_t2:
                c_t = st.text_area("Kodlu Veri")
                if st.button("ÇÖZ"): st.info(protocol_decrypt(c_t))
            
            st.divider()
            st.write("Node Analitiği")
            st.bar_chart(pd.DataFrame({
                "Veri": ["Global", "Priv", "Logs", "Vault"],
                "Boyut": [len(db_read("global")), len(db_read("private")), len(db_read("logs")), 10]
            }).set_index("Veri"))
        else:
            st.error("Teknik araçlar sadece saha tecrübesi olan ajanlara (Shadow+) açıktır.")

    # --- 6. ROOT_CENTRAL MODÜLÜ ---
    elif menu_opt == "🛡️ ROOT_CENTRAL":
        if my_lvl >= 4 or me == "admin":
            st.subheader("🛡️ Root Kontrol Merkezi")
            if me == "admin":
                adm_tab1, adm_tab2, adm_tab3 = st.tabs(["[ 👤 AGENTS ]", "[ 📣 INTEL ]", "[ 📜 LOGS ]"])
                
                with adm_tab1:
                    all_ids = [l.split(":")[0] for l in db_read("auth")]
                    for aid in all_ids:
                        with st.expander(f"Agent ID: {aid}"):
                            ap = get_agent_profile(aid)
                            c1, c2 = st.columns(2)
                            nr = c1.selectbox("New Rank", list(RANK_ENGINE.keys()), index=list(RANK_ENGINE.keys()).index(ap['rank']), key=f"r_{aid}")
                            ni = c2.text_input("New Avatar URL", ap['img'], key=f"i_{aid}")
                            nb = st.text_area("New Bio", ap['bio'], key=f"b_{aid}")
                            if st.button("SYNC_PROFILE", key=f"btn_{aid}"):
                                update_agent_profile(aid, nr, nb, ni)
                                sys_log("ADMIN", f"{aid} profilini güncelledi."); st.success("OK")
                
                with adm_tab2:
                    broadcast_msg = st.text_input("Flash İstihbarat Yayınla")
                    if st.button("YAYINLA"):
                        db_write("intel", broadcast_msg, mode="w")
                        sys_log("ADMIN", "İstihbarat yayını yaptı."); st.success("Yayınlandı.")
                
                with adm_tab3:
                    st.code("".join(db_read("logs")[-100:]))
                    if st.button("WIPE_LOGS"):
                        open(CORE_FILES["logs"], "w").close()
                        terminal_print("Loglar temizlendi."); st.rerun()
            else:
                st.info("İzleme Yetkisi: Sadece sistem loglarını okuyabilirsiniz.")
                st.code("".join(db_read("logs")[-50:]))
        else:
            st.error("ERİŞİM YASAK: Bu bölge sadece Root/Ghost yetkisindeki ajanlar içindir.")

# ==============================================================================
# OMEGA PROTOCOL SİSTEM SONU // 2026 ZERO NETWORK
# ==============================================================================
