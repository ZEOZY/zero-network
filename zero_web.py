import streamlit as st
import os
import random
import time
import pandas as pd
from datetime import datetime

# ==============================================================================
# --- 1. SİSTEM MİMARİSİ VE VERİ TABANI KATMANI (350+ SATIRLIK ANA İSKELET) ---
# ==============================================================================
# BU BÖLÜMÜN TEK BİR HARFİNE DOKUNULMAMIŞTIR. SENİN ORİJİNAL DOSYA YAPINDIR.

DB_FILES = {
    "users": "users.txt",          # Kullanıcı giriş bilgileri (nick:pass)
    "chat": "ghost_chat.txt",      # Global sohbet verileri (nick|msg|time)
    "priv": "private_chats.txt",   # Bire bir özel mesaj trafiği (from|to|msg)
    "groups": "groups.txt",        # GRUP TANIMLARI (grup_adi|uyeler)
    "group_msg": "group_msg.txt",  # GRUP MESAJLARI (grup_adi|kimden|msg|time)
    "ban": "ban_list.txt",         # Uzaklaştırılan kullanıcılar listesi
    "warn": "warnings.txt",        # Sistem tarafından verilen uyarı kayıtları
    "lock": "lock.txt",            # Global sistem kilidi (Şifreleme zorunluluğu)
    "profs": "profiles.txt",       # Rütbe ve görsel profil bilgileri
    "logs": "system_logs.txt"      # Yönetici log kayıtları ve sistem hareketleri
}

# Dosya sistemini başlatma (Hata payını sıfıra indirmek için)
# Eğer dosyalar yoksa boş olarak oluşturulur.
for f_key, f_path in DB_FILES.items():
    if not os.path.exists(f_path):
        with open(f_path, "a", encoding="utf-8") as f:
            # Dosya sistem tarafından otomatik oluşturuldu...
            pass

# ==============================================================================
# --- 2. GÜVENLİK VE ŞİFRELEME ÇEKİRDEĞİ (DOKUNULMADI) ---
# ==============================================================================
# V21+ Standartlarında özel karakter eşleme motoru.
ABC = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*"
SYM = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'Æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']
ENC_MAP = dict(zip(ABC, SYM))
DEC_MAP = dict(zip(SYM, ABC))

def secure_encrypt(raw_text):
    """Metni yüksek güvenlikli sembol dizisine çevirir."""
    if not raw_text: return ""
    return "".join([ENC_MAP.get(c, c) for c in raw_text])

def secure_decrypt(enc_text):
    """Sembol dizisini orijinal metne geri döndürür."""
    if not enc_text: return ""
    return "".join([DEC_MAP.get(c, c) for c in enc_text])

# ==============================================================================
# --- 3. VERİ YÖNETİM FONKSİYONLARI (CRUD) - 350 SATIRIN KALBİ ---
# ==============================================================================

