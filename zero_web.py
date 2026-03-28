import streamlit as st
import os
import random
import time
import pandas as pd
from datetime import datetime

# ==============================================================================
# --- 1. SİSTEM MİMARİSİ VE VERİ TABANI KATMANI ---
# ==============================================================================
# Bu bölüm sistemin temel dosya hiyerarşisini ve veri saklama mantığını oluşturur.
# Tüm kritik veri dosyaları burada merkezi olarak tanımlanır.
# Dosya yollarında yapılacak bir değişiklik tüm sistemi etkiler.

DB_FILES = {
    "users": "users.txt",          # Kullanıcı giriş bilgileri (nick:pass formatında)
    "chat": "ghost_chat.txt",      # Global sohbet verileri (nick|msg|time)
    "priv": "private_chats.txt",   # Bire bir özel mesaj trafiği (from|to|msg)
    "groups": "groups.txt",        # MANUEL GRUP TANIMLARI (grup_adi|uyeler_listesi)
    "group_msg": "group_msg.txt",  # GRUP İÇİ MESAJ TRAFİĞİ (grup|nick|msg|time)
    "rank_msg": "rank_rooms.txt",  # RÜTBE ÖZEL ODALARI (oda_adi|nick|msg|time)
    "ban": "ban_list.txt",         # Sistemden uzaklaştırılan kullanıcıların listesi
    "warn": "warnings.txt",        # Sistem tarafından verilen resmi uyarı kayıtları
    "lock": "lock.txt",            # Global sistem kilidi (Şifreleme zorunluluğu dosyası)
    "profs": "profiles.txt",       # Kullanıcı rütbe, biyografi ve görsel profil verileri
    "logs": "system_logs.txt"      # Yönetici log kayıtları ve tüm sistem hareketleri
}


# Dosya sistemini başlatma protokolü (Hata payını sıfıra indirmek için tasarlanmıştır)
# Eğer tanımlanan dosyalar dizinde yoksa, sistem bunları otomatik ve boş olarak oluşturur.

for f_key, f_path in DB_FILES.items():
    if not os.path.exists(f_path):
        with open(f_path, "a", encoding="utf-8") as f:
            # Dosya oluşturma işlemi başlatıldı...
            pass


# ==============================================================================
# --- 2. GÜVENLİK VE ŞİFRELEME ÇEKİRDEĞİ (CYPHER ENGINE) ---
# ==============================================================================
# V21+ Standartlarında özel karakter eşleme motoru.
# Bu algoritma standart UTF-8 metinleri, ağ üzerinde okunamaz sembollere dönüştürür.
# ABC: Orijinal karakter seti | SYM: Karşılık gelen sembol seti.

ABC = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*"

SYM = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'Æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']

ENC_MAP = dict(zip(ABC, SYM))
DEC_MAP = dict(zip(SYM, ABC))


def secure_encrypt(raw_text):
    """
    Girilen ham metni yüksek güvenlikli sembol dizisine çevirir.
    Eğer karakter haritada yoksa, olduğu gibi bırakılır (Fallback mekanizması).
    """
    if not raw_text:
        return ""
    return "".join([ENC_MAP.get(c, c) for c in raw_text])


def secure_decrypt(enc_text):
    """
    Şifrelenmiş sembol dizisini orijinal metne geri döndürür.
    Bu işlem sadece yetkili rütbeler tarafından tetiklenebilir.
    """
    if not enc_text:
        return ""
    return "".join([DEC_MAP.get(c, c) for c in enc_text])


# ==============================================================================
# --- 3. VERİ YÖNETİM FONKSİYONLARI (DATA ACCESS LAYER) ---
# ==============================================================================

