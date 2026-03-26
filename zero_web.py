import streamlit as st
import os
import random
import time
from datetime import datetime

# --- 1. DOSYA SİSTEMİ ÇEKİRDEĞİ (TAM KONTROL) ---
FILES = {
    "users": "users.txt",       # Nick:Sifre
    "chat": "ghost_chat.txt",   # Nick|SifreliMesaj|Saat
    "priv": "private_chats.txt",# Nick|Alici|SifreliMesaj
    "ban": "ban_list.txt",      # Nick
    "warn": "warnings.txt",     # Nick|UyariMesaji
    "lock": "lock.txt",         # Kilit Dosyasi
    "profs": "profiles.txt"     # Nick|TakmaAd|Bio|FotoURL|Rutbe
}

for f_key, f_path in FILES.items():
    if not os.path.exists(f_path):
        with open(f_path, "a", encoding="utf-8") as f:
            pass

# --- 2. ŞİFRELEME MOTORU (V21 STANDARTI) ---
ALFABE = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*"
SEMBOL = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'Æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']
S_DICT = dict(zip(ALFABE, SEMBOL))
C_DICT = dict(zip(SEMBOL, ALFABE))

def sifrele(metin):
    return "".join([S_DICT.get(k, k) for k in metin])

def coz(metin):
    return "".join([C_DICT.get(k, k) for k in metin])

# --- 3. VERİ YÖNETİM FONKSİYONLARI ---
def get_all_users():
    with open(FILES["users"], "r", encoding="utf-8") as f:
        return [l.strip().split(":")[0] for l in f if ":" in l]

def get_profile(nick):
    # Varsayilan Veriler
    profile_data = {
        "nick": nick, 
        "name": nick, 
        "bio": "Bu ajanın dosyası henüz oluşturulmadı.", 
        "img": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png", 
        "rank": "MEMBER"
    }
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    parts = line.strip().split("|")
                    if len(parts) >= 5:
                        profile_data["name"] = parts[1] if parts[1] else nick
                        profile_data["bio"] = parts[2] if parts[2] else profile_data["bio"]
                        profile_data["img"] = parts[3] if parts[3] else profile_data["img"]
                        profile_data["rank"] = parts[4] if parts[4] else "MEMBER"
                        break
    return profile_data

def save_profile(nick, name, bio, img, rank):
    lines = []
    found = False
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    with open(FILES["profs"], "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")

def get_warn_list():
    if not os.path.exists(FILES["warn"]): return []
    with open(FILES["warn"], "r", encoding="utf-8") as f:
        return [l.strip() for l in f if "|" in l]

# --- 4. SESSION STATE BAŞLATMA ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'spy_target' not in st.session_state: st.session_state['spy_target'] = None
if 'viewing_profile' not in st.session_state: st.session_state['viewing_profile'] = None

st.set_page_config(page_title="ZERO NETWORK V25", page_icon="🕵️", layout="wide")

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state['auth']:
    st.title("📡 ZERO NETWORK - ACCESS TERMINAL")
    st.divider()
    col_log, col_reg = st.columns(2)
    
    with col_log:
        st.subheader("🔐 Mevcut Bağlantı")
        u_in = st.text_input("Nick")
        p_in = st.text_input("Şifre", type="password")
        if st.button("SISTEME SIZ"):
            with open(FILES["ban"], "r") as f:
                if u_in in f.read():
                    st.error("ERİŞİM ENGELLENDİ: SİSTEMDEN BANLANDINIZ!")
                elif (u_in == "admin" and p_in == "1234") or (f"{u_in}:{p_in}" in open(FILES["users"]).read()):
                    st.session_state.update({'auth': True, 'user': u_in})
                    st.rerun()
                else:
                    st.error("KİMLİK DOĞRULANAMADI.")

    with col_reg:
        st.subheader("📝 Yeni Protokol")
        nu_in = st.text_input("Yeni Nick")
        np_in = st.text_input("Yeni Şifre", type="password")
        if st.button("PROTOKOLÜ BAŞLAT"):
            if nu_in and np_in and nu_in != "admin" and nu_in not in get_all_users():
                with open(FILES["users"], "a", encoding="utf-8") as f:
                    f.write(f"{nu_in}:{np_in}\n")
                st.success("Kayıt Başarılı. Giriş Yapabilirsiniz.")
            else:
                st.error("Geçersiz veya Kullanımda Olan Nick.")