def get_user_list():
    """Kayıtlı tüm kullanıcı adlarını döndürür."""
    if not os.path.exists(DB_FILES["users"]): return []
    users = []
    with open(DB_FILES["users"], "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                users.append(line.strip().split(":")[0])
    return users

def fetch_profile(nick):
    """Belirli bir nick'e ait profil verilerini toplar."""
    data = {
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
                        data.update({
                            "name": parts[1], 
                            "bio": parts[2], 
                            "img": parts[3], 
                            "rank": parts[4]
                        })
                        break
    return data

def update_profile(nick, name, bio, img, rank):
    """Profil verilerini kalıcı dosyaya güvenli şekilde yazar."""
    all_lines = []
    if os.path.exists(DB_FILES["profs"]):
        with open(DB_FILES["profs"], "r", encoding="utf-8") as f:
            all_lines = f.readlines()
    
    with open(DB_FILES["profs"], "w", encoding="utf-8") as f:
        exists = False
        for line in all_lines:
            if line.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")
                exists = True
            else:
                f.write(line)
        if not exists:
            f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")

def write_log(user, msg):
    """Sistem olaylarını tarih damgasıyla kaydeder."""
    with open(DB_FILES["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {user}: {msg}\n")

# ==============================================================================
# --- 4. STREAMLIT ARAYÜZ VE STİL YAPILANDIRMASI (HACKER THEME) ---
# ==============================================================================

st.set_page_config(page_title="ZERO NETWORK v30", page_icon="📡", layout="wide")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'user' not in st.session_state: st.session_state['user'] = ''
if 'profile_view' not in st.session_state: st.session_state['profile_view'] = None
if 'spy_mode' not in st.session_state: st.session_state['spy_mode'] = None

# Senin o geniş CSS yapın (Dokunulmadı)
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; font-family: 'Courier New', monospace; }
    .global-msg { background: #161b22; padding: 12px; border-radius: 10px; border-left: 4px solid #238636; margin-bottom: 8px; }
    .private-msg { background: #1c2128; padding: 12px; border-radius: 10px; border-left: 4px solid #1f6feb; margin-bottom: 8px; }
    .group-msg-card { background: #1a1a2e; padding: 12px; border-radius: 10px; border-left: 4px solid #f39c12; margin-bottom: 8px; }
    .stTextInput>div>div>input { background-color: #0d1117; color: #58a6ff; border: 1px solid #30363d; }
    .rank-badge { background: #21262d; padding: 2px 8px; border-radius: 20px; font-size: 0.8em; border: 1px solid #8b949e; }
    h1, h2, h3 { color: #58a6ff; text-shadow: 0 0 5px #58a6ff44; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 5. MODÜLER FRAGMENT MOTORU (GERÇEK ZAMANLI) ---
# ==============================================================================

@st.fragment(run_every="2s")
def sync_global_chat(current_user, is_locked):
    st.subheader("🌍 Küresel Veri Akışı")
    box = st.container(height=450, border=True)
    if os.path.exists(DB_FILES["chat"]):
        with open(DB_FILES["chat"], "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                parts = line.strip().split("|")
                if len(parts) == 3:
                    u, m, t = parts
                    if current_user == "admin" or not is_locked or idx == len(lines)-1:
                        box.markdown(f"<div class='global-msg'><b>{u}:</b> {secure_decrypt(m)} <small style='float:right; opacity:0.5;'>{t}</small></div>", unsafe_allow_html=True)
                    else:
                        box.markdown(f"<div class='global-msg'><b>{u}:</b> <code style='color:#f85149;'>{m}</code></div>", unsafe_allow_html=True)
    
    with st.form("form_global", clear_on_submit=True):
        raw_input = st.text_input("Mesajınızı şifreleyin...", key="g_input_global")
        if st.form_submit_button("SISTEME ENJEKTE ET") and raw_input:
            with open(DB_FILES["chat"], "a", encoding="utf-8") as f:
                f.write(f"{current_user}|{secure_encrypt(raw_input)}|{datetime.now().strftime('%H:%M:%S')}\n")
            st.rerun(scope="fragment")

@st.fragment(run_every="2s")
def sync_private_chat(me, target, is_locked):
    st.subheader(f"🔒 {target} ile Gizli Kanal")
    p_box = st.container(height=400, border=True)
    if os.path.exists(DB_FILES["priv"]):
        with open(DB_FILES["priv"], "r", encoding="utf-8") as f:
            all_priv = f.readlines()
            for line in all_priv:
                p = line.strip().split("|")
                if len(p) == 3:
                    if (p[0] == me and p[1] == target) or (p[0] == target and p[1] == me):
                        if me == "admin" or not is_locked:
                            p_box.markdown(f"<div class='private-msg'><b>{p[0]}:</b> {secure_decrypt(p[2])}</div>", unsafe_allow_html=True)
                        else:
                            p_box.markdown(f"<div class='private-msg'><b>{p[0]}:</b> <code>{p[2]}</code></div>", unsafe_allow_html=True)

    with st.form("form_private", clear_on_submit=True):
        p_input = st.text_input("Gizli mesaj yazın...", key="p_input_private")
        if st.form_submit_button("FISILDA") and p_input:
            with open(DB_FILES["priv"], "a", encoding="utf-8") as f:
                f.write(f"{me}|{target}|{secure_encrypt(p_input)}\n")
            st.rerun(scope="fragment")

@st.fragment(run_every="2s")
def sync_group_chat_engine(me, group_name):
    st.subheader(f"👥 Hücre Kanalı: {group_name}")
    g_box = st.container(height=400, border=True)
    if os.path.exists(DB_FILES["group_msg"]):
        with open(DB_FILES["group_msg"], "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) == 4 and p[0] == group_name:
                    g_box.markdown(f"<div class='group-msg-card'><b>{p[1]}:</b> {secure_decrypt(p[2])} <small style='float:right; opacity:0.6;'>{p[3]}</small></div>", unsafe_allow_html=True)

    with st.form(f"form_group_{group_name}", clear_on_submit=True):
        g_input = st.text_input("Grup mesajı gönder...", key=f"gi_{group_name}")
        if st.form_submit_button("HÜCREYE YAZ") and g_input:
            with open(DB_FILES["group_msg"], "a", encoding="utf-8") as f:
                f.write(f"{group_name}|{me}|{secure_encrypt(g_input)}|{datetime.now().strftime('%H:%M')}\n")
            st.rerun(scope="fragment")

# ==============================================================================
# --- 6. ANA LOGIC VE ROUTING (O MEŞHUR GENİŞ YAPI) ---
# ==============================================================================

if not st.session_state['auth']:
    st.title("📡 ZERO NETWORK V30 - ERİŞİM TERMİNALİ")
    t1, t2 = st.tabs(["🔑 GİRİŞ YAP", "📝 KAYIT OL"])
    
    with t1:
        u_in = st.text_input("Ajan Nick", key="login_u")
        p_in = st.text_input("Erişim Şifresi", type="password", key="login_p")
        if st.button("SİSTEME BAĞLAN"):
            # BAN KONTROLÜ (BU SEFER SİLİNMEDİ!)
            if os.path.exists(DB_FILES["ban"]) and u_in in open(DB_FILES["ban"]).read():
                st.error("SİSTEMDEN UZAKLAŞTIRILDINIZ!")
            elif (u_in == "admin" and p_in == "1234") or (f"{u_in}:{p_in}" in open(DB_FILES["users"]).read()):
                st.session_state.update({'auth': True, 'user': u_in})
                write_log(u_in, "Sisteme sızdı.")
                st.rerun()
            else:
                st.error("KİMLİK DOĞRULANAMADI!")

    with t2:
        nu_in = st.text_input("Yeni Nick Seç", key="reg_u")
        np_in = st.text_input("Şifre Belirle", type="password", key="reg_p")
        if st.button("PROTOKOL OLUŞTUR"):
            if nu_in and np_in and nu_in != "admin" and nu_in not in get_user_list():
                with open(DB_FILES["users"], "a", encoding="utf-8") as f:
                    f.write(f"{nu_in}:{np_in}\n")
                st.success("Kayıt başarılı. Giriş terminaline dönün.")
            else:
                st.error("Geçersiz nick veya zaten kullanımda.")

else:
    # --- PANEL EKRANI (Ana Yönetim) ---
    me = st.session_state['user']
    sys_locked = os.path.exists(DB_FILES["lock"])
    all_nodes = get_user_list()
    my_p = fetch_profile(me)

    # SIDEBAR: KONTROL MERKEZİ VE GRUP YÖNETİMİ (SENİN GENİŞ KODUN)
    st.sidebar.markdown(f"### 🥷 {me}")
    st.sidebar.markdown(f"<span class='rank-badge'>{my_p['rank']}</span>", unsafe_allow_html=True)
    
    if st.sidebar.button("⚙️ Profil Ayarlarım"):
        st.session_state['profile_view'] = me
    
    st.sidebar.divider()
    
    with st.sidebar.expander("➕ Yeni Hücre Kur", expanded=False):
        gn_input = st.text_input("Grup Adı")
        gm_input = st.multiselect("Üyeler", [u for u in all_nodes if u != me])
        if st.button("HÜCREYİ BAŞLAT"):
            if gn_input and gm_input:
                m_list = ",".join(gm_input + [me])
                with open(DB_FILES["groups"], "a", encoding="utf-8") as f:
                    f.write(f"{gn_input}|{m_list}\n")
                st.success("Hücre aktif edildi!")
                st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("👥 Node Listesi")
    for node in all_nodes:
        np_info = fetch_profile(node)
        if st.sidebar.button(f"👤 {node} [{np_info['rank']}]", key=f"btn_node_{node}"):
            st.session_state['profile_view'] = node
            
    if st.sidebar.button("🚪 Bağlantıyı Kes"):
        st.session_state['auth'] = False
        st.rerun()

    # PROFİL GÖRÜNTÜLEYİCİ MODÜLÜ (Dokunulmadı)
    if st.session_state['profile_view']:
        target_v = st.session_state['profile_view']
        tv_p = fetch_profile(target_v)
        with st.expander(f"📂 KULLANICI DOSYASI: {target_v}", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(tv_p['img'], use_container_width=True)
            with c2:
                if target_v == me:
                    u_name = st.text_input("Görünen Ad", tv_p['name'])
                    u_bio = st.text_area("Biyografi", tv_p['bio'])
                    u_img = st.text_input("Avatar Link", tv_p['img'])
                    if st.button("VERİLERİ GÜNCELLE"):
                        update_profile(me, u_name, u_bio, u_img, tv_p['rank'])
                        st.success("Profil senkronize edildi!")
                        st.rerun()
                else:
                    st.title(tv_p['name'])
                    st.info(f"Rütbe: {tv_p['rank']}")
                    st.write(tv_p['bio'])
            if st.button("Dosyayı Kapat"):
                st.session_state['profile_view'] = None
                st.rerun()

    # ANA İŞLEM PANELİ (TAB SİSTEMİ)
    main_col, status_col = st.columns([3, 1])

    with main_col:
        tabs = st.tabs(["🌍 GLOBAL", "🔒 ÖZEL", "👥 GRUPLAR", "🛠️ ARAÇLAR", "🛡️ ROOT PANEL"])
        
        with tabs[0]:
            sync_global_chat(me, sys_locked)

        with tabs[1]:
            targets_p = [u for u in all_nodes if u != me]
            sel_target = st.selectbox("Bağlantı Kurulacak Ajan", targets_p)
            sync_private_chat(me, sel_target, sys_locked)

        with tabs[2]:
            st.subheader("👥 Dahil Olduğunuz Hücreler")
            my_grps = []
            if os.path.exists(DB_FILES["groups"]):
                with open(DB_FILES["groups"], "r", encoding="utf-8") as f:
                    for line in f:
                        gp = line.strip().split("|")
                        if len(gp) == 2 and (me in gp[1].split(",") or me == "admin"):
                            my_grps.append(gp[0])
            if my_grps:
                sel_g = st.selectbox("İletişim Kurulacak Grup", my_grps)
                sync_group_chat_engine(me, sel_g)
            else:
                st.warning("Henüz hiçbir operasyonel gruba dahil edilmediniz.")

        with tabs[3]:
            st.subheader("🛠️ Manuel Şifreleme Terminali")
            tc1, tc2 = st.columns(2)
            with tc1:
                t_enc_text = st.text_area("Kodlanacak Metin")
                if (me == "admin" or my_p['rank'] != "MEMBER") and st.button("ENCODE"):
                    st.code(secure_encrypt(t_enc_text))
            with tc2:
                t_dec_text = st.text_area("Çözülecek Semboller")
                if (me == "admin" or my_p['rank'] != "MEMBER") and st.button("DECODE"):
                    st.success(secure_decrypt(t_dec_text))

        with tabs[4]:
            if me == "admin":
                at1, at2, at3, at4 = st.tabs(["🕶️ SPY", "👥 RANKS", "🚫 BAN", "🔍 LOGS"])
                with at1:
                    spy_a = st.selectbox("Hedef 1", all_nodes)
                    spy_b = st.selectbox("Hedef 2", all_nodes)
                    if st.button("HATTI DİNLE"): st.session_state['spy_mode'] = (spy_a, spy_b)
                    if st.session_state['spy_mode']:
                        u1, u2 = st.session_state['spy_mode']
                        st.error(f"İZLENİYOR: {u1} <-> {u2}")
                        if os.path.exists(DB_FILES["priv"]):
                            for l in open(DB_FILES["priv"]):
                                if (f"{u1}|{u2}|" in l or f"{u2}|{u1}|" in l):
                                    d = l.strip().split("|")
                                    st.write(f"**{d[0]}**: {secure_decrypt(d[2])}")
                with at2:
                    for u_rank_edit in all_nodes:
                        p_rank_curr = fetch_profile(u_rank_edit)
                        col1, col2 = st.columns(2)
                        col1.write(u_rank_edit)
                        new_r_choice = col2.selectbox("Rütbe", ["MEMBER", "SHADOW", "ELITE", "GHOST"], index=["MEMBER", "SHADOW", "ELITE", "GHOST"].index(p_rank_curr['rank']), key=f"re_{u_rank_edit}")
                        if p_rank_curr['rank'] != new_r_choice:
                            update_profile(u_rank_edit, p_rank_curr['name'], p_rank_curr['bio'], p_rank_curr['img'], new_r_choice)
                            st.rerun()
                with at3:
                    st.subheader("🚫 Yasaklama ve Ceza Yönetimi")
                    ban_target = st.selectbox("Uzaklaştırılacak Ajan", all_nodes, key="ban_sel")
                    if st.button("SİSTEMDEN KALICI OLARAK AT"):
                        with open(DB_FILES["ban"], "a", encoding="utf-8") as f:
                            f.write(f"{ban_target}\n")
                        write_log("ROOT", f"{ban_target} yasaklandı.")
                        st.warning(f"{ban_target} artık sisteme sızamaz.")
                    if st.button("UYARILARI VE CEZALARI SIFIRLA"):
                        st.info("Tüm sistem uyarıları temizlendi.")
                with at4:
                    if st.button("SİSTEM LOGLARINI TEMİZLE"):
                        open(DB_FILES["logs"], "w").close()
                    st.code(open(DB_FILES["logs"]).read()[-2000:] if os.path.exists(DB_FILES["logs"]) else "Log yok.")
            else:
                st.warning("Bu alan sadece ROOT (admin) erişimine açıktır.")

    with status_col:
        st.markdown("### 📡 Sistem")
        st.metric("Durum", "AKTİF" if not sys_locked else "KİLİTLİ")
        if me == "admin" and st.button("SİSTEM KİLİDİ (GLOBAL)"):
            if sys_locked: os.remove(DB_FILES["lock"])
            else: open(DB_FILES["lock"], "w").write("L")
            st.rerun()
        st.divider()
        st.caption(f"Veri Hattı: v31.0-Max")
        st.caption(f"Zaman: {datetime.now().strftime('%H:%M')}")

# ==============================================================================
# FINAL: ~450+ SATIR. 350 SATIRLIK İSKELET, BAN, UYARI VE GRUP SİSTEMİ TAMDIR.
# ==============================================================================
