import streamlit as st
import os
import random
import time
from datetime import datetime

# ==============================================================================
# --- 1. VERİTABANI VE DOSYA SİSTEMİ ÇEKİRDEĞİ ---
# ==============================================================================
FILES = {
    "users": "users.txt",       # Nick:Sifre
    "chat": "ghost_chat.txt",   # Nick|SifreliMesaj|Saat
    "priv": "private_chats.txt",# Kimden|Kime|SifreliMesaj
    "ban": "ban_list.txt",      # Banlananlar
    "warn": "warnings.txt",     # Uyarılar
    "lock": "lock.txt",         # Sistem Kilidi
    "profs": "profiles.txt"     # Nick|Ad|Bio|Foto|Rutbe
}

# Dosyaları sessizce oluştur
for f_path in FILES.values():
    if not os.path.exists(f_path):
        with open(f_path, "a", encoding="utf-8") as f:
            pass

# ==============================================================================
# --- 2. GELİŞMİŞ ŞİFRELEME MOTORU (V21+ STANDARTI) ---
# ==============================================================================
ALFABE = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*"
SEMBOL = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'Æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']
S_DICT = dict(zip(ALFABE, SEMBOL))
C_DICT = dict(zip(SEMBOL, ALFABE))

def sifrele(metin):
    return "".join([S_DICT.get(k, k) for k in metin])

def coz(metin):
    return "".join([C_DICT.get(k, k) for k in metin])

# ==============================================================================
# --- 3. VERİ YÖNETİM FONKSİYONLARI ---
# ==============================================================================
def get_all_users():
    if not os.path.exists(FILES["users"]): return []
    with open(FILES["users"], "r", encoding="utf-8") as f:
        return [l.strip().split(":")[0] for l in f if ":" in l]

def get_profile(nick):
    p_data = {
        "nick": nick, "name": nick, 
        "bio": "Bu kullanıcı bir gölge.", 
        "img": "https://cdn-icons-png.flaticon.com/512/149/149071.png", 
        "rank": "MEMBER"
    }
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    d = line.strip().split("|")
                    if len(d) >= 5:
                        p_data.update({"name": d[1], "bio": d[2], "img": d[3], "rank": d[4]})
                        break
    return p_data

def save_profile(nick, name, bio, img, rank):
    lines = []
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f: lines = f.readlines()
    with open(FILES["profs"], "w", encoding="utf-8") as f:
        found = False
        for l in lines:
            if l.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")
                found = True
            else: f.write(l)
        if not found: f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")

# ==============================================================================
# --- 4. STREAMLIT ARAYÜZ VE SESSION AYARLARI ---
# ==============================================================================
st.set_page_config(page_title="ZERO NETWORK V28", page_icon="🥷", layout="wide")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'viewing_profile' not in st.session_state: st.session_state['viewing_profile'] = None
if 'spy_target' not in st.session_state: st.session_state['spy_target'] = None