# --- ANA SİSTEM ---
else:
    me = st.session_state['user']
    is_locked = os.path.exists(FILES["lock"])
    all_users = get_all_users()

    # Aktif Uyarı Takibi
    my_warnings = [w.split("|")[1] for w in get_warn_list() if w.split("|")[0] == me]
    for msg in my_warnings:
        st.warning(f"⚠️ DİKKAT: {msg}")

    # Sidebar: Kullanıcı Listesi ve Profil Erişimi
    st.sidebar.header(f"🥷 {me}")
    if st.sidebar.button("⚙️ Profilimi Düzenle"):
        st.session_state['viewing_profile'] = me

    st.sidebar.divider()
    st.sidebar.subheader("👥 Bağlı Node'lar")
    st.sidebar.write("⭐ admin (ROOT)")
    for un in all_users:
        up = get_profile(un)
        if st.sidebar.button(f"👤 {up['name']} [{up['rank']}]", key=f"side_{un}"):
            st.session_state['viewing_profile'] = un

    if st.sidebar.button("🚪 Bağlantıyı Kes"):
        st.session_state['auth'] = False
        st.rerun()

    # --- PROFİL GÖRÜNTÜLEYİCİ (MODAL) ---
    if st.session_state['viewing_profile']:
        target_nick = st.session_state['viewing_profile']
        p_data = get_profile(target_nick)
        
        with st.expander(f"📂 KULLANICI DOSYASI: {target_nick}", expanded=True):
            pc1, pc2 = st.columns([1, 2])
            with pc1:
                st.image(p_data['img'], use_container_width=True)
            with pc2:
                if target_nick == me:
                    st.subheader("Kimlik Bilgilerini Güncelle")
                    n_name = st.text_input("Görünen Ad", p_data['name'])
                    n_bio = st.text_area("Biyografi / Notlar", p_data['bio'])
                    n_img = st.text_input("Avatar URL", p_data['img'])
                    if st.button("VERİTABANINI GÜNCELLE"):
                        save_profile(me, n_name, n_bio, n_img, p_data['rank'])
                        st.success("Profil Güncellendi!")
                        st.rerun()
                else:
                    st.title(f"ID: {p_data['name']}")
                    st.markdown(f"**Rütbe:** `{p_data['rank']}`")
                    st.write(f"**Bio:** {p_data['bio']}")
                    st.caption(f"Kayıtlı Nick: {target_nick}")
            if st.button("Dosyayı Kapat"):
                st.session_state['viewing_profile'] = None
                st.rerun()

    # --- ANA PANEL ---
    m_col, r_col = st.columns([3, 1])

    with m_col:
        tabs = st.tabs(["🌍 Global Chat", "🔒 Özel Sohbet", "🛠️ Şifreleme Araçları", "🛡️ ADMİN PANELİ" if me == "admin" else "Sistem"])

        with tabs[0]: # GLOBAL CHAT
            st.subheader("🌐 Global Veri Akışı")
            g_box = st.container(height=350)
            g_lines = open(FILES["chat"], "r", encoding="utf-8").readlines()
            with g_box:
                for idx, line in enumerate(g_lines):
                    if "|" in line:
                        n, m, t = line.strip().split("|")
                        # KURAL: Admin her şeyi çözer. Kullanıcılar sadece SON mesajı görür.
                        if me == "admin" or (not is_locked and idx == len(g_lines)-1):
                            st.markdown(f"**{n}:** {coz(m)} <small style='color:grey; float:right;'>{t}</small>", unsafe_allow_html=True)
                        else:
                            st.write(f"*{n}*: `{m}`")
            with st.form("g_form", clear_on_submit=True):
                gm = st.text_input("Mesajınızı şifreleyin...")
                if st.form_submit_button("Sisteme Gönder") and gm:
                    with open(FILES["chat"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{sifrele(gm)}|{datetime.now().strftime('%H:%M:%S')}\n")
                    st.rerun()

        with tabs[1]: # ÖZEL SOHBET
            target_chat = st.selectbox("Bağlantı Kurulacak Kişi", [u for u in all_users if u != me] + (["admin"] if me != "admin" else []))
            p_box = st.container(height=350)
            p_lines = open(FILES["priv"], "r", encoding="utf-8").readlines()
            # Filtreleme
            filtered = [l for l in p_lines if f"|{target_chat}|" in l and (f"{me}|" in l or f"|{me}|" in l)]
            with p_box:
                for idx, line in enumerate(filtered):
                    if "|" in line:
                        f, t, m = line.strip().split("|")
                        if me == "admin" or (not is_locked and idx == len(filtered)-1):
                            st.write(f"**{f} ➔ {t}:** {coz(m)}")
                        else:
                            st.write(f"*{f}*: `{m}`")
            with st.form("p_form", clear_on_submit=True):
                pm = st.text_input(f"{target_chat} kişisine özel veri...")
                if st.form_submit_button("Fısılda") and pm:
                    with open(FILES["priv"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{target_chat}|{sifrele(pm)}\n")
                    st.rerun()

        with tabs[2]: # ŞİFRELEME ARAÇLARI (HERKESE AÇIK)
            st.header("🛠️ Manuel Şifreleme Terminali")
            st.info("Bu terminali kullanarak platform dışı yazışmalarınızı şifreleyebilirsiniz.")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.subheader("🔒 Şifrele")
                plain_text = st.text_area("Düz Metin Girin", key="tools_p")
                if st.button("KOD OLUŞTUR"):
                    st.code(sifrele(plain_text))
            with t_col2:
                st.subheader("🔓 Çöz")
                enc_text = st.text_area("Şifreli Kod Girin", key="tools_e")
                if st.button("KODU ÇÖZ"):
                    st.success(f"Çözülen Veri: {coz(enc_text)}")

        if me == "admin":
            with tabs[3]:
                at1, at2, at3, at4 = st.tabs(["🕶️ Hayalet Gözlem", "👥 Kullanıcı & Rütbe", "🔍 Ham Veri (ÇÖZÜLMÜŞ)", "📋 Uyarı Yönetimi"])
                
                with at1: # HAYALET GÖZLEM
                    s1, s2 = st.columns(2)
                    spy1 = s1.selectbox("Hedef 1", all_users, key="spy1")
                    spy2 = s2.selectbox("Hedef 2", all_users, key="spy2")
                    if st.button("ODAYA SIZ"): st.session_state['spy_target'] = (spy1, spy2)
                    if st.session_state['spy_target']:
                        u1, u2 = st.session_state['spy_target']
                        st.error(f"🕵️ İZLENİYOR: {u1} ↔️ {u2}")
                        spy_box = st.container(height=250, border=True)
                        all_p_lines = open(FILES["priv"], "r", encoding="utf-8").readlines()
                        with spy_box:
                            for sl in all_p_lines:
                                if (f"{u1}|{u2}|" in sl or f"{u2}|{u1}|" in sl):
                                    sf, st, sm = sl.strip().split("|")
                                    st.write(f"**{sf}**: {coz(sm)}")
                        with st.form("spy_send"):
                            s_msg = st.text_input("Araya Sızdırılacak Mesaj")
                            s_as = st.selectbox("Kimin Adına?", [u1, u2])
                            if st.form_submit_button("MESAJI ENJEKTE ET"):
                                with open(FILES["priv"], "a", encoding="utf-8") as f:
                                    f.write(f"{s_as}|{(u2 if s_as==u1 else u1)}|{sifrele(s_msg)}\n")
                                st.rerun()

                with at2: # KULLANICI YÖNETİMİ
                    for u_man in all_users:
                        mc1, mc2, mc3 = st.columns([1, 1, 1])
                        u_prof = get_profile(u_man)
                        mc1.write(f"**{u_man}**")
                        new_r = mc2.selectbox("Rütbe", ["MEMBER", "SHADOW", "ELITE", "GHOST"], 
                                             index=["MEMBER", "SHADOW", "ELITE", "GHOST"].index(u_prof['rank']), 
                                             key=f"r_{u_man}")
                        if mc2.button("RÜTBE VER", key=f"rb_{u_man}"):
                            save_profile(u_man, u_prof['name'], u_prof['bio'], u_prof['img'], new_r)
                            st.rerun()
                        if mc3.button("BANLA", key=f"bb_{u_man}"):
                            with open(FILES["ban"], "a") as f: f.write(u_man + "\n")
                            st.rerun()

                with at3: # HAM VERİ (ÇÖZÜLMÜŞ)
                    st.subheader("📋 Tüm Trafik (Admin İçin Şifreleri Çözülmüş)")
                    raw_data = [l.strip().split("|") for l in open(FILES["priv"], "r", encoding="utf-8").readlines() if "|" in l]
                    # Admin tablosunda mesajlar her zaman coz() ile cozulur.
                    st.table([{"Kimden": d[0], "Kime": d[1], "Mesaj": coz(d[2])} for d in raw_data])

                with at4: # UYARI YÖNETİMİ
                    st.subheader("Aktif Uyarı Listesi")
                    w_list = get_warn_list()
                    for idx, wl in enumerate(w_list):
                        wc1, wc2, wc3 = st.columns([1, 2, 1])
                        w_u, w_m = wl.split("|")
                        wc1.write(f"**{w_u}**")
                        wc2.write(w_m)
                        if wc3.button("SİL", key=f"dw_{idx}"):
                            new_ws = [x for i, x in enumerate(w_list) if i != idx]
                            with open(FILES["warn"], "w", encoding="utf-8") as f:
                                for nw in new_ws: f.write(nw + "\n")
                            st.rerun()
                    st.divider()
                    st.subheader("Yeni Uyarı Gönder")
                    u_target = st.selectbox("Kullanıcı", all_users, key="warn_target")
                    u_text = st.text_input("Uyarı Notu", key="warn_text")
                    if st.button("UYARIYI GÖNDER"):
                        with open(FILES["warn"], "a", encoding="utf-8") as f:
                            f.write(f"{u_target}|{u_text}\n")
                        st.rerun()

    with r_col: # SAĞ TARAF: SİSTEM DURUMU
        st.subheader("📡 Sistem Durumu")
        st.write(f"Kilit Durumu: {'🔒 AKTİF' if is_locked else '🔓 PASİF'}")
        if me == "admin":
            if st.button("🚨 TÜM VERİLERİ SİL"):
                for k in ["chat", "priv", "warn"]: open(FILES[k], "w").close()
                st.rerun()
            if st.button("🔓 KİLİDİ AÇ" if is_locked else "🔒 KİLİTLE"):
                if is_locked: os.remove(FILES["lock"])
                else: open(FILES["lock"], "w").write("L")
                st.rerun()