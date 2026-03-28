import streamlit as st
import os
import random
import time
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime
import io

# ==============================================================================
# --- 1. SİSTEM ÇEKİRDEĞİ VE VERİ TABANI KATMANI ---
# ==============================================================================
DB_FILES = {
    "users": "db_users.txt",
    "chat": "db_global_chat.txt",
    "priv": "db_priv_messages.txt",
    "groups": "db_group_chats.txt",
    "ban": "db_ban_list.txt",
    "profs": "db_user_profs.txt",
    "logs": "db_system_logs.txt",
    "vault": "db_vault_files.txt",
    "lock": "db_lock.txt" 
}

# Dosya sistemini boot sürecinde başlat.
for f_path in DB_FILES.values():
    if not os.path.exists(f_path):
        with open(f_path, "a", encoding="utf-8") as f:
            pass

# Rütbe Hiyerarşisi (Yetki Puanı)
RANK_LVL = {"MEMBER": 1, "SHADOW": 2, "ELITE": 3, "GHOST": 4}

# ==============================================================================
# --- 2. GÜVENLİK VE KRİPTO ÇEKİRDEĞİ (V30 OPTIMIZED) ---
# ==============================================================================
# Klasik V30 sembolik eşleme motoru.
ALFABE = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*"
SEMBOL = ['"', '!', '£', '#', '$', '+', '%', '&', '/', '=', '*', '?', '_', '-', '|', '@', 'æ', 'ß', '~', ',', '<', '.', ':', ';', '€', '>', '{', '}', '[', ']', '(', ')', '¹', '²', '³', '½', '¾', '∆', 'Ω', 'μ', 'π', '∞', '≈', '≠', '≤', '≥', '¶', '§', '÷', '×', '•', '¤', '†', '‡', '±', '√', '¬', '°', '^', 'º', '¥', '©', '®', '™', '¿', '¡', 'ø', 'æ', '∫', 'ç']
ENC_MAP = dict(zip(ALFABE, SEMBOL)); DEC_MAP = dict(zip(SEMBOL, ALFABE))

def encode_text(raw):
    if not raw: return ""
    return "".join([ENC_MAP.get(c, c) for c in raw])

def decode_text(enc):
    if not enc: return ""
    return "".join([DEC_MAP.get(c, c) for c in enc])

# ==============================================================================
# --- 3. STENANOGRAFİ MOTORU (LSB VERİ GİZLEME) - YENİ VE KRİTİK ---
# ==============================================================================
def text_to_bin(t):
    """Metni binary diziye çevirir."""
    return [format(ord(i), '08b') for i in t]
    
def hide_text_in_image(img, secret):
    """Metni fotoğrafın piksel bitlerine gizler (Güvenli LSB)."""
    secure_msg = encode_text(secret)
    # Bit bit mesajı hazırla ve bitiş imzasını ekle
    binary_secret = "".join(text_to_bin(secure_msg)) + '1111111111111110'
    
    # Fotoğrafı değiştirilebilir bir numpy dizisine çevir (uint8 zorunlu)
    img_array = np.array(img, dtype=np.uint8)
    rows, cols, channels = img_array.shape
    
    if len(binary_secret) > rows * cols * channels:
        return None, "Hata: Mesaj bu fotoğraf için çok büyük!"

    idx = 0
    # İşlemi hızlandırmak ve hatayı önlemek için düzleştirilmiş dizi kullanıyoruz
    flat_img = img_array.flatten()
    
    for i in range(len(binary_secret)):
        # Mevcut piksel değerini al
        val = int(flat_img[i]) 
        # Son biti temizle ve mesaj bitini ekle
        new_val = (val & ~1) | int(binary_secret[i])
        # Geri yaz (0-255 aralığında kalmasını garanti et)
        flat_img[i] = np.uint8(new_val)
    
    # Diziyi orijinal şekline geri döndür
    res_img = flat_img.reshape((rows, cols, channels))
    return Image.fromarray(res_img), "Gölge Deseni başarıyla enjekte edildi."
    # Bit gizleme işlemi (Hata payı sıfır).
    idx = 0
    for r in range(rows):
        for c in range(cols):
            for ch in range(channels):
                if idx < len(binary_secret):
                    # Piksel bitini mesaj biti ile değiştir.
                    img_array[r, c, ch] = (img_array[r, c, ch] & ~1) | int(binary_secret[idx])
                    idx += 1
    
    # Yeni fotoğrafı oluştur ve döndür.
    return Image.fromarray(img_array), "Gölge Deseni enjekte edildi."

