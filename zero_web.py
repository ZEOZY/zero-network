import streamlit as st
import os
import random
import time
import pandas as pd
from datetime import datetime

# ==============================================================================
# --- 1. SİSTEM ÇEKİRDEĞİ VE DOSYA MİMARİSİ ---
# ==============================================================================
# Tüm veri tabanları burada tanımlanır.
DB = {
    "users": "users.txt",         # Kullanıcı verileri (Nick:Sifre)
    "chat": "ghost_chat.txt",     # Küresel veri akışı
    "priv": "private_chats.txt",  # Uçtan uca şifreli mesajlar
    "ban": "ban_list.txt",        # Yasaklı node listesi
    "warn": "warnings.txt",       # Sistem uyarı kayıtları
    "lock": "lock.txt",           # Sistem güvenlik kilidi durumu
    "profs": "profiles.txt",      # Detaylı rütbe ve profil verileri
    "logs": "system_logs.txt"     # Kritik işlem logları
}

# Dosya sistemini başlat (Yoksa oluştur)
for file_key, file_path in DB.items():
    if not os.path.exists(file_path):
        with open(file_path, "a", encoding="utf-8") as f:
            pass

# ==============================================================================
# --- 2. GELİŞMİŞ ŞİFRELEME VE GÜVENLİK MOTORU ---
# ==============================================================================
# V21 Standartlarında sembolik yer değiştirme algoritması
ALFABE = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*"
SEMBOL = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'Æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']
S_MAP = dict(zip(ALFABE, SEMBOL))
C_MAP = dict(zip(SEMBOL, ALFABE))

def encrypt_core(text):
    """Metni sembolik karşılıklarına dönüştürür."""
    return "".join([S_MAP.get(char, char) for char in text])

def decrypt_core(text):
    """Sembolik metni okunabilir hale getirir."""
    return "".join([C_MAP.get(char, char) for char in text])

# ==============================================================================
# --- 3. VERİ YÖNETİM KATMANI (CRUD) ---
# ==============================================================================
def fetch_all_users():
    """Sistemdeki tüm kayıtlı kullanıcıları çeker."""
    if not os.path.exists(DB["users"]): return []
    with open(DB["users"], "r", encoding="utf-8") as f:
        return [line.strip().split(":")[0] for line in f if ":" in line]

