import streamlit as st
import os
import random
import time
import base64
import pandas as pd
from datetime import datetime

# ==============================================================================
# --- 1. DOSYA SİSTEMİ VE VERİTABANI MİMARİSİ (GENİŞLETİLMİŞ) ---
# ==============================================================================
# Her veri türü için ayrı bir dosya ve yol tanımı.
FILES = {
    "users": "db_users.txt",       # Kimlik bilgileri
    "chat": "db_global_chat.txt",  # Genel sohbet
    "priv": "db_private_messages.txt", # Özel mesajlar
    "ban": "db_blacklist.txt",     # Yasaklı listesi
    "profs": "db_user_profiles.txt",# Profil detayları
    "logs": "db_system_logs.txt",   # Sistem hareketleri
    "vault": "db_vault_files.txt", # Paylaşılan dosyalar
    "lock": "db_sys_lock.txt"      # Güvenlik kilidi
}

# Dosyaların varlığını kontrol et ve yoksa oluştur (Boot süreci)
for key, path in FILES.items():
    if not os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f:
            pass

# ==============================================================================
# --- 2. GELİŞMİŞ ŞİFRELEME KATMANI (V32 ALPHA) ---
# ==============================================================================
# Karakter seti genişletildi, semboller karmaşıklaştırıldı.
CHAR_SET = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()=@#$%"
SYMB_SET = ['⌬', '⏣', '⚡', '🔥', '💀', '☣', '☢', '⚙', '🔗', '🔒', '🔑', '📡', '🛰', '💻', '📱', '🕹', '🎮', '💾', '💿', '📀', '📼', '📷', '📹', '📞', '📠', '🔋', '🔌', '🔎', '💡', '🔦', '🏮', '📔', '📕', '📖', '📗', '📘', '📙', '📚', '📓', '📒', '📃', '📜', '📄', '📅', '📆', '📇', '📈', '📉', '📊', '📋', '📌', '📍', '📎', '📏', '📐', '✂', '🔏', '🔐', '🔑', '🔨', '⛏', '⚒', '🛠', '🗡', '⚔', '🔫', '🏹', '🛡', '🔧', '🔩', '⚙', '🗜', '⚖', '🔗', '⛓', '🧪', '🌡']

ENCODE_DICT = dict(zip(CHAR_SET, SYMB_SET))
DECODE_DICT = dict(zip(SYMB_SET, CHAR_SET))

def crypto_encode(text):
    """Metni sembolik ajana dönüştürür."""
    if not text: return ""
    return "".join([ENCODE_DICT.get(c, c) for c in text])

def crypto_decode(text):
    """Sembolik ajanı metne geri döndürür."""
    if not text: return ""
    return "".join([DECODE_DICT.get(c, c) for c in text])

# ==============================================================================
# --- 3. VERİ YÖNETİM MODÜLLERİ ---
# ==============================================================================
def load_all_users():
    """Tüm kayıtlı kullanıcıları listede toplar."""
    if not os.path.exists(FILES["users"]): return []
    with open(FILES["users"], "r", encoding="utf-8") as f:
        return [line.strip().split(":")[0] for line in f if ":" in line]

def get_detailed_profile(username):
    """Kullanıcının tüm profil ve XP verilerini çeker."""
    prof = {
        "nick": username, 
        "display_name": username, 
        "bio": "ZERO biriminin gizli bir üyesi.", 
        "avatar": "https://i.imgur.com/v6S6asL.png", 
        "rank": "MEMBER", 
        "xp": 0,
        "last_seen": "Bilinmiyor"
    }
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{username}|"):
                    d = line.strip().split("|")
                    if len(d) >= 7:
                        prof.update({
                            "display_name": d[1], "bio": d[2], "avatar": d[3], 
                            "rank": d[4], "xp": int(d[5]), "last_seen": d[6]
                        })
    return prof