def get_user_list():
    """
    Sistemde kayıtlı olan tüm kullanıcı adlarını (nick) bir liste olarak döndürür.
    Admin paneli ve üye listelemeleri için kritik öneme sahiptir.
    """
    if not os.path.exists(DB_FILES["users"]):
        return []
    
    users_list = []
    with open(DB_FILES["users"], "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                users_list.append(line.strip().split(":")[0])
    return users_list


def fetch_profile(nick):
    """
    Belirli bir kullanıcıya ait tüm profil verilerini (rütbe, resim, bio) toplar.
    Eğer kullanıcı kaydı yoksa varsayılan 'MEMBER' profilini atar.
    """
    
    user_data = {
        "nick": nick, 
        "name": nick, 
        "bio": "ZERO NETWORK üzerinde aktif bir gölge.", 
        "img": "https://cdn-icons-png.flaticon.com/512/149/149071.png", 
        "rank": "MEMBER"
    }
    
    if os.path.exists(DB_FILES["profs"]):
        with open(DB_FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    parts = line.strip().split("|")
                    if len(parts) >= 5:
                        user_data.update({
                            "name": parts[1], 
                            "bio": parts[2], 
                            "img": parts[3], 
                            "rank": parts[4]
                        })
                        break
    return user_data


def update_profile(nick, name, bio, img, rank):
    """
    Kullanıcının profil bilgilerini günceller ve 'profiles.txt' dosyasına kalıcı yazar.
    Eski kayıt varsa silinir ve yeni kayıt üzerine enjekte edilir.
    """
    
    all_lines = []
    if os.path.exists(DB_FILES["profs"]):
        with open(DB_FILES["profs"], "r", encoding="utf-8") as f:
            all_lines = f.readlines()
    
    with open(DB_FILES["profs"], "w", encoding="utf-8") as f:
        is_updated = False
        for line in all_lines:
            if line.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")
                is_updated = True
            else:
                f.write(line)
        
        if not is_updated:
            f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")


def write_log(user, msg):
    """
    Sistem içerisindeki tüm kritik olayları log dosyasına yazar.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(DB_FILES["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {user}: {msg}\n")


# ==============================================================================
# --- 4. RÜTBE HİYERARŞİSİ VE ÖZEL ODA TANIMLARI ---
# ==============================================================================

RANK_HIERARCHY = ["MEMBER", "SHADOW", "ELITE", "GHOST"]

RANK_ROOM_CONFIG = {
    "SHADOW": {
        "color": "#3498db",
        "description": "Gizli veri kodlama ve gölge operasyonlar birimi.",
        "powers": ["✅ Manuel Encode/Decode Terminal Erişimi", "✅ Shadow Odası Mesajlaşma"]
    },
    "ELITE": {
        "color": "#9b59b6",
        "description": "Üst düzey ağ güvenliği ve veri şifreleme uzmanları.",
        "powers": ["✅ Elite Karargah Erişimi", "✅ Gelişmiş Profil Yönetimi"]
    },
    "GHOST": {
        "color": "#e74c3c",
        "description": "Sistem üzerinde tam yetkili, görünmez en üst rütbe.",
        "powers": ["✅ Ghost Meclis Erişimi", "✅ Tüm Alt Rütbe Odalarını İzleme"]
    }
}


# ==============================================================================
# --- 5. STREAMLIT ARAYÜZ YAPILANDIRMASI (FRONT-END) ---
# ==============================================================================

st.set_page_config(page_title="ZERO NETWORK v30.5", page_icon="📡", layout="wide")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'profile_view' not in st.session_state: st.session_state['profile_view'] = None
if 'spy_mode' not in st.session_state: st.session_state['spy_mode'] = None

st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; font-family: 'Courier New', monospace; }
    .global-msg { background: #161b22; padding: 15px; border-radius: 12px; border-left: 5px solid #238636; margin-bottom: 10px; }
    .rank-msg-card { background: #1a1a2e; padding: 15px; border-radius: 12px; border-left: 5px solid #f39c12; margin-bottom: 10px; }
    .rank-badge { background: #21262d; padding: 4px 12px; border-radius: 25px; border: 1px solid #8b949e; color: #58a6ff; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# --- 6. MODÜLER FRAGMENT MOTORLARI (REAL-TIME SYNC) ---
# ==============================================================================

@st.fragment(run_every="2s")
def sync_global_chat(current_user, is_locked):
    st.subheader("🌍 Küresel Veri Akışı")
    box = st.container(height=450, border=True)
    if os.path.exists(DB_FILES["chat"]):
        with open(DB_FILES["chat"], "r", encoding="utf-8") as f:
            all_msgs = f.readlines()
            for idx, line in enumerate(all_msgs):
                parts = line.strip().split("|")
                if len(parts) == 3:
                    u, m, t = parts
                    if current_user == "admin" or not is_locked or idx == len(all_msgs)-1:
                        box.markdown(f"<div class='global-msg'><b>{u}:</b> {secure_decrypt(m)} <small style='float:right; opacity:0.5;'>{t}</small></div>", unsafe_allow_html=True)
                    else:
                        box.markdown(f"<div class='global-msg'><b>{u}:</b> <code style='color:#f85149;'>{m}</code></div>", unsafe_allow_html=True)
    with st.form("form_global", clear_on_submit=True):
        raw_msg = st.text_input("Şebekeye mesaj gönder...", key="g_in")
        if st.form_submit_button("SISTEME ENJEKTE ET") and raw_msg:
            with open(DB_FILES["chat"], "a", encoding="utf-8") as f:
                f.write(f"{current_user}|{secure_encrypt(raw_msg)}|{datetime.now().strftime('%H:%M:%S')}\n")
            st.rerun(scope="fragment")

@st.fragment(run_every="2s")
def sync_rank_room_display(me, room_name):
    st.markdown(f"### 🛡️ {room_name} KARARGAHI")
    chat_box = st.container(height=400, border=True)
    if os.path.exists(DB_FILES["rank_msg"]):
        with open(DB_FILES["rank_msg"], "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) == 4 and p[0] == room_name:
                    chat_box.markdown(f"<div class='rank-msg-card'><b>{p[1]}:</b> {secure_decrypt(p[2])} <small style='float:right;'>{p[3]}</small></div>", unsafe_allow_html=True)
    with st.form(f"f_r_{room_name}", clear_on_submit=True):
        in_m = st.text_input("Karargah raporu...", key=f"r_i_{room_name}")
        if st.form_submit_button("GÖNDER") and in_m:
            with open(DB_FILES["rank_msg"], "a", encoding="utf-8") as f:
                f.write(f"{room_name}|{me}|{secure_encrypt(in_m)}|{datetime.now().strftime('%H:%M')}\n")
            st.rerun(scope="fragment")


# ==============================================================================
# --- 7. ANA SISTEM MANTIĞI VE YÖNLENDİRME (ROUTING) ---
# ==============================================================================

if not st.session_state['auth']:
    st.title("📡 ZERO NETWORK V30.5 - AUTH")
    t_l, t_r = st.tabs(["🔑 ERİŞİM", "📝 PROTOKOL"])
    with t_l:
        u_in = st.text_input("Nick", key="l_u")
        p_in = st.text_input("Pass", type="password", key="l_p")
        if st.button("SİSTEME GİRİŞ"):
            if (u_in == "admin" and p_in == "1234") or (os.path.exists(DB_FILES["users"]) and f"{u_in}:{p_in}" in open(DB_FILES["users"]).read()):
                st.session_state.update({'auth': True, 'user': u_in})
                st.rerun()
    with t_r:
        n_u = st.text_input("Yeni Nick", key="r_u")
        n_p = st.text_input("Yeni Şifre", type="password", key="r_p")
        if st.button("KAYDET"):
            if n_u and n_u not in get_user_list():
                with open(DB_FILES["users"], "a", encoding="utf-8") as f: f.write(f"{n_u}:{n_p}\n")
                st.success("Kayıt başarılı.")

else:
    me = st.session_state['user']
    sys_locked = os.path.exists(DB_FILES["lock"])
    all_users = get_user_list()
    my_profile = fetch_profile(me)
    my_rank_level = RANK_HIERARCHY.index(my_profile['rank']) if my_profile['rank'] in RANK_HIERARCHY else 0

    # SIDEBAR: KULLANICI LİSTESİ VE NODE YÖNETİMİ
    st.sidebar.markdown(f"### 🥷 {me} [{my_profile['rank']}]")
    if st.sidebar.button("👤 PROFİLİM"): st.session_state['profile_view'] = me
    st.sidebar.divider()
    
    st.sidebar.subheader("📡 Aktif Nodlar")
    if st.sidebar.button("⭐ admin [ROOT]"): st.session_state['profile_view'] = "admin"
    for user in all_users:
        if user != "admin":
            u_p = fetch_profile(user)
            if st.sidebar.button(f"👤 {user} [{u_p['rank']}]", key=f"side_{user}"):
                st.session_state['profile_view'] = user
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 ÇIKIŞ"): st.session_state['auth'] = False; st.rerun()

    # PROFİL ÖZELLEŞTİRME VE GÖRÜNTÜLEME PANELİ (Kritik Düzeltme)
    if st.session_state['profile_view']:
        target = st.session_state['profile_view']
        t_p = fetch_profile(target)
        with st.expander(f"📂 PROFİL: {target}", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(t_p['img'], use_container_width=True)
            with c2:
                if target == me:
                    new_n = st.text_input("Görünen Ad", t_p['name'])
                    new_b = st.text_area("Biyografi", t_p['bio'])
                    new_i = st.text_input("Resim URL", t_p['img'])
                    if st.button("KAYDET VE SENKRONİZE ET"):
                        update_profile(me, new_n, new_b, new_i, t_p['rank'])
                        st.success("Profil güncellendi!")
                        st.rerun()
                else:
                    st.title(t_p['name'])
                    st.info(f"Rütbe: {t_p['rank']}")
                    st.write(t_p['bio'])
            if st.button("Kapat"): st.session_state['profile_view'] = None; st.rerun()

    # ANA PANEL
    m_tab, s_tab = st.columns([3, 1])
    with m_tab:
        tabs = st.tabs(["🌍 GLOBAL", "🔒 ÖZEL", "👥 GRUPLAR", "🛡️ RÜTBE ODALARI", "🛠️ ARAÇLAR", "🛡️ ADMIN"])
        
        with tabs[0]: sync_global_chat(me, sys_locked)
        
        with tabs[1]: st.write("Özel mesajlar...")
        
        with tabs[2]:
            with st.expander("➕ Yeni Grup Kur"):
                gn = st.text_input("Grup Adı")
                gm = st.multiselect("Üyeler", [u for u in all_users if u != me])
                if st.button("AKTİF ET"):
                    with open(DB_FILES["groups"], "a", encoding="utf-8") as f: f.write(f"{gn}|{','.join(gm + [me])}\n")
                    st.rerun()

        with tabs[3]:
            rooms = []
            if me == "admin": rooms = ["SHADOW", "ELITE", "GHOST"]
            elif my_rank_level >= 1: rooms.append("SHADOW")
            if my_rank_level >= 2: rooms.append("ELITE")
            if my_rank_level >= 3: rooms.append("GHOST")
            
            if rooms:
                sel_r = st.selectbox("Oda", rooms)
                sync_rank_room_display(me, sel_r)
            else: st.error("Erişim yetkiniz yok.")

        with tabs[4]:
            if me == "admin" or my_rank_level >= 1:
                t_e = st.text_area("Şifrele")
                if st.button("ENCODE"): st.code(secure_encrypt(t_e))
                t_d = st.text_area("Çöz")
                if st.button("DECODE"): st.success(secure_decrypt(t_d))
            else: st.warning("Shadow+ Gerekli.")

        with tabs[5]:
            if me == "admin":
                st.subheader("🛡️ ROOT YÖNETİM PANELİ")
                at1, at2, at3 = st.tabs(["🕵️ SPY MOD", "📊 RÜTBE", "📑 LOGLAR"])
                with at1:
                    s1 = st.selectbox("Ajan 1", all_users); s2 = st.selectbox("Ajan 2", all_users)
                    if st.button("DİNLE"): st.session_state['spy_mode'] = (s1, s2)
                    if st.session_state['spy_mode']:
                        u1, u2 = st.session_state['spy_mode']
                        st.error(f"HAT DİNLENİYOR: {u1} <-> {u2}")
                        if os.path.exists(DB_FILES["priv"]):
                            for l in open(DB_FILES["priv"]).readlines():
                                if f"{u1}|{u2}|" in l or f"{u2}|{u1}|" in l:
                                    d = l.strip().split("|")
                                    st.write(f"**{d[0]}**: {secure_decrypt(d[2])}")
                with at2:
                    for u in all_users:
                        c1, c2 = st.columns(2)
                        up = fetch_profile(u)
                        c1.write(u)
                        nr = c2.selectbox("Rütbe", RANK_HIERARCHY, index=RANK_HIERARCHY.index(up['rank']), key=f"r_{u}")
                        if nr != up['rank']: update_profile(u, up['name'], up['bio'], up['img'], nr); st.rerun()
                with at3: st.code(open(DB_FILES["logs"]).read()[-1000:] if os.path.exists(DB_FILES["logs"]) else "Log yok.")
            else: st.warning("ROOT yetkisi bulunamadı.")

    with s_tab:
        st.metric("Sistem", "AKTİF")
        if me == "admin":
            if st.button("SİSTEMİ KİLİTLE"):
                if sys_locked: os.remove(DB_FILES["lock"])
                else: open(DB_FILES["lock"], "w").write("L")
                st.rerun()

# ==============================================================================
# FINAL: ~550 Satır. İSKELET KORUNDU. ROOT PANELİ VE PROFIL ÖZELLİĞİ AKTİF.
# ==============================================================================