def get_node_profile(nick):
    """Kullanıcının rütbe, biyografi ve avatar verilerini getirir."""
    default = {
        "nick": nick, "name": nick, 
        "bio": "Sistem üzerinde tanımlanmamış gölge.", 
        "img": "https://cdn-icons-png.flaticon.com/512/149/149071.png", 
        "rank": "MEMBER"
    }
    if os.path.exists(DB["profs"]):
        with open(DB["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    data = line.strip().split("|")
                    if len(data) >= 5:
                        default.update({"name": data[1], "bio": data[2], "img": data[3], "rank": data[4]})
                        break
    return default

def update_node_profile(nick, name, bio, img, rank):
    """Profil verilerini kalıcı olarak dosyaya işler."""
    lines = []
    if os.path.exists(DB["profs"]):
        with open(DB["profs"], "r", encoding="utf-8") as f: lines = f.readlines()
    
    with open(DB["profs"], "w", encoding="utf-8") as f:
        found = False
        for line in lines:
            if line.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")

def log_event(user, action):
    """Kritik sistem olaylarını kaydeder."""
    with open(DB["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] USER:{user} ACTION:{action}\n")

# ==============================================================================
# --- 4. STREAMLIT ARAYÜZ KONFİGÜRASYONU ---
# ==============================================================================
st.set_page_config(page_title="ZERO NETWORK ULTIMATE", page_icon="🥷", layout="wide")

# State Yönetimi
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'viewing' not in st.session_state: st.session_state['viewing'] = None
if 'spy_on' not in st.session_state: st.session_state['spy_on'] = None

# Custom CSS - Matrix ve Karanlık Tema Arayüzü
st.markdown("""
<style>
    .reportview-container { background: #0a0a0a; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .chat-container { 
        padding: 20px; border-radius: 15px; background: #161b22; 
        border: 1px solid #30363d; margin-bottom: 15px;
    }
    .user-tag { color: #58a6ff; font-weight: bold; }
    .rank-ghost { color: #bc8cff; font-weight: bold; border: 1px solid #bc8cff; padding: 2px 5px; border-radius: 5px; }
    .rank-admin { color: #ff7b72; font-weight: bold; text-shadow: 0 0 10px #ff7b72; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #21262d; color: white; border: 1px solid #30363d; }
    .stButton>button:hover { border-color: #8b949e; background-color: #30363d; }
    hr { border: 0; height: 1px; background: #30363d; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 5. MODÜLER FRAGMENTLAR (REAL-TIME ENGINE) ---
# ==============================================================================
@st.fragment(run_every="2s")
def render_global_chat(current_user, locked_status):
    """Küresel sohbet akışını sayfayı yenilemeden günceller."""
    st.markdown("### 🌐 Global Veri Akışı")
    display_area = st.container(height=450, border=True)
    
    if os.path.exists(DB["chat"]):
        with open(DB["chat"], "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                parts = line.strip().split("|")
                if len(parts) == 3:
                    u, m, t = parts
                    # Kilit durumunda sadece son mesaj veya admin görebilir
                    if current_user == "admin" or not locked_status or i == len(lines)-1:
                        display_area.markdown(f"**{u}:** {decrypt_core(m)} <small style='color:grey; float:right;'>{t}</small>", unsafe_allow_html=True)
                    else:
                        display_area.write(f"**{u}:** `{m}`")
    
    with st.form("global_input", clear_on_submit=True):
        msg = st.text_input("Mesaj girin...", placeholder="Protokol mesajı...")
        if st.form_submit_button("GÖNDER") and msg:
            with open(DB["chat"], "a", encoding="utf-8") as f:
                f.write(f"{current_user}|{encrypt_core(msg)}|{datetime.now().strftime('%H:%M:%S')}\n")
            st.rerun(scope="fragment")

@st.fragment(run_every="2s")
def render_private_chat(me, target, locked_status):
    """1-1 Özel mesajlaşma hattını yönetir."""
    st.markdown(f"### 🔒 {target} Hattı")
    priv_area = st.container(height=400, border=True)
    
    if os.path.exists(DB["priv"]):
        with open(DB["priv"], "r", encoding="utf-8") as f:
            lines = f.readlines()
            relevant = [l for l in lines if f"|{target}|" in l and (f"{me}|" in l or f"|{me}|" in l)]
            for i, line in enumerate(relevant):
                p = line.strip().split("|")
                if len(p) == 3:
                    if me == "admin" or not locked_status or i == len(relevant)-1:
                        priv_area.write(f"**{p[0]} ➜ {p[1]}:** {decrypt_core(p[2])}")
                    else:
                        priv_area.write(f"**{p[0]}**: `{p[2]}`")
                        
    with st.form("priv_input", clear_on_submit=True):
        p_msg = st.text_input("Özel mesaj...")
        if st.form_submit_button("FISILDA") and p_msg:
            with open(DB["priv"], "a", encoding="utf-8") as f:
                f.write(f"{me}|{target}|{encrypt_core(p_msg)}\n")
            st.rerun(scope="fragment")

# ==============================================================================
# --- 6. ANA SİSTEM MANTIĞI ---
# ==============================================================================
if not st.session_state['auth']:
    # --- GİRİŞ / KAYIT EKRANI ---
    st.title("🕵️ ZERO NETWORK - AUTH TERMINAL")
    st.warning("Sisteme erişmek için yetkilendirme gereklidir.")
    
    tab_log, tab_reg = st.tabs(["🔑 ERİŞİM", "📝 KAYIT"])
    
    with tab_log:
        u_log = st.text_input("Kullanıcı Kimliği (Nick)")
        p_log = st.text_input("Erişim Kodu (Şifre)", type="password")
        if st.button("SİSTEME GİRİŞ YAP"):
            if os.path.exists(DB["ban"]) and u_log in open(DB["ban"]).read():
                st.error("DİKKAT: BU KİMLİK SİSTEMDEN BANLANMIŞTIR!")
            elif (u_log == "admin" and p_log == "1234") or (f"{u_log}:{p_log}" in open(DB["users"]).read()):
                st.session_state.update({'auth': True, 'user': u_log})
                log_event(u_log, "Giriş Başarılı")
                st.rerun()
            else:
                st.error("GEÇERSİZ KİMLİK VEYA KOD!")

    with tab_reg:
        u_reg = st.text_input("Yeni Nick Belirle")
        p_reg = st.text_input("Yeni Şifre Belirle", type="password")
        if st.button("PROTOKOLÜ KAYDET"):
            if u_reg and p_reg and u_reg != "admin" and u_reg not in fetch_all_users():
                with open(DB["users"], "a", encoding="utf-8") as f:
                    f.write(f"{u_reg}:{p_reg}\n")
                log_event(u_reg, "Yeni Kayıt Oluşturuldu")
                st.success("Kayıt tamamlandı. Giriş sekmesine geçebilirsin.")
            else:
                st.error("Bu nick kullanılamaz veya sistemde mevcut.")

else:
    # --- PANEL EKRANI (AUTH SONRASI) ---
    me = st.session_state['user']
    sys_lock = os.path.exists(DB["lock"])
    active_nodes = fetch_all_users()

    # SIDEBAR: KULLANICI KONTROLÜ
    st.sidebar.markdown(f"### 🥷 {me}")
    my_p = get_node_profile(me)
    st.sidebar.markdown(f"**Rütbe:** `{my_p['rank']}`")
    
    if st.sidebar.button("👤 Profilimi Düzenle"):
        st.session_state['viewing'] = me
    
    st.sidebar.divider()
    st.sidebar.subheader("🌐 Aktif Node'lar")
    if st.sidebar.button("⭐ admin [ROOT]", key="side_root"):
        st.session_state['viewing'] = "admin"
        
    for node in active_nodes:
        n_p = get_node_profile(node)
        if st.sidebar.button(f"👤 {node} [{n_p['rank']}]", key=f"node_btn_{node}"):
            st.session_state['viewing'] = node
            
    st.sidebar.divider()
    if st.sidebar.button("🚪 Bağlantıyı Kopar"):
        log_event(me, "Çıkış Yapıldı")
        st.session_state['auth'] = False
        st.rerun()

    # PROFİL EDİTÖRÜ / MODAL
    if st.session_state['viewing']:
        target_node = st.session_state['viewing']
        t_p = get_node_profile(target_node)
        with st.expander(f"📁 DOSYA: {target_node}", expanded=True):
            col_img, col_info = st.columns([1, 2])
            with col_img:
                st.image(t_p['img'], use_container_width=True)
            with col_info:
                if target_node == me:
                    v_name = st.text_input("Görünen İsim", t_p['name'])
                    v_bio = st.text_area("Biyografi / Kod Adı", t_p['bio'])
                    v_img = st.text_input("Avatar URL", t_p['img'])
                    if st.button("VERİLERİ SENKRONİZE ET"):
                        update_node_profile(me, v_name, v_bio, v_img, t_p['rank'])
                        st.success("Profil güncellendi!")
                        st.rerun()
                else:
                    st.title(t_p['name'])
                    st.markdown(f"**Sınıf:** `{t_p['rank']}`")
                    st.write(t_p['bio'])
            if st.button("Dosyayı Kapat"):
                st.session_state['viewing'] = None
                st.rerun()

    # ANA ÇALIŞMA ALANI
    col_main, col_status = st.columns([3, 1])

    with col_main:
        tab_global, tab_private, tab_tools, tab_admin = st.tabs(["🌍 GLOBAL", "🔒 ÖZEL", "🛠️ TERMİNAL", "🛡️ ROOT"])
        
        with tab_global:
            render_global_chat(me, sys_lock)

        with tab_private:
            target_chat = st.selectbox("Hedef Node Seçin", [u for u in active_nodes if u != me] + (["admin"] if me != "admin" else []))
            render_private_chat(me, target_chat, sys_lock)

        with tab_tools:
            st.subheader("🛠️ Manuel Dekoder")
            c_enc, c_dec = st.columns(2)
            with c_enc:
                txt_enc = st.text_area("Şifrelenecek Metin")
                if st.button("KODLA"): st.code(encrypt_core(txt_enc))
            with c_dec:
                txt_dec = st.text_area("Çözülecek Semboller")
                if st.button("ÇÖZ"): st.success(decrypt_core(txt_dec))

        with tab_admin:
            if me == "admin":
                adm_1, adm_2, adm_3 = st.tabs(["🕶️ SPY", "👥 YÖNETİM", "🔍 ANALİZ"])
                with adm_1:
                    st.subheader("Hayalet İzleme Modu")
                    s_c1, s_c2 = st.columns(2)
                    spy_u1 = s_c1.selectbox("Node A", active_nodes, key="spy1")
                    spy_u2 = s_c2.selectbox("Node B", active_nodes, key="spy2")
                    if st.button("TRAFİĞİ İZLE"): st.session_state['spy_on'] = (spy_u1, spy_u2)
                    if st.session_state['spy_on']:
                        u1, u2 = st.session_state['spy_on']
                        st.error(f"İzleme Aktif: {u1} <-> {u2}")
                        spy_box = st.container(height=200, border=True)
                        if os.path.exists(DB["priv"]):
                            for l in open(DB["priv"]).readlines():
                                if (f"{u1}|{u2}|" in l or f"{u2}|{u1}|" in l):
                                    d = l.strip().split("|")
                                    if len(d)==3: spy_box.write(f"**{d[0]}**: {decrypt_core(d[2])}")
                with adm_2:
                    st.subheader("Kullanıcı Rütbe ve Ban Sistemi")
                    for node_m in active_nodes:
                        m_1, m_2, m_3 = st.columns([1, 1, 1])
                        curr_p = get_node_profile(node_m)
                        m_1.write(f"**{node_m}**")
                        new_rk = m_2.selectbox("Rütbe", ["MEMBER", "SHADOW", "ELITE", "GHOST"], 
                                               index=["MEMBER", "SHADOW", "ELITE", "GHOST"].index(curr_p['rank']), 
                                               key=f"rk_sel_{node_m}")
                        if m_2.button("ATA", key=f"rk_btn_{node_m}"):
                            update_node_profile(node_m, curr_p['name'], curr_p['bio'], curr_p['img'], new_rk)
                            st.rerun()
                        if m_3.button("BANLA", key=f"ban_btn_{node_m}"):
                            with open(DB["ban"], "a") as f: f.write(node_m+"\n")
                            log_event("admin", f"{node_m} banlandı")
                            st.rerun()
                with adm_3:
                    st.subheader("Kritik Veri Analizi")
                    if st.button("🚨 TÜM TRAFİĞİ TEMİZLE"):
                        open(DB["chat"], "w").close(); open(DB["priv"], "w").close()
                        st.rerun()
                    st.write("Sistem Logları:")
                    st.code(open(DB["logs"]).read()[-500:]) # Son 500 karakter
            else:
                st.info("Bu alan sadece ROOT yetkisine sahip kullanıcılar içindir.")
                st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJwamF6Mnd4eGZ6ZzJ3eGZ6ZzJ3eGZ6ZzJ3eGZ6ZzJ3ZzJ3ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/V3p0fv87uvA/giphy.gif")

    with col_status:
        st.markdown("### 📡 Sistem")
        st.metric("Durum", "ONLINE" if not sys_lock else "LOCKED")
        if me == "admin":
            if st.button("KİLİDİ ÇEVİR"):
                if sys_lock: os.remove(DB["lock"])
                else: open(DB["lock"], "w").write("LOCK")
                log_event("admin", "Sistem kilidi değiştirildi")
                st.rerun()
        st.divider()
        st.markdown("**Node Bilgisi:**")
        st.caption(f"IP: {random.randint(100,255)}.{random.randint(0,255)}.0.1")
        st.caption(f"Zaman: {datetime.now().strftime('%H:%M:%S')}")

# FINAL: Uygulama asla kapanmaz, fragmentlar kendi içinde döner.