def reveal_text_from_image(img):
    """Fotoğrafın piksel bitlerinden gizli metni çıkarır."""
    img_array = np.array(img)
    rows, cols, channels = img_array.shape
    
    binary_data = ""
    for r in range(rows):
        for c in range(cols):
            for ch in range(channels):
                # Piksellerin son bitini oku.
                binary_data += str(img_array[r, c, ch] & 1)
    
    # Binary veriyi metne geri çevir.
    # Son biti bulmak için 8-bitlik gruplar halinde tara.
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_bin = ""
    for byte in all_bytes:
        decoded_bin += chr(int(byte, 2))
        if decoded_bin[-2:] == "þ€": # Son bit kontrolü (V30 şifreleme ile uyumlu)
            break
            
    # Gizli mesajı V30 çözücü ile okunabilir hale getir.
    return decode_text(decoded_bin[:-2]), "Gölge deşifre edildi."

# ==============================================================================
# --- 4. VERİ ERİŞİM FONKSİYONLARI (CRUD) ---
# ==============================================================================
def get_user_list():
    if not os.path.exists(DB_FILES["users"]): return []
    with open(DB_FILES["users"], "r", encoding="utf-8") as f:
        return [line.strip().split(":")[0] for line in f if ":" in line]

def fetch_profile(nick):
    data = {"nick": nick, "name": nick, "bio": "ZERO Aktif Birim", "img": "https://i.imgur.com/v6S6asL.png", "rank": "MEMBER"}
    if nick == "admin": data["rank"] = "GHOST"
    if os.path.exists(DB_FILES["profs"]):
        with open(DB_FILES["profs"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{nick}|"):
                    p = line.strip().split("|")
                    if len(p) >= 5: data.update({"name": p[1], "bio": p[2], "img": p[3], "rank": p[4]})
    return data

def update_profile(nick, name, bio, img, rank):
    lines = open(DB_FILES["profs"], "r", encoding="utf-8").readlines() if os.path.exists(DB_FILES["profs"]) else []
    with open(DB_FILES["profs"], "w", encoding="utf-8") as f:
        exists = False
        for l in lines:
            if l.startswith(f"{nick}|"):
                f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n"); exists = True
            else: f.write(l)
        if not exists: f.write(f"{nick}|{name}|{bio}|{img}|{rank}\n")

def write_log(user, msg):
    with open(DB_FILES["logs"], "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {user}: {msg}\n")

# ==============================================================================
# --- 5. ARAYÜZ YAPILANDIRMASI VE STİL ---
# ==============================================================================
st.set_page_config(page_title="ZERO SHADOW v33", page_icon="📡", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #c9d1d9; font-family: 'Courier New', monospace; }
    .global-msg { background: #161b22; padding: 12px; border-radius: 10px; border-left: 4px solid #238636; margin-bottom: 8px; }
    .private-msg { background: #1c2128; padding: 12px; border-radius: 10px; border-left: 4px solid #1f6feb; margin-bottom: 8px; }
    .stTextInput>div>div>input { background-color: #0d1117; color: #58a6ff; border: 1px solid #30363d; }
    .rank-tag { background: #21262d; padding: 2px 10px; border-radius: 15px; font-size: 0.8em; border: 1px solid #58a6ff; }
    h1, h2, h3 { color: #58a6ff; }
    .f-file { background: #21262d; padding: 5px; border-radius: 5px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.update({'auth':False, 'user':'', 'spy_target':None, 'decoded_msg': ''})

# ==============================================================================
# --- 6. MODÜLER MOTORLAR (FRAGMENT) ---
# ==============================================================================
@st.fragment(run_every="2s")
def sync_global(me, locked):
    st.subheader("🌍 Küresel Akış")
    box = st.container(height=450, border=True)
    if os.path.exists(DB_FILES["chat"]):
        lines = open(DB_FILES["chat"], "r", encoding="utf-8").readlines()
        for idx, line in enumerate(lines):
            parts = line.strip().split("|")
            if len(parts) == 3:
                u, m, t = parts
                # Admin her şeyi çözer, kilit yoksa herkes çözer
                if me == "admin" or not locked or idx == len(lines)-1:
                    box.markdown(f"<div class='global-msg'><b>{u}</b> <small style='color:grey; float:right;'>{t}</small><br>{decode_text(m)}</div>", unsafe_allow_html=True)
                else: box.markdown(f"<div class='global-msg'><b>{u}</b> <small style='color:grey; float:right;'>{t}</small><br><code>{m}</code></div>", unsafe_allow_html=True)
    
    with st.form("form_global", clear_on_submit=True):
        msg = st.text_input("Mesaj...")
        if st.form_submit_button("SISTEME ENJEKTE") and msg:
            open(DB_FILES["chat"], "a", encoding="utf-8").write(f"{me}|{encode_text(msg)}|{datetime.now().strftime('%H:%M')}\n")
            st.rerun(scope="fragment")

@st.fragment(run_every="2s")
def sync_private(me, target, locked):
    st.subheader(f"🔒 Kanal: {target}")
    p_box = st.container(height=400, border=True)
    if os.path.exists(DB_FILES["priv"]):
        lines = open(DB_FILES["priv"], "r", encoding="utf-8").readlines()
        # Çift yönlü filtreleme.
        matches = [l.strip().split("|") for l in lines if (f"{me}|{target}" in l or f"{target}|{me}" in l)]
        for idx, msg_data in enumerate(matches):
            if len(msg_data) == 3:
                sender, _, crypt = msg_data
                if me == "admin" or not locked or idx == len(matches)-1:
                    p_box.write(f"**{sender}:** {decode_text(crypt)}")
                else: p_box.write(f"**{sender}:** `ŞİFRELİ SİNYAL`")

    with st.form("form_private", clear_on_submit=True):
        p_msg = st.text_input("Gizli Mesaj...")
        if st.form_submit_button("FISILDA") and p_msg:
            open(DB_FILES["priv"], "a", encoding="utf-8").write(f"{me}|{target}|{encode_text(p_msg)}\n")
            st.rerun(scope="fragment")

# ==============================================================================
# --- 7. ANA PROGRAM AKIŞI VE LOGIC ---
# ==============================================================================
if not st.session_state['auth']:
    # --- GİRİŞ / KAYIT EKRANI (V30) ---
    st.title("📡 ZERO NETWORK v33")
    st.info("Erişim için yetkilendirme katmanını geçmelisiniz.")
    t1, t2 = st.tabs(["🔑 GİRİŞ", "📝 KAYIT"])
    with t1:
        u_in = st.text_input("Nick")
        p_in = st.text_input("Pass", type="password")
        if st.button("SİSTEME BAĞLAN"):
            if os.path.exists(DB_FILES["ban"]) and u_in in open(DB_FILES["ban"]).read(): st.error("Erişim Reddedildi!")
            elif (u_in == "admin" and p_in == "1234") or (f"{u_in}:{p_in}" in open(DB_FILES["users"]).read()):
                st.session_state.update({'auth':True, 'user':u_in})
                write_log(u_in, "Sisteme giriş yaptı."); st.rerun()
            else: st.error("Hatalı Kimlik!")
    with t2:
        nu = st.text_input("Yeni Nick")
        np = st.text_input("Şifre Belirle", type="password")
        if st.button("PROTOKOL OLUŞTUR"):
            if nu and np and nu not in get_user_list():
                open(DB_FILES["users"], "a").write(f"{nu}:{np}\n")
                update_profile(nu, nu, "Yeni Ajan", "https://i.imgur.com/v6S6asL.png", "MEMBER")
                write_log(nu, "Yeni kayıt oluşturuldu."); st.success("Tamamlandı.")

else:
    # --- ANA PANEL ---
    me = st.session_state['user']
    sys_lock = os.path.exists(DB_FILES["lock"])
    all_u = get_user_list()
    my_p = fetch_profile(me)
    my_rank_lvl = RANK_LVL.get(my_p['rank'], 1)

    # Sidebar: Kontrol Merkezi
    st.sidebar.title(f"🥷 {me}")
    st.sidebar.markdown(f"<span class='rank-tag'>{my_p['rank']}</span>", unsafe_allow_html=True)
    if st.sidebar.button("⚙️ Profilim"): st.session_state['profile_view'] = me
    
    st.sidebar.divider()
    st.sidebar.subheader("👥 Node Listesi")
    if st.sidebar.button("⭐ admin [ROOT]"): st.session_state['profile_view'] = "admin"
    for un in all_u:
        up = fetch_profile(un)
        if st.sidebar.button(f"👤 {un} [{up['rank']}]", key=f"s_{un}"): st.session_state['profile_view'] = un
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Bağlantıyı Kes"):
        st.session_state['auth'] = False; st.rerun()

    # Profil Görüntüleyici
    if 'profile_view' in st.session_state and st.session_state['profile_view']:
        target_v = st.session_state['profile_view']; pd = fetch_profile(target_v)
        with st.expander(f"📂 KULLANICI DOSYASI: {target_v}", expanded=True):
            pc1, pc2 = st.columns([1, 2])
            pc1.image(pd['img'], use_container_width=True)
            if target_v == me:
                u_dn = st.text_input("Ad", pd['name']); u_bio = st.text_area("Bio", pd['bio']); u_img = st.text_input("Foto Link", pd['img'])
                if st.button("DOSYALARI GÜNCELLE"):
                    update_profile(me, u_dn, u_bio, u_img, pd['rank']); st.rerun()
            else:
                pc2.title(pd['name']); pc2.info(f"Rütbe: {pd['rank']}"); pc2.write(pd['bio'])
            if st.button("Dosyayı Kapat"): st.session_state['profile_view'] = None; st.rerun()

    # Ana Çalışma Alanı
    main_col, side_col = st.columns([3, 1])

    with main_col:
        tabs = st.tabs(["🌍 GLOBAL", "🔒 ÖZEL", "📂 GÖLGE DESENİ (LSB)", "🛠️ ARAÇLAR", "🛡️ MERKEZ"])
        
        with tabs[0]: sync_global(me, sys_lock)
        
        with tabs[1]:
            # Alıcı listesi.
            others = [u for u in all_u if u != me]
            if me != "admin": others.append("admin")
            sel_target = st.selectbox("Ajan Seç", others)
            sync_private(me, sel_target, sys_lock)
            
        with tabs[2]:
            st.subheader("📂 Gölge Deseni Motoru (LSB Casusluk)")
            st.warning("Bu teknik, fotoğrafın piksel bitlerine veri gizler. Fotoğrafta bir bozulma olmaz.")
            
            lsb_t1, lsb_t2 = st.tabs(["🔒 GİZLE (ENCODE)", "🔓 ÇÖZ (DECODE)"])
            
            with lsb_t1:
                col_u1, col_u2 = st.columns(2)
                file_in = col_u1.file_uploader("Gizleme yapılacak fotoğrafı seç", type=['png', 'jpg', 'jpeg'])
                secret_msg = col_u2.text_area("Gizlenecek Mesaj (Otomatik Şifrelenecek)")
                
                if file_in and secret_msg:
                    # RÜTBE KONTROLÜ (Gölge Deseni enjekte etmek ELITE+ gerektirir)
                    if my_rank_lvl >= 3:
                        if st.button("GÖLGE DESENİ ENJEKTE ET"):
                            input_img = Image.open(file_in).convert("RGB")
                            shadow_img, status = hide_text_in_image(input_img, secret_msg)
                            
                            if shadow_img:
                                # Fotoğrafı indirilebilir formata çevir.
                                buf = io.BytesIO()
                                shadow_img.save(buf, format='PNG')
                                byte_img = buf.getvalue()
                                
                                st.image(shadow_img, caption="Aşılanmış Fotoğraf (İndirmek için sağ tıklayın veya indirme butonunu kullanın)", use_container_width=True)
                                st.download_button("ŞİFRELİ FOTOĞRAFI İNDİR", byte_img, file_name=f"shadow_{file_in.name[:-4]}.png", mime="image/png")
                                st.success(status)
                            else:
                                st.error(status)
                    else:
                        st.error("Gölge Deseni enjekte etmek için ELITE+ rütbe gerekir.")

            with lsb_t2:
                col_d1, col_d2 = st.columns(2)
                file_dec = col_d1.file_uploader("Şifreli fotoğrafı seç (Deşifre)", type=['png'], key="dec")
                
                if file_dec:
                    st.image(file_dec, caption="Okunan Fotoğraf", use_container_width=True)
                    if st.button("DESENİ DEŞİFRE ET"):
                        # RÜTBE KONTROLÜ (Gölge Deseni çözmek SHADOW+ gerektirir)
                        if my_rank_lvl >= 2:
                            input_img = Image.open(file_dec).convert("RGB")
                            decoded, status = reveal_text_from_image(input_img)
                            
                            if decoded:
                                st.success(f"Gizli Mesaj: {decoded}")
                                write_log(me, f"{file_dec.name} Gölge Desenini çözdü.")
                            else:
                                st.error(status)
                        else:
                            st.error("Gölge Deseni çözmek için SHADOW+ rütbe gerekir.")

        with tabs[3]:
            # ŞİFRE ÇÖZÜCÜ SINIRLAMASI (Shadow ve Üstü)
            if my_rank_lvl >= 2: 
                st.subheader("🛠️ Manuel Dekoder Terminali")
                tc1, tc2 = st.columns(2)
                raw = tc1.text_area("Şifrelenecek")
                if tc1.button("KODLA"): st.code(secure_encrypt(raw))
                enc = tc2.text_area("Çözülecek")
                if tc2.button("ÇÖZ"): st.success(secure_decrypt(enc))
            else:
                st.error("Bu araçlar MEMBER rütbesine kapalıdır. En az SHADOW rütbesi gereklidir.")

        with tabs[4]:
            if my_rank_lvl >= 4 or me == "admin":
                st.subheader("🛡️ ROOT Merkezi")
                
                # SADECE ADMIN ÖZELLİKLERİ
                if me == "admin":
                    if st.button("SİSTEM KİLİDİ AÇ/KAPA"):
                        if sys_lock: os.remove(DB_FILES["lock"])
                        else: open(DB_FILES["lock"], "w").write("L")
                        st.rerun()
                    
                    st.write("Yetki Dağıtımı:")
                    for u_man in get_user_list():
                        col1, col2 = st.columns(2)
                        col1.write(u_man)
                        p_inf = fetch_profile(u_man)
                        new_r = col2.selectbox("Rank", list(RANK_LVL.keys()), key=f"r_{u_man}", index=list(RANK_LVL.keys()).index(p_inf['rank']))
                        if col2.button("GÜNCELLE", key=f"b_{u_man}"):
                            update_profile(u_man, p_inf['name'], p_inf['bio'], p_inf['img'], new_r); st.rerun()
                    
                    if st.button("TÜM VERİYİ SIFIRLA"):
                        for k in ["chat", "priv", "logs", "vault"]: open(DB_FILES[k], "w").close()
                        st.rerun()
                
                else:
                    st.info("Ghost Yetkisi: Moderasyon yetkileri kısıtlıdır. Sadece izleme ve raporlama yapabilirsiniz.")
                
                st.divider()
                if os.path.exists(DB_FILES["logs"]):
                    st.code(open(DB_FILES["logs"]).read()[-1000:])
            else:
                st.error("Erişim Yasak!")

    with side_col:
        st.subheader("📡 Bilgi")
        if 'profile_view' in st.session_state and st.session_state['profile_view']:
            v_p = fetch_profile(st.session_state['profile_view'])
            st.image(v_p['img'], use_container_width=True)
            st.write(f"**{v_p['name']}**")
            st.caption(v_p['bio'])
        st.divider()
        # F-Sistemi (Dosya/Foto Paylaşımı Altyapısı)
        st.subheader("📂 F-Hattı (vault)")
        upload_f = st.file_uploader("Dosya Yükle", type=['txt', 'png', 'jpg'])
        if upload_f and my_rank_lvl >= 3:
            st.success(f"{upload_f.name} Vault'a enjekte edildi.")
            with open(DB_FILES["vault"], "a", encoding="utf-8") as f:
                f.write(f"{me}|{upload_f.name}|{datetime.now().strftime('%H:%M')}\n")
        
        st.divider()
        if os.path.exists(DB_FILES["vault"]):
            f_lines = open(DB_FILES["vault"], "r", encoding="utf-8").readlines()
            for fl in f_lines[-10:]: # Son 10 dosya
                st.markdown(f"<div class='f-file'>📄 {fl}</div>", unsafe_allow_html=True)
