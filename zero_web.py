# ==============================================================================
# PROJECT: ZERO NETWORK - LEGION ULTIMA v30.0 (LEGACY REBUILD)
# STATUS: STABLE CORE - PHASE 1
# ==============================================================================

import streamlit as st
import os
import base64
from datetime import datetime

# --- SYSTEM DIRECTORY SETUP ---
CORE_DIR = "legion_data_v30"
if not os.path.exists(CORE_DIR):
    os.makedirs(CORE_DIR)

DB_PATHS = {
    "auth": os.path.join(CORE_DIR, "auth.zero"),
    "global": os.path.join(CORE_DIR, "global.zero"),
    "profiles": os.path.join(CORE_DIR, "profiles.zero")
}

for path in DB_PATHS.values():
    if not os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f: pass

# --- V30 CRYPTO ENGINE ---
K_S = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()[]{}@#$%"
V_S = "!?*#$+%&/=+-_.:;<|>@æß~ΔΩμπ∞≈≠≤≥¶§÷×•¤†‡±√¬°^º¥©®™¿¡øæ∫çαβγδεζηθικλνξοπρστυφχψω"
E_D, D_D = dict(zip(K_S, V_S)), dict(zip(V_S, K_S))

def crypt_v30(txt, mode="enc"):
    if not txt: return ""
    if mode == "enc":
        res = "".join([E_D.get(c, c) for c in txt])
        return base64.b64encode(res.encode()).decode()[::-1]
    else:
        try:
            res = base64.b64decode(txt[::-1]).decode()
            return "".join([D_D.get(c, c) for c in res])
        except: return "ERR:SIGNAL_CORRUPT"

# --- PAGE CONFIG & THEME ---
st.set_page_config(page_title="LEGION v30", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #00FF41; }
    .stTextInput>div>div>input { background-color: #0A0A0A; color: #00FF41; border: 1px solid #00FF41; }
    .stButton>button { background-color: #0A0A0A; color: #00FF41; border: 1px solid #00FF41; width: 100%; }
    .stButton>button:hover { background-color: #00FF41; color: #000; }
    .chat-card { border: 1px solid #00FF41; padding: 10px; margin-bottom: 5px; background: #050505; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'rank': 'MEMBER'})

# --- CORE LOGIC ---
def main():
    if not st.session_state.auth:
        st.title("📟 LEGION_GATEWAY v30")
        t1, t2 = st.tabs(["LOGIN", "REGISTER"])
        
        with t1:
            u = st.text_input("AGENT ID")
            p = st.text_input("ACCESS KEY", type="password")
            if st.button("AUTHORIZE"):
                if u == "admin" and p == "1234":
                    st.session_state.update({'auth': True, 'user': u, 'rank': 'GHOST'})
                    st.rerun()
                else:
                    if os.path.exists(DB_PATHS["auth"]):
                        with open(DB_PATHS["auth"], "r") as f:
                            if f"{u}:{p}\n" in f.readlines():
                                st.session_state.update({'auth': True, 'user': u, 'rank': 'MEMBER'})
                                st.rerun()
        
        with t2:
            nu = st.text_input("NEW ID")
            np = st.text_input("NEW KEY")
            if st.button("INITIALIZE"):
                with open(DB_PATHS["auth"], "a") as f: f.write(f"{nu}:{np}\n")
                st.success("Node Created.")
    
    else:
        # SIDEBAR
        st.sidebar.title(f"AGENT: {st.session_state.user}")
        st.sidebar.subheader(f"RANK: {st.session_state.rank}")
        
        menu = st.sidebar.radio("NAV", ["GLOBAL FEED", "TECH OPS", "ROOT"])
        
        if st.sidebar.button("EXIT"):
            st.session_state.auth = False
            st.rerun()

        # MODULES
        if menu == "GLOBAL FEED":
            st.subheader("🌐 GLOBAL BROADCAST")
            with st.container(height=400, border=True):
                with open(DB_PATHS["global"], "r") as f:
                    for line in f:
                        parts = line.strip().split("|")
                        if len(parts) == 3:
                            st.markdown(f"<div class='chat-card'><b>{parts[0]}</b> ({parts[2]}):<br>{crypt_v30(parts[1], 'dec')}</div>", unsafe_allow_html=True)
            
            with st.form("msg_form", clear_on_submit=True):
                msg = st.text_input("Enter Signal...")
                if st.form_submit_button("SEND") and msg:
                    ts = datetime.now().strftime("%H:%M")
                    with open(DB_PATHS["global"], "a") as f:
                        f.write(f"{st.session_state.user}|{crypt_v30(msg)}|{ts}\n")
                    st.rerun()

        elif menu == "TECH OPS":
            st.subheader("🛠️ CRYPTO STATION")
            c1, c2 = st.columns(2)
            with c1:
                t_e = st.text_area("To Enc
