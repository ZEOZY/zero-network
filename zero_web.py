import streamlit as st
import os
import random
import time
from datetime import datetime

# --- 1. DOSYA SİSTEMİ ÇEKİRDEĞİ ---
FILES = {
    "users": "users.txt",
    "chat": "ghost_chat.txt",
    "priv": "private_chats.txt",
    "ban": "ban_list.txt",
    "warn": "warnings.txt",
    "lock": "lock.txt",
    "profs": "profiles.txt"
}

for f_path in FILES.values():
    if not os.path.exists(f_path):
        open(f_path, "a", encoding="utf-8").close()

# --- 2. ŞİFRELEME MOTORU (V21 STANDARTI) ---
ALFABE = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuÜvyz 0123456789.,!?+-/*"
SEMBOL = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'Æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']
S_DICT = dict(zip(ALFABE, SEMBOL)); C_DICT = dict(zip(SEMBOL, ALFABE))

def sifrele(m): return "".join([S_DICT.get(k, k) for k in m])
def coz(m): return "".join([C_DICT.get(k, k) for k in m])

# --- 3. VERİ YÖNETİMİ ---
def get_all_users():
    with open(FILES["users"], "r", encoding="utf-8") as f:
        return [l.strip().split(":")[0] for l in f if ":" in l]

def get_profile(nick):
    p = {"nick": nick, "name": nick, "bio": "Sistem Üyesi", "img": "https://cdn-icons-png.flaticon.com/512/149/149071.png", "rank": "MEMBER"}
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    d = line.strip().split("|")
                    if len(d) >= 5: p.update({"name": d[1], "bio": d[2], "img": d[3], "rank": d[4]})
    return p

def save_profile(nick, name, bio, img, rank="MEMBER"):
    lines = []
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f: lines = f.readlines()
    with open(FILES["profs"], "w", encoding="utf-8") as f:
        found = False
        for l in lines:
            if l.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n"); found = True
            else: f.write(l)
        if not found: f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")

# --- 4. SESSION BAŞLATMA ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'viewing_profile' not in st.session_state: st.session_state['viewing_profile'] = None
if 'spy_target' not in st.session_state: st.session_state['spy_target'] = None

st.set_page_config(page_title="ZERO NETWORK V26.5", page_icon="🕵️", layout="wide")

# --- GİRİŞ / KAYIT ---
if not st.session_state['auth']:
    st.title("📡 ZERO NETWORK - BAĞLANTI TERMİNALİ")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔑 Giriş")
        u = st.text_input("Nick")
        p = st.text_input("Şifre", type="password")
        if st.button("SİSTEME SIZ"):
            if (u=="admin" and p=="1234") or (f"{u}:{p}" in open(FILES["users"]).read()):
                st.session_state.update({'auth': True, 'user': u}); st.rerun()
            else: st.error("Erişim Reddedildi!")
    with c2:
        st.subheader("📝 Kayıt")
        nu = st.text_input("Yeni Nick"); np = st.text_input("Yeni Şifre", type="password")
        if st.button("PROTOKOLÜ BAŞLAT"):
            if nu and np and nu not in get_all_users():
                with open(FILES["users"], "a", encoding="utf-8") as f: f.write(f"{nu}:{np}\n")
                st.success("Kaydedildi!"); st.rerun()

# --- ANA SİSTEM ---
else:
    me = st.session_state['user']
    locked = os.path.exists(FILES["lock"])
    all_u = get_all_users()

    # SIDEBAR
    st.sidebar.title(f"🥷 {me}")
    if st.sidebar.button("⚙️ Profilimi Düzenle"): st.session_state['viewing_profile'] = me
    st.sidebar.divider()
    
    st.sidebar.subheader("👥 Bağlı Node'lar")
    st.sidebar.write("⭐ admin [ROOT]")
    for un in all_u:
        up = get_profile(un)
        if st.sidebar.button(f"👤 {un} [{up['rank']}]", key=f"side_{un}"): st.session_state['viewing_profile'] = un
    
    st.sidebar.divider()
    # OTO-YENİLEME KONTROLÜ
    auto_ref = st.sidebar.toggle("Canlı Akış (5s)", value=True)
    if st.sidebar.button("🚪 Bağlantıyı Kes"): st.session_state['auth'] = False; st.rerun()

    # PROFİL GÖRÜNTÜLEYİCİ
    if st.session_state['viewing_profile']:
        target = st.session_state['viewing_profile']; pd = get_profile(target)
        with st.expander(f"📂 Dosya: {target}", expanded=True):
            pc1, pc2 = st.columns([1, 2])
            with pc1: st.image(pd['img'], width=150)
            with pc2:
                if target == me:
                    nn = st.text_input("Görünen Ad", pd['name']); nb = st.text_area("Bio", pd['bio']); ni = st.text_input("Avatar URL", pd['img'])
                    if st.button("VERİLERİ GÜNCELLE"): save_profile(me, nn, nb, ni, pd['rank']); st.rerun()
                else:
                    st.title(pd['name']); st.write(f"**Rank:** {pd['rank']}"); st.write(pd['bio'])
            if st.button("Kapat"): st.session_state['viewing_profile'] = None; st.rerun()

    # ANA PANEL
    m_col, r_col = st.columns([3, 1])
    
    with m_col:
        tabs = st.tabs(["🌍 Global Veri", "🔒 Özel Kanal", "🛠️ Araçlar", "🛡️ Admin" if me == "admin" else "Sistem"])
        
        with tabs[0]: # GLOBAL CHAT
            st.subheader("🌐 Global Veri Akışı")
            g_cont = st.container(height=400)
            if os.path.exists(FILES["chat"]):
                lines = open(FILES["chat"], "r", encoding="utf-8").readlines()
                for idx, l in enumerate(lines):
                    parts = l.strip().split("|")
                    if len(parts) == 3:
                        n, m, h = parts
                        if me == "admin" or not locked or idx == len(lines)-1:
                            g_cont.write(f"**{n}:** {coz(m)}  -- *{h}*")
                        else: g_cont.write(f"*{n}*: `{m}`")
            with st.form("gf", clear_on_submit=True):
                gm = st.text_input("Mesaj...")
                if st.form_submit_button("Sisteme Gönder") and gm:
                    with open(FILES["chat"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{sifrele(gm)}|{datetime.now().strftime('%H:%M:%S')}\n")
                    st.rerun()

        with tabs[1]: # ÖZEL CHAT
            st.subheader("🔒 Uçtan Uca Şifreli")
            target_p = st.selectbox("Ajan Seç", [u for u in all_u if u != me] + (["admin"] if me != "admin" else []))
            p_cont = st.container(height=350)
            if os.path.exists(FILES["priv"]):
                p_lines = open(FILES["priv"], "r", encoding="utf-8").readlines()
                filtered = [l for l in p_lines if f"|{target_p}|" in l and (f"{me}|" in l or f"|{me}|" in l)]
                for idx, l in enumerate(filtered):
                    parts = l.strip().split("|")
                    if len(parts) == 3:
                        f, t, m = parts
                        if me == "admin" or not locked or idx == len(filtered)-1:
                            p_cont.write(f"**{f} ➔ {t}:** {coz(m)}")
                        else: p_cont.write(f"**{f}**: `{m}`")
            with st.form("pf", clear_on_submit=True):
                pm = st.text_input(f"{target_p} için gizli mesaj...")
                if st.form_submit_button("Fısılda") and pm:
                    with open(FILES["priv"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{target_p}|{sifrele(pm)}\n")
                    st.rerun()

        with tabs[2]: # ARAÇLAR
            st.subheader("🛠️ Manuel Dekoder")
            tc1, tc2 = st.columns(2)
            with tc1:
                t_p = st.text_area("Şifrelenecek Metin")
                if st.button("KODLA"): st.code(sifrele(t_p))
            with tc2:
                t_e = st.text_area("Çözülecek Metin")
                if st.button("ÇÖZ"): st.success(coz(t_e))

        if me == "admin":
            with tabs[3]:
                at1, at2, at3 = st.tabs(["🕶️ Hayalet", "👥 Yönetim", "🔍 Ham Veri"])
                with at1: # SPY
                    s1, s2 = st.columns(2)
                    sp1 = s1.selectbox("Hedef 1", all_u, key="sp1")
                    sp2 = s2.selectbox("Hedef 2", all_u, key="sp2")
                    if st.button("İZLEMEYİ BAŞLAT"): st.session_state['spy_target'] = (sp1, sp2)
                    if st.session_state['spy_target']:
                        u1, u2 = st.session_state['spy_target']; st.error(f"İZLENİYOR: {u1}-{u2}")
                        for l in open(FILES["priv"]).readlines():
                            if (f"{u1}|{u2}|" in l or f"{u2}|{u1}|" in l):
                                d = l.strip().split("|")
                                if len(d)==3: st.write(f"**{d[0]}**: {coz(d[2])}")
                with at2: # USER MGMT
                    for u_man in all_u:
                        m1, m2 = st.columns(2); upr = get_profile(u_man)
                        m1.write(f"**{u_man}** ({upr['rank']})")
                        if m2.button("BAN", key=f"ban_{u_man}"):
                            with open(FILES["ban"], "a") as f: f.write(u_man+"\n"); st.rerun()
                with at3: # RAW DATA
                    if st.button("🚨 SIFIRLA (MESAJLARI SİL)"):
                        open(FILES["chat"], "w").close(); open(FILES["priv"], "w").close(); st.rerun()
                    st.subheader("📋 Tüm Çözülmüş Trafik")
                    raw_data = []
                    if os.path.exists(FILES["priv"]):
                        for rl in open(FILES["priv"], "r", encoding="utf-8").readlines():
                            d = rl.strip().split("|")
                            if len(d) == 3: raw_data.append({"Kimden": d[0], "Kime": d[1], "Mesaj": coz(d[2])})
                    st.table(raw_data)

    with r_col: # SAĞ DURUM PANELİ
        st.subheader("📡 Sistem")
        st.write(f"Kilit: {'🔒 AKTİF' if locked else '🔓 PASİF'}")
        if me == "admin":
            if st.button("KİLİDİ DEĞİŞTİR"):
                if locked: os.remove(FILES["lock"])
                else: open(FILES["lock"], "w").write("L")
                st.rerun()
        st.divider()
        st.info("Sayfayı elle yenilemeyin, akış otomatiktir.")

    # OTO-YENİLEME TETİKLEYİCİ (EN ALTA KOYUYORUZ Kİ KODU KESMESİN)
    if auto_ref:
        time.sleep(5)
        st.rerun()