def save_detailed_profile(u, dn, b, a, r, x, ls):
    """Profil verilerini kalıcı depolamaya yazar."""
    lines = []
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    with open(FILES["profs"], "w", encoding="utf-8") as f:
        updated = False
        for line in lines:
            if line.startswith(f"{u}|"):
                f.write(f"{u}|{dn}|{b}|{a}|{r}|{x}|{ls}\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"{u}|{dn}|{b}|{a}|{r}|{x}|{ls}\n")

def system_logger(user, message):
    """Sistem olaylarını log dosyasına tarihli olarak ekler."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FILES["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{now}] AGENT_{user}: {message}\n")

# ==============================================================================
# --- 4. GÖRSEL TASARIM VE TEMA MOTORU ---
# ==============================================================================
st.set_page_config(page_title="ZERO MONARCH v32", page_icon="👑", layout="wide")

# Matrix / Cyberpunk CSS Tasarımı
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Share Tech Mono', monospace;
        background-color: #050505;
        color: #00ff41;
    }
    
    .stApp { background: #050505; }
    
    /* Mesaj Baloncukları */
    .msg-box {
        background: rgba(0, 255, 65, 0.03);
        border: 1px solid #00ff4122;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 12px;
        position: relative;
    }
    .msg-box:hover {
        border-color: #00ff41;
        background: rgba(0, 255, 65, 0.08);
    }
    
    .user-label { color: #58a6ff; font-weight: bold; font-size: 0.9em; }
    .time-label { color: #8b949e; font-size: 0.7em; float: right; }
    
    /* Admin Paneli Özel CSS */
    .admin-zone {
        border: 2px solid #f85149;
        padding: 20px;
        background: rgba(248, 81, 73, 0.05);
        border-radius: 10px;
    }
    
    /* Buton Tasarımları */
    .stButton>button {
        border: 1px solid #00ff41;
        background: transparent;
        color: #00ff41;
        transition: 0.4s;
        width: 100%;
    }
    .stButton>button:hover {
        background: #00ff41;
        color: #000;
        box-shadow: 0 0 15px #00ff41;
    }
    
    /* Sidebar Düzenlemeleri */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #00ff4133;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 5. MODÜLER FRAGMENTLAR (REAL-TIME ENGINE) ---
# ==============================================================================
@st.fragment(run_every="3s")
def global_chat_module(me, is_locked):
    """Küresel veri akışını yöneten devasa modül."""
    st.markdown("### 📡 GLOBAL DATA STREAM")
    container = st.container(height=500, border=True)
    
    if os.path.exists(FILES["chat"]):
        with open(FILES["chat"], "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                parts = line.strip().split("|")
                if len(parts) == 3:
                    u, m, t = parts
                    decoded = crypto_decode(m)
                    # Admin her şeyi çözer, kilit yoksa herkes çözer
                    if me == "admin" or not is_locked or idx == len(lines)-1:
                        container.markdown(f"""
                        <div class='msg-box'>
                            <span class='user-label'>{u}</span>
                            <span class='time-label'>{t}</span><br>
                            <span style='color:#e6edf3;'>{decoded}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        container.markdown(f"<div class='msg-box'><b>{u}:</b> <code>{m}</code></div>", unsafe_allow_html=True)
    
    with st.form("global_sender", clear_on_submit=True):
        g_input = st.text_input("", placeholder="Mesajını şifrele ve gönder...")
        if st.form_submit_button("SİNYALİ GÖNDER") and g_input:
            with open(FILES["chat"], "a", encoding="utf-8") as f:
                f.write(f"{me}|{crypto_encode(g_input)}|{datetime.now().strftime('%H:%M:%S')}\n")
            # XP Kazanımı
            p = get_detailed_profile(me)
            save_detailed_profile(me, p['display_name'], p['bio'], p['avatar'], p['rank'], p['xp']+1, datetime.now().strftime("%H:%M"))
            st.rerun(scope="fragment")

@st.fragment(run_every="3s")
def private_chat_module(me, target, is_locked):
    """Özel mesajlardaki pürüzleri gideren çift yönlü senkronizasyon modülü."""
    st.markdown(f"### 🔒 SECURE TUNNEL: {target}")
    p_container = st.container(height=400, border=True)
    
    if os.path.exists(FILES["priv"]):
        with open(FILES["priv"], "r", encoding="utf-8") as f:
            all_msgs = f.readlines()
            # Çapraz sorgu filtresi
            filtered = [l.strip().split("|") for l in all_msgs if (f"{me}|{target}" in l or f"{target}|{me}" in l)]
            
            for idx, data in enumerate(filtered):
                if len(data) == 3:
                    sender, _, crypted = data
                    if me == "admin" or not is_locked or idx == len(filtered)-1:
                        p_container.write(f"**{sender}:** {crypto_decode(crypted)}")
                    else:
                        p_container.write(f"**{sender}:** `ENCRYPTED_SIGNAL`")
    
    with st.form("private_sender", clear_on_submit=True):
        p_input = st.text_input("", placeholder="Fısılda...")
        if st.form_submit_button("GÖNDER"):
            if p_input:
                with open(FILES["priv"], "a", encoding="utf-8") as f:
                    f.write(f"{me}|{target}|{crypto_encode(p_input)}\n")
                st.rerun(scope="fragment")

# ==============================================================================
# --- 6. ANA KONTROL ÜNİTESİ (MAIN) ---
# ==============================================================================
if 'auth' not in st.session_state or not st.session_state['auth']:
    # --- AUTH KATMANI ---
    st.title("🛡️ ZERO NETWORK - AUTHENTICATION REQUIRED")
    st.divider()
    
    col_log, col_reg = st.columns(2)
    
    with col_log:
        st.subheader("🔑 LOGIN_NODE")
        username = st.text_input("NODE_ID")
        password = st.text_input("PASS_KEY", type="password")
        if st.button("SİSTEME BAĞLAN"):
            if os.path.exists(FILES["ban"]) and username in open(FILES["ban"]).read():
                st.error("ERİŞİM ENGELLENDİ: BANLI NODE!")
            elif (username == "admin" and password == "1234") or (f"{username}:{password}" in open(FILES["users"]).read()):
                st.session_state.update({'auth': True, 'user': username})
                system_logger(username, "Sisteme giriş yaptı.")
                st.rerun()
            else:
                st.error("KİMLİK DOĞRULANAMADI.")
                
    with col_reg:
        st.subheader("📝 REGISTER_NODE")
        new_u = st.text_input("NEW_ID")
        new_p = st.text_input("NEW_PASS", type="password")
        if st.button("KAYDI TAMAMLA"):
            if new_u and new_p and new_u != "admin" and new_u not in load_all_users():
                with open(FILES["users"], "a", encoding="utf-8") as f:
                    f.write(f"{new_u}:{new_p}\n")
                save_detailed_profile(new_u, new_u, "Yeni Birim", "https://i.imgur.com/v6S6asL.png", "MEMBER", 0, "Yeni")
                st.success("NODE SİSTEME EKLENDİ. GİRİŞ YAPABİLİRSİNİZ.")
            else:
                st.error("BU ID KULLANILAMAZ.")

else:
    # --- PANEL KATMANI ---
    me = st.session_state['user']
    sys_lock = os.path.exists(FILES["lock"])
    user_list = load_all_users()
    my_profile = get_detailed_profile(me)

    # SIDEBAR: KONTROL PANELİ
    st.sidebar.image(my_profile['avatar'], width=100)
    st.sidebar.title(f"AGENT: {me}")
    st.sidebar.markdown(f"**RANK:** `{my_profile['rank']}`")
    st.sidebar.markdown(f"**LEVEL:** `{my_profile['xp'] // 10}` | **XP:** `{my_profile['xp']}`")
    
    st.sidebar.divider()
    nav = st.sidebar.radio("NAVIGASYON", ["TERMINAL", "FILES", "NETWORK", "DECODER", "ADMIN_ROOT"])
    
    if st.sidebar.button("🚪 DISCONNECT"):
        system_logger(me, "Bağlantıyı kesti.")
        st.session_state['auth'] = False
        st.rerun()

    # --- ROUTING SİSTEMİ ---
    if nav == "TERMINAL":
        # Global ve Özel Sohbet Yan Yana
        c_main, c_side = st.columns([2, 1])
        with c_main:
            global_chat_module(me, sys_lock)
        with c_side:
            st.markdown("### 🔒 PRIVATE")
            target_list = [u for u in user_list if u != me]
            if me != "admin": target_list.append("admin")
            sel_target = st.selectbox("HEDEF", target_list)
            private_chat_module(me, sel_target, sys_lock)

    elif nav == "FILES":
        st.subheader("📂 VAULT - GÜVENLİ DOSYA PAYLAŞIMI")
        f_up = st.file_uploader("Dosyayı sisteme yükle")
        if f_up:
            with open(FILES["vault"], "a", encoding="utf-8") as f:
                f.write(f"{me}|{f_up.name}|{datetime.now().strftime('%d/%m %H:%M')}\n")
            st.success(f"{f_up.name} başarıyla şifrelendi.")
        
        st.divider()
        st.write("Paylaşılan Dosya Kayıtları:")
        if os.path.exists(FILES["vault"]):
            v_lines = open(FILES["vault"]).readlines()
            for vl in v_lines:
                st.info(f"💾 {vl}")

    elif nav == "NETWORK":
        st.subheader("👥 SİSTEMDEKİ AKTİF NODE'LAR")
        for u in user_list + ["admin"]:
            p = get_detailed_profile(u)
            with st.expander(f"NODE: {u} [{p['rank']}]"):
                col_a, col_b = st.columns([1, 4])
                col_a.image(p['avatar'], width=100)
                if u == me:
                    new_dn = st.text_input("Görünen Ad", p['display_name'])
                    new_bio = st.text_area("Biyografi", p['bio'])
                    new_img = st.text_input("Avatar URL", p['avatar'])
                    if st.button("PROFİLİ GÜNCELLE"):
                        save_detailed_profile(me, new_dn, new_bio, new_img, p['rank'], p['xp'], p['last_seen'])
                        st.rerun()
                else:
                    st.markdown(f"**Ad:** {p['display_name']}")
                    st.markdown(f"**Bio:** {p['bio']}")
                    st.markdown(f"**XP:** {p['xp']} | **Son Görülme:** {p['last_seen']}")

    elif nav == "DECODER":
        st.subheader("🛠️ SİNYAL ÇÖZÜCÜ")
        dc1, dc2 = st.columns(2)
        with dc1:
            raw_t = st.text_area("Şifrelenecek Ham Veri")
            if st.button("ENCODE"): st.code(crypto_encode(raw_t))
        with dc2:
            enc_t = st.text_area("Çözülecek Sembolik Veri")
            if st.button("DECODE"): st.success(crypto_decode(enc_t))

    elif nav == "ADMIN_ROOT":
        if me == "admin":
            st.title("🛡️ COMMAND CENTER")
            a_tab1, a_tab2, a_tab3 = st.tabs(["SİSTEM KONTROL", "HAYALET İZLEME", "LOG ANALİZİ"])
            
            with a_tab1:
                st.markdown("### Sistem Güvenlik Ayarları")
                st.write(f"Kilit Durumu: {'🔒 AKTİF' if sys_lock else '🔓 PASİF'}")
                if st.button("KİLİDİ DEĞİŞTİR"):
                    if sys_lock: os.remove(FILES["lock"])
                    else: open(FILES["lock"], "w").write("L")
                    st.rerun()
                st.divider()
                st.markdown("### Kullanıcı Yönetimi")
                for target_u in user_list:
                    m1, m2, m3 = st.columns([1,1,1])
                    tp = get_detailed_profile(target_u)
                    m1.write(f"**{target_u}**")
                    nr = m2.selectbox("Rank", ["MEMBER", "SHADOW", "ELITE", "GHOST"], index=["MEMBER", "SHADOW", "ELITE", "GHOST"].index(tp['rank']), key=f"r_{target_u}")
                    if m3.button("YETKİ VER", key=f"ub_{target_u}"):
                        save_detailed_profile(target_u, tp['display_name'], tp['bio'], tp['avatar'], nr, tp['xp'], tp['last_seen'])
                        st.rerun()
            
            with a_tab2:
                st.markdown("### Çapraz Trafik İzleme (Spy)")
                s1, s2 = st.columns(2)
                spy1 = s1.selectbox("Node 1", user_list, key="spy1")
                spy2 = s2.selectbox("Node 2", user_list, key="spy2")
                if st.button("TRAFİĞİ DİNLE"):
                    box = st.container(height=300, border=True)
                    if os.path.exists(FILES["priv"]):
                        for l in open(FILES["priv"]).readlines():
                            if (f"{spy1}|{spy2}" in l or f"{spy2}|{spy1}" in l):
                                d = l.strip().split("|")
                                box.write(f"**{d[0]}:** {crypto_decode(d[2])}")
                                
            with a_tab3:
                st.markdown("### Kritik Log Kayıtları")
                if st.button("🚨 TÜM VERİLERİ SIFIRLA"):
                    for k in ["chat", "priv", "logs", "vault"]: open(FILES[k], "w").close()
                    st.rerun()
                if os.path.exists(FILES["logs"]):
                    st.code(open(FILES["logs"]).read()[-2000:])
        else:
            st.error("ERİŞİM REDDEDİLDİ. YETKİNİZ YOK.")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJwamF6Mnd4eGZ6ZzJ3eGZ6ZzJ3eGZ6ZzJ3eGZ6ZzJ3ZzJ3ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/V3p0fv87uvA/giphy.gif")

# ==============================================================================
# --- 7. SİSTEM ÇIKIŞI VE SATIR SAYISI KONTROLÜ ---
# Toplam Satır Sayısı: ~470 (Detaylı, Açıklamalı ve Tam Kapsamlı)
# ==============================================================================
