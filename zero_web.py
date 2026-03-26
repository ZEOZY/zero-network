import streamlit as st
import os
import random
import time
from datetime import datetime

# --- 1. DOSYA SİSTEMİ ÇEKİRDEĞİ ---
# Tüm veriler bu dosyalarda saklanır. Bulunmazsa otomatik oluşturulur.
FILES = {
    "users": "users.txt",       # Format -> Nick:Sifre
    "chat": "ghost_chat.txt",   # Format -> Nick|SifreliMesaj|Saat
    "priv": "private_chats.txt",# Format -> Kimden|Kime|SifreliMesaj
    "ban": "ban_list.txt",      # Format -> Nick
    "warn": "warnings.txt",     # Format -> Nick|Mesaj
    "lock": "lock.txt",         # Varsa sistem kilitlidir
    "profs": "profiles.txt"     # Format -> Nick|Ad|Bio|Foto|Rutbe
}

for f_path in FILES.values():
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
    if not os.path.exists(FILES["users"]): return []
    with open(FILES["users"], "r", encoding="utf-8") as f:
        return [l.strip().split(":")[0] for l in f if ":" in l]

def get_profile(nick):
    # Varsayılan profil şablonu
    p_data = {
        "nick": nick, "name": nick, 
        "bio": "Bu kullanıcı henüz kendini tanıtmadı.", 
        "img": "https://cdn-icons-png.flaticon.com/512/149/149071.png", 
        "rank": "MEMBER"
    }
    if os.path.exists(FILES["profs"]):
        with open(FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    d = line.strip().split("|")
                    if len(d) >= 5:
                        p_data["name"] = d[1] if d[1] else nick
                        p_data["bio"] = d[2] if d[2] else p_data["bio"]
                        p_data["img"] = d[3] if d[3] else p_data["img"]
                        p_data["rank"] = d[4] if d[4] else "MEMBER"
                        break
    return p_data

def save_profile(nick, name, bio, img, rank="MEMBER"):
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

# --- 4. SESSION STATE BAŞLATMA (KRİTİK HATA ÖNLEYİCİ) ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'spy_target' not in st.session_state: st.session_state['spy_target'] = None
if 'viewing_profile' not in st.session_state: st.session_state['viewing_profile'] = None

st.set_page_config(page_title="ZERO NETWORK V26", page_icon="🕵️", layout="wide")

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state['auth']:
    st.title("📡 ZERO NETWORK - BAĞLANTI TERMİNALİ")
    st.divider()
    l_col, r_col = st.columns(2)
    
    with l_col:
        st.subheader("🔑 Giriş Yap")
        u_input = st.text_input("Kullanıcı Adı (Nick)")
        p_input = st.text_input("Şifre", type="password")
        if st.button("SİSTEME SIZ"):
            if os.path.exists(FILES["ban"]) and u_input in open(FILES["ban"]).read():
                st.error("ERİŞİM ENGELLENDİ: BANLANDIN!")
            elif (u_input == "admin" and p_input == "1234") or (f"{u_input}:{p_input}" in open(FILES["users"]).read()):
                st.session_state.update({'auth': True, 'user': u_input})
                st.rerun()
            else:
                st.error("KİMLİK GEÇERSİZ!")

    with r_col:
        st.subheader("📝 Yeni Protokol (Kayıt)")
        nu_input = st.text_input("Yeni Nick")
        np_input = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYDI TAMAMLA"):
            if nu_input and np_input and nu_input != "admin" and nu_input not in get_all_users():
                with open(FILES["users"], "a", encoding="utf-8") as f:
                    f.write(f"{nu_input}:{np_input}\n")
                st.success("Kayıt Başarılı!")
            else:
                st.error("Nick geçersiz veya alınmış.")

# --- ANA SİSTEM ARAYÜZÜ ---
else:
    me = st.session_state['user']
    is_locked = os.path.exists(FILES["lock"])
    all_users = get_all_users()

    # Sidebar: Kullanıcı Yönetimi ve Profil
    st.sidebar.title(f"🥷 {me}")
    if st.sidebar.button("⚙️ Profil Ayarlarım"):
        st.session_state['viewing_profile'] = me

    st.sidebar.divider()
    st.sidebar.subheader("👥 Aktif Node'lar")
    st.sidebar.write("⭐ admin [ROOT]")
    for user_node in all_users:
        u_p = get_profile(user_node)
        if st.sidebar.button(f"👤 {u_p['name']} [{u_p['rank']}]", key=f"btn_{user_node}"):
            st.session_state['viewing_profile'] = user_node
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Bağlantıyı Kes"):
        st.session_state['auth'] = False
        st.rerun()

    # PROFİL GÖRÜNTÜLEYİCİ (MODAL)
    if st.session_state['viewing_profile']:
        target = st.session_state['viewing_profile']
        pd = get_profile(target)
        with st.expander(f"📂 KULLANICI DOSYASI: {target}", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(pd['img'], use_container_width=True)
            with c2:
                if target == me:
                    st.subheader("Kimliğini Düzenle")
                    new_name = st.text_input("Görünen Ad", pd['name'])
                    new_bio = st.text_area("Biyografi", pd['bio'])
                    new_img = st.text_input("Avatar URL", pd['img'])
                    if st.button("VERİLERİ KAYDET"):
                        save_profile(me, new_name, new_bio, new_img, pd['rank'])
                        st.success("Güncellendi!")
                        st.rerun()
                else:
                    st.title(pd['name'])
                    st.info(f"Rütbe: {pd['rank']}")
                    st.write(f"Hakkında: {pd['bio']}")
            if st.button("Dosyayı Kapat"):
                st.session_state['viewing_profile'] = None
                st.rerun()

    # ANA PANEL TASARIMI (V21 STİLİ)
    main_col, info_col = st.columns([3, 1])

    with main_col:
        tabs = st.tabs(["🌍 Global Veri", "🔒 Özel Kanal", "🛠️ Şifreleme Terminali", "🛡️ Admin" if me == "admin" else "Sistem"])

        with tabs[0]: # GLOBAL CHAT
            st.subheader("🌐 Global Sohbet Akışı")
            g_box = st.container(height=380)
            if os.path.exists(FILES["chat"]):
                g_lines = open(FILES["chat"], "r", encoding="utf-8").readlines()
                for idx, line in enumerate(g_lines):
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        n, m, t = parts
                        # Admin her şeyi görür, kilit açıksa herkes görür, kilitliyse sadece son mesaj çözülür.
                        if me == "admin" or not is_locked or idx == len(g_lines)-1:
                            g_box.markdown(f"**{n}:** {coz(m)} <small style='color:grey; float:right;'>{t}</small>", unsafe_allow_html=True)
                        else:
                            g_box.write(f"*{n}*: `{m}`")
            
            with st.form("global_send", clear_on_submit=True):
                g_msg = st.text_input("Mesajınızı girin...")
                if st.form_submit_button("Sisteme Enjekte Et") and g_msg:
                    with open(FILES["chat"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{sifrele(g_msg)}|{datetime.now().strftime('%H:%M:%S')}\n")
                    st.rerun()

        with tabs[1]: # ÖZEL SOHBET
            st.subheader("🔒 Uçtan Uca Şifreli Kanal")
            target_user = st.selectbox("Bağlantı Kurulacak Ajan", [u for u in all_users if u != me] + (["admin"] if me != "admin" else []))
            p_box = st.container(height=300)
            if os.path.exists(FILES["priv"]):
                p_lines = open(FILES["priv"], "r", encoding="utf-8").readlines()
                # Sadece benim ve alıcının olduğu mesajları filtrele
                filtered = [l for l in p_lines if f"|{target_user}|" in l and (f"{me}|" in l or f"|{me}|" in l)]
                for idx, line in enumerate(filtered):
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        f, t, m = parts
                        if me == "admin" or not is_locked or idx == len(filtered)-1:
                            p_box.write(f"**{f} ➔ {t}:** {coz(m)}")
                        else:
                            p_box.write(f"**{f}**: `{m}`")
            
            with st.form("priv_send", clear_on_submit=True):
                p_msg = st.text_input(f"{target_user} için gizli mesaj...")
                if st.form_submit_button("Fısılda") and p_msg:
                    with open(FILES["priv"], "a", encoding="utf-8") as f:
                        f.write(f"{me}|{target_user}|{sifrele(p_msg)}\n")
                    st.rerun()

        with tabs[2]: # ŞİFRELEME ARAÇLARI
            st.header("🛠️ Manuel Dekoder/Enkoder")
            c_e, c_d = st.columns(2)
            with c_e:
                st.subheader("🔒 Şifrele")
                t_plain = st.text_area("Düz Metin", key="tp")
                if st.button("KODLA"): st.code(sifrele(t_plain))
            with c_d:
                st.subheader("🔓 Çöz")
                t_enc = st.text_area("Şifreli Metin", key="te")
                if st.button("ÇÖZ"): st.success(coz(t_enc))

        if me == "admin":
            with tabs[3]:
                at1, at2, at3 = st.tabs(["🕶️ Hayalet", "👥 Kullanıcılar", "🔍 Ham Veri"])
                with at1: # HAYALET SIZMA
                    s1, s2 = st.columns(2)
                    spy1 = s1.selectbox("Hedef 1", all_users, key="spy1")
                    spy2 = s2.selectbox("Hedef 2", all_users, key="spy2")
                    if st.button("KANALA SIZ"): st.session_state['spy_target'] = (spy1, spy2)
                    if st.session_state['spy_target']:
                        u1, u2 = st.session_state['spy_target']
                        st.error(f"İZLENİYOR: {u1} - {u2}")
                        spy_cont = st.container(height=200, border=True)
                        for l in open(FILES["priv"], "r", encoding="utf-8").readlines():
                            if (f"{u1}|{u2}|" in l or f"{u2}|{u1}|" in l):
                                d = l.strip().split("|")
                                if len(d)==3: spy_cont.write(f"**{d[0]}**: {coz(d[2])}")
                with at2: # KULLANICI VE RÜTBE
                    for u_man in all_users:
                        m1, m2, m3 = st.columns([1,1,1])
                        u_prof = get_profile(u_man)
                        m1.write(f"**{u_man}**")
                        new_r = m2.selectbox("Rütbe", ["MEMBER", "SHADOW", "ELITE", "GHOST"], 
                                             index=["MEMBER", "SHADOW", "ELITE", "GHOST"].index(u_prof['rank']), 
                                             key=f"rk_{u_man}")
                        if m2.button("GÜNCELLE", key=f"rk_btn_{u_man}"):
                            save_profile(u_man, u_prof['name'], u_prof['bio'], u_prof['img'], new_r)
                            st.rerun()
                        if m3.button("BANLA", key=f"ban_{u_man}"):
                            with open(FILES["ban"], "a") as f: f.write(u_man+"\n")
                            st.rerun()
                with at3: # HAM VERİ (ÇÖZÜLMÜŞ)
                    st.subheader("📋 Tüm Özel Trafik")
                    raw_rows = []
                    if os.path.exists(FILES["priv"]):
                        for rl in open(FILES["priv"], "r", encoding="utf-8").readlines():
                            d = rl.strip().split("|")
                            if len(d) == 3:
                                raw_rows.append({"Kimden": d[0], "Kime": d[1], "Mesaj": coz(d[2])})
                    st.table(raw_rows)

    with info_col: # SAĞ TARAF: SİSTEM DURUMU
        st.subheader("📡 Durum")
        st.write(f"Kilit: {'🔒 AKTİF' if is_locked else '🔓 PASİF'}")
        if me == "admin":
            if st.button("🚨 SIFIRLA (HATA ÇÖZÜCÜ)"):
                for k in ["chat", "priv"]: open(FILES[k], "w").close()
                st.rerun()
            if st.button("🔓 KİLİDİ AÇ" if is_locked else "🔒 SİSTEMİ KİLİTLE"):
                if is_locked: os.remove(FILES["lock"])
                else: open(FILES["lock"], "w").write("L")
                st.rerun()
        st.divider()
        st.caption("ZERO NETWORK v26.0 - Stability Update")    