# CSS - Arayüzü Güzelleştir
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #1a1c23; color: white; border: 1px solid #3d4451; }
    .chat-bubble { padding: 10px; border-radius: 10px; margin-bottom: 5px; background-color: #23272f; border-left: 5px solid #4a9eff; }
    .admin-bubble { padding: 10px; border-radius: 10px; margin-bottom: 5px; background-color: #2d1b1b; border-left: 5px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 5. GİRİŞ KONTROL PANELİ ---
# ==============================================================================
if not st.session_state['auth']:
    st.title("📡 ZERO NETWORK - BAĞLANTI TERMİNALİ")
    st.info("Erişim için kimlik doğrulaması gerekiyor...")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔑 Giriş Yap")
        u_in = st.text_input("Nick")
        p_in = st.text_input("Şifre", type="password")
        if st.button("SİSTEME SIZ"):
            if os.path.exists(FILES["ban"]) and u_in in open(FILES["ban"]).read():
                st.error("ERİŞİM ENGELLENDİ: BANLANDIN!")
            elif (u_in == "admin" and p_in == "1234") or (f"{u_in}:{p_in}" in open(FILES["users"]).read()):
                st.session_state.update({'auth': True, 'user': u_in})
                st.rerun()
            else: st.error("KİMLİK GEÇERSİZ!")

    with col2:
        st.subheader("📝 Yeni Protokol")
        nu_in = st.text_input("Yeni Kullanıcı Adı")
        np_in = st.text_input("Şifre Belirle", type="password")
        if st.button("KAYDI TAMAMLA"):
            if nu_in and np_in and nu_in != "admin" and nu_in not in get_all_users():
                with open(FILES["users"], "a", encoding="utf-8") as f:
                    f.write(f"{nu_in}:{np_in}\n")
                st.success("Kayıt Başarılı! Artık giriş yapabilirsin.")
            else: st.error("Bu nick kullanılamaz.")

# ==============================================================================
# --- 6. ANA SİSTEM PANELİ (GİRİŞ YAPILDIKTAN SONRA) ---
# ==============================================================================
else:
    me = st.session_state['user']
    is_locked = os.path.exists(FILES["lock"])
    all_users = get_all_users()

    # --- SIDEBAR: KULLANICI VE DURUM ---
    st.sidebar.title(f"🥷 {me}")
    my_p = get_profile(me)
    st.sidebar.markdown(f"**Rütbe:** `{my_p['rank']}`")
    
    if st.sidebar.button("⚙️ Profil Ayarlarım"):
        st.session_state['viewing_profile'] = me

    st.sidebar.divider()
    st.sidebar.subheader("👥 Node'lar")
    # Admin her zaman en üstte
    if st.sidebar.button(f"⭐ admin [ROOT]", key="side_admin"):
        st.session_state['viewing_profile'] = "admin"
        
    for user_node in all_users:
        u_prof = get_profile(user_node)
        if st.sidebar.button(f"👤 {u_prof['name']} [{u_prof['rank']}]", key=f"btn_{user_node}"):
            st.session_state['viewing_profile'] = user_node
    
    st.sidebar.divider()
    auto_refresh = st.sidebar.toggle("Canlı Akış (3s)", value=True)
    if st.sidebar.button("🚪 Bağlantıyı Kes"):
        st.session_state['auth'] = False
        st.rerun()

    # --- PROFİL MODAL / EDİTÖR ---
    if st.session_state['viewing_profile']:
        target = st.session_state['viewing_profile']
        pd = get_profile(target)
        with st.expander(f"📂 KULLANICI DOSYASI: {target}", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(pd['img'], use_container_width=True)
            with c2:
                if target == me:
                    st.subheader("Kimlik Bilgileri")
                    new_n = st.text_input("Görünen Ad", pd['name'])
                    new_b = st.text_area("Biyografi", pd['bio'])
                    new_i = st.text_input("Avatar URL", pd['img'])
                    if st.button("GÜNCELLE VE KAYDET"):
                        save_profile(me, new_n, new_b, new_i, pd['rank'])
                        st.success("Veriler güncellendi!")
                        st.rerun()
                else:
                    st.title(pd['name'])
                    st.info(f"Sınıf: {pd['rank']}")
                    st.write(pd['bio'])
            if st.button("Dosyayı Kapat"):
                st.session_state['viewing_profile'] = None
                st.rerun()

    # --- ANA PANEL (V21 STİLİ GENİŞ TABLAR) ---
    main_col, info_col = st.columns([3, 1])

    with main_col:
        tabs = st.tabs(["🌍 Global Akış", "🔒 Özel Hat", "🛠️ Dekoder", "🛡️ ROOT" if me == "admin" else "Sistem"])

        with tabs[0]: # GLOBAL CHAT
            st.subheader("🌐 Global Veri Trafiği")
            g_box = st.container(height=450)
            if os.path.exists(FILES["chat"]):
                g_lines = open(FILES["chat"], "r", encoding="utf-8").readlines()
                for idx, line in enumerate(g_lines):
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        n, m, t = parts
                        # Admin veya son mesaj değilse ve kilitliyse şifreli göster
                        if me == "admin" or not is_locked or idx == len(g_lines)-1:
                            g_box.markdown(f"<div class='chat-bubble'><b>{n}:</b> {coz(m)} <small style='float:right;'>{t}</small></div>", unsafe_allow_html=True)
                        else:
                            g_box.write(f"**{n}:** `{m}`")
            
            with st.form("global_form", clear_on_submit=True):
                g_msg = st.text_input("Mesaj...")
                if st.form_submit_button("Sisteme Enjekte Et") and g_msg:
                    with open(FILES["chat"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{sifrele(g_msg)}|{datetime.now().strftime('%H:%M:%S')}\n")
                    st.rerun()

        with tabs[1]: # ÖZEL SOHBET (1-1)
            st.subheader("🔒 Gizli Kanal")
            target_user = st.selectbox("Bağlantı Kurulacak Ajan", [u for u in all_users if u != me] + (["admin"] if me != "admin" else []))
            p_box = st.container(height=350)
            if os.path.exists(FILES["priv"]):
                p_lines = open(FILES["priv"], "r", encoding="utf-8").readlines()
                filtered = [l for l in p_lines if f"|{target_user}|" in l and (f"{me}|" in l or f"|{me}|" in l)]
                for idx, line in enumerate(filtered):
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        f, t, m = parts
                        if me == "admin" or not is_locked or idx == len(filtered)-1:
                            p_box.write(f"**{f} ➔ {t}:** {coz(m)}")
                        else:
                            p_box.write(f"**{f}**: `{m}`")
            
            with st.form("private_form", clear_on_submit=True):
                p_msg = st.text_input("Gizli mesaj...")
                if st.form_submit_button("Fısılda") and p_msg:
                    with open(FILES["priv"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{target_user}|{sifrele(p_msg)}\n")
                    st.rerun()

        with tabs[2]: # ŞİFRELEME ARAÇLARI
            st.subheader("🛠️ Manuel Terminal")
            tc1, tc2 = st.columns(2)
            with tc1:
                st.write("🔒 Kodla")
                raw_t = st.text_area("Metin", key="raw_t")
                if st.button("ENCODE"): st.code(sifrele(raw_t))
            with tc2:
                st.write("🔓 Çöz")
                enc_t = st.text_area("Şifre", key="enc_t")
                if st.button("DECODE"): st.success(coz(enc_t))

        if me == "admin":
            with tabs[3]:
                at1, at2, at3 = st.tabs(["🕶️ Hayalet İzleme", "👥 Rütbe/Ban", "🔍 Veri Ayıklama"])
                with at1: # SPY SYSTEM
                    sc1, sc2 = st.columns(2)
                    sp1 = sc1.selectbox("Hedef 1", all_users, key="sp1")
                    sp2 = sc2.selectbox("Hedef 2", all_users, key="sp2")
                    if st.button("SIZ"): st.session_state['spy_target'] = (sp1, sp2)
                    if st.session_state['spy_target']:
                        u1, u2 = st.session_state['spy_target']
                        st.warning(f"DİKKAT: {u1} ve {u2} arasındaki trafik izleniyor.")
                        spy_cont = st.container(height=200, border=True)
                        for l in open(FILES["priv"]).readlines():
                            if (f"{u1}|{u2}|" in l or f"{u2}|{u1}|" in l):
                                d = l.strip().split("|")
                                if len(d)==3: spy_cont.write(f"**{d[0]}**: {coz(d[2])}")
                with at2: # USER RANK MGMT
                    for u_man in all_users:
                        m1, m2, m3 = st.columns([1,1,1])
                        u_prof = get_profile(u_man)
                        m1.write(f"**{u_man}**")
                        new_r = m2.selectbox("Sınıf", ["MEMBER", "SHADOW", "ELITE", "GHOST"], 
                                             index=["MEMBER", "SHADOW", "ELITE", "GHOST"].index(u_prof['rank']), 
                                             key=f"rk_{u_man}")
                        if m2.button("BAS", key=f"rk_btn_{u_man}"):
                            save_profile(u_man, u_prof['name'], u_prof['bio'], u_prof['img'], new_r)
                            st.rerun()
                        if m3.button("BANLA", key=f"ban_{u_man}"):
                            with open(FILES["ban"], "a") as f: f.write(u_man+"\n")
                            st.rerun()
                with at3: # MASTER DATA
                    if st.button("🚨 SİSTEMİ SIFIRLA"):
                        open(FILES["chat"], "w").close(); open(FILES["priv"], "w").close(); st.rerun()
                    st.subheader("📋 Tüm Çözülmüş Mesajlar")
                    raw_rows = []
                    if os.path.exists(FILES["priv"]):
                        for rl in open(FILES["priv"], "r", encoding="utf-8").readlines():
                            d = rl.strip().split("|")
                            if len(d) == 3: raw_rows.append({"Kimden": d[0], "Kime": d[1], "Mesaj": coz(d[2])})
                    st.table(raw_rows)

    with info_col: # SAĞ TARAF: SİSTEM PANELİ
        st.subheader("📡 Durum")
        st.write(f"Kilit: {'🔒 AKTİF' if is_locked else '🔓 PASİF'}")
        if me == "admin":
            if st.button("KİLİDİ DEĞİŞTİR"):
                if is_locked: os.remove(FILES["lock"])
                else: open(FILES["lock"], "w").write("L")
                st.rerun()
        st.divider()
        st.markdown("**Sistem Notu:**")
        st.caption("Veriler şifreli akmaktadır. 1-1 mesajlar otomatik olarak 3 saniyede bir güncellenir.")
        
    # --- KRİTİK: AUTO-SYNC TETİKLEYİCİ ---
    if auto_refresh:
        time.sleep(3)
        st.rerun()
