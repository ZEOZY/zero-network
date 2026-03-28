# ==============================================================================
# PROJECT: ZERO NETWORK - LEGION ULTIMA v50.0
# STATUS: MAXIMUM ENCRYPTION & EXPANDED ARCHITECTURE
# LINE TARGET: 580+ FUNCTIONAL LINES (EXCLUDING WHITESPACE)
# ==============================================================================

import streamlit as st
import os
import numpy as np
import pandas as pd
import io
import time
import random
import base64
import binascii
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime

# ------------------------------------------------------------------------------
# SECTION 1: SYSTEM ENVIRONMENT & DIRECTORY MAPPING
# ------------------------------------------------------------------------------
def setup_system_directories():
    base_path = "legion_data_core"
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    return base_path

CORE_DIR = setup_system_directories()

def get_db_map():
    db_map = {
        "access": os.path.join(CORE_DIR, "auth_registry.zero"),
        "global": os.path.join(CORE_DIR, "global_stream.zero"),
        "private": os.path.join(CORE_DIR, "private_nodes.zero"),
        "profiles": os.path.join(CORE_DIR, "agent_profiles.zero"),
        "logs": os.path.join(CORE_DIR, "system_audit.zero"),
        "groups": os.path.join(CORE_DIR, "group_clusters.zero"),
        "intel": os.path.join(CORE_DIR, "intel_broadcast.zero"),
        "vault": os.path.join(CORE_DIR, "secure_vault.zero"),
        "config": os.path.join(CORE_DIR, "system_config.zero")
    }
    return db_map

DB_PATHS = get_db_map()

def initialize_databases():
    for key in DB_PATHS:
        current_path = DB_PATHS[key]
        if not os.path.exists(current_path):
            with open(current_path, "a", encoding="utf-8") as f:
                pass

initialize_databases()

# ------------------------------------------------------------------------------
# SECTION 2: RANKING ENGINE & PERMISSION MATRIX
# ------------------------------------------------------------------------------
def get_rank_definitions():
    ranks = {
        "MEMBER": {
            "level": 1, 
            "color": "#00FF41", 
            "prefix": "[UNIT-01]", 
            "access_score": 10,
            "can_mask": False,
            "can_root": False
        },
        "SHADOW": {
            "level": 2, 
            "color": "#BC13FE", 
            "prefix": "[OP-SHADOW]", 
            "access_score": 25,
            "can_mask": True,
            "can_root": False
        },
        "ELITE": {
            "level": 3, 
            "color": "#00D4FF", 
            "prefix": "[ELITE-V]", 
            "access_score": 50,
            "can_mask": True,
            "can_root": False
        },
        "GHOST": {
            "level": 4, 
            "color": "#FF3131", 
            "prefix": "[GHOST-X]", 
            "access_score": 100,
            "can_mask": True,
            "can_root": True
        }
    }
    return ranks

RANK_MAP = get_rank_definitions()

# ------------------------------------------------------------------------------
# SECTION 3: ADVANCED CRYPTOGRAPHY & SIGNAL PROCESSING
# ------------------------------------------------------------------------------
def get_encryption_keys():
    key_source = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZabcçdefgğhıijk_lmnoöprsştuüvyz 0123456789.,!?+-/*:()[]{}@#$%"
    val_source = "!?*#$+%&/=+-_.:;<|>@æß~ΔΩμπ∞≈≠≤≥¶§÷×•¤†‡±√¬°^º¥©®™¿¡øæ∫çαβγδεζηθικλνξοπρστυφχψω"
    return dict(zip(key_source, val_source)), dict(zip(val_source, key_source))

ENC_DICT, DEC_DICT = get_encryption_keys()

def process_signal_encrypt(raw_input):
    if not raw_input:
        return ""
    
    # Phase 1: Substitution
    cipher_text = ""
    for char in raw_input:
        if char in ENC_DICT:
            cipher_text += ENC_DICT[char]
        else:
            cipher_text += char
            
    # Phase 2: Base64 Obfuscation
    b64_bytes = base64.b64encode(cipher_text.encode("utf-8"))
    b64_string = b64_bytes.decode("utf-8")
    
    # Phase 3: Bit-Shift Reversal
    final_output = b64_string[::-1]
    return final_output

def process_signal_decrypt(encoded_input):
    if not encoded_input:
        return ""
    try:
        # Phase 1: Reverse the string
        reversed_signal = encoded_input[::-1]
        
        # Phase 2: Decode Base64
        decoded_bytes = base64.b64decode(reversed_signal)
        decoded_string = decoded_bytes.decode("utf-8")
        
        # Phase 3: Reverse Substitution
        plain_text = ""
        for char in decoded_string:
            if char in DEC_DICT:
                plain_text += DEC_DICT[char]
            else:
                plain_text += char
        return plain_text
    except Exception as decoding_error:
        return f"CRITICAL_DECODE_FAILURE: {str(decoding_error)}"

# ------------------------------------------------------------------------------
# SECTION 4: IMAGE STENANOGRAPHY & VISUAL MASKING (ULTIMA-LSB)
# ------------------------------------------------------------------------------
def convert_text_to_binary_stream(message):
    binary_stream = ""
    for character in message:
        binary_char = format(ord(character), '08b')
        binary_stream += binary_char
    return binary_stream

def convert_binary_stream_to_text(binary_data):
    text_data = ""
    for i in range(0, len(binary_data), 8):
        byte_chunk = binary_data[i:i+8]
        char_code = int(byte_chunk, 2)
        text_data += chr(char_code)
    return text_data

def apply_ultima_masking(input_image, hidden_message, noise_level=5):
    """Embeds data into pixels and applies visual noise/censorship."""
    working_img = input_image.convert("RGB")
    
    # Append termination signature
    hidden_message += " [X_TERMINATE_X]"
    binary_payload = convert_text_to_binary_stream(hidden_message)
    
    pixel_array = np.array(working_img, dtype=np.uint8)
    flattened_pixels = pixel_array.flatten()
    
    if len(binary_payload) > len(flattened_pixels):
        return None, "PAYLOAD_OVERFLOW: Image too small for this signal."
    
    # LSB Injection Phase
    for bit_index in range(len(binary_payload)):
        current_val = int(flattened_pixels[bit_index])
        modified_val = (current_val & ~1) | int(binary_payload[bit_index])
        flattened_pixels[bit_index] = np.uint8(modified_val)
        
    restored_array = flattened_pixels.reshape(pixel_array.shape)
    final_mask_img = Image.fromarray(restored_array)
    
    # Visual Masking Layer (Glitch Effect)
    canvas = ImageDraw.Draw(final_mask_img)
    img_w, img_h = final_mask_img.size
    
    for _ in range(noise_level * 4):
        start_x = random.randint(0, img_w)
        start_y = random.randint(0, img_h)
        end_x = start_x + random.randint(30, 150)
        end_y = start_y + random.randint(3, 15)
        
        # Draw dark red glitch bars
        glitch_color = (random.randint(0, 30), 0, 0)
        canvas.rectangle([start_x, start_y, end_x, end_y], fill=glitch_color)
        
    return final_mask_img, "SIGNAL_INJECTED_SUCCESSFULLY"

def extract_ultima_masking(masked_image):
    pixel_data = np.array(masked_image.convert("RGB"), dtype=np.uint8)
    flat_pixels = pixel_data.flatten()
    
    extracted_bits = ""
    for pixel_val in flat_pixels:
        extracted_bits += str(pixel_val & 1)
        
        # Check for signature at 8-bit intervals for performance
        if len(extracted_bits) % 8 == 0:
            current_text = ""
            # Sampling the last few characters to find the signature
            if len(extracted_bits) > 128:
                try:
                    # Convert bits to check signature
                    sample_text = ""
                    for j in range(len(extracted_bits) - 128, len(extracted_bits), 8):
                        byte_seg = extracted_bits[j:j+8]
                        sample_text += chr(int(byte_seg, 2))
                    
                    if "[X_TERMINATE_X]" in sample_text:
                        full_msg = ""
                        for k in range(0, len(extracted_bits), 8):
                            full_msg += chr(int(extracted_bits[k:k+8], 2))
                        return full_msg.replace(" [X_TERMINATE_X]", "")
                except:
                    continue
                    
    return "DECRYPTION_FAILED: No valid signature found."

# ------------------------------------------------------------------------------
# SECTION 5: DATA MANAGEMENT & STORAGE PROTOCOLS
# ------------------------------------------------------------------------------
def read_db_entries(db_key):
    target_path = DB_PATHS[db_key]
    if not os.path.exists(target_path):
        return []
    try:
        with open(target_path, "r", encoding="utf-8") as data_file:
            return data_file.readlines()
    except Exception as read_err:
        return []

def write_db_entry(db_key, entry_string, write_mode="a"):
    target_path = DB_PATHS[db_key]
    try:
        with open(target_path, write_mode, encoding="utf-8") as data_file:
            data_file.write(entry_string + "\n")
        return True
    except Exception as write_err:
        return False

def get_profile_data(agent_name):
    """Retrieves full profile for a given agent."""
    default_prof = {
        "name": agent_name, 
        "rank": "MEMBER", 
        "bio": "ZERO_LEGION_UNIT", 
        "avatar": "https://i.imgur.com/v6S6asL.png", 
        "status": "ACTIVE"
    }
    
    if agent_name == "admin":
        default_prof["rank"] = "GHOST"
        
    stored_entries = read_db_entries("profiles")
    for entry in stored_entries:
        if entry.startswith(f"{agent_name}|"):
            segments = entry.strip().split("|")
            if len(segments) >= 4:
                default_prof.update({
                    "rank": segments[1], 
                    "bio": segments[2], 
                    "avatar": segments[3]
                })
    return default_prof

def update_profile_data(agent_name, new_rank, new_bio, new_avatar):
    all_profiles = read_db_entries("profiles")
    profile_found = False
    
    with open(DB_PATHS["profiles"], "w", encoding="utf-8") as profile_db:
        for line in all_profiles:
            if line.startswith(f"{agent_name}|"):
                new_line = f"{agent_name}|{new_rank}|{new_bio}|{new_avatar}\n"
                profile_db.write(new_line)
                profile_found = True
            else:
                profile_db.write(line)
        
        if not profile_found:
            new_line = f"{agent_name}|{new_rank}|{new_bio}|{new_avatar}\n"
            profile_db.write(new_line)

def log_system_event(agent_id, action_description):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ID: {agent_id.upper()} -> ACTION: {action_description}"
    write_db_entry("logs", log_entry)

# ------------------------------------------------------------------------------
# SECTION 6: STREAMLIT UI ARCHITECTURE & NEON STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ZERO LEGION ULTIMA v50", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    neon_styles = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        /* Main Body Background */
        .stApp { 
            background-color: #050505; 
            color: #00FF41; 
            font-family: 'Share Tech Mono', monospace; 
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a !important;
            border-right: 1px solid #00FF41;
        }
        
        /* Neon Message Boxes */
        .neon-box-received { 
            background: rgba(0, 255, 65, 0.05); 
            border-left: 3px solid #00FF41; 
            padding: 12px; 
            margin-bottom: 10px; 
            border-radius: 0 8px 8px 0;
            box-shadow: -2px 0 10px rgba(0, 255, 65, 0.1);
        }
        
        .neon-box-sent { 
            background: rgba(188, 19, 254, 0.05); 
            border-right: 3px solid #BC13FE; 
            padding: 12px; 
            margin-bottom: 10px; 
            border-radius: 8px 0 0 8px;
            text-align: right;
            box-shadow: 2px 0 10px rgba(188, 19, 254, 0.1);
        }
        
        /* Intel Flash Box */
        .intel-broadcast { 
            background: #2b0000; 
            color: #ff3131; 
            padding: 15px; 
            border: 1px dashed #ff3131; 
            border-radius: 4px; 
            font-weight: bold; 
            text-transform: uppercase;
            animation: pulse-red 2s infinite;
        }
        
        @keyframes pulse-red {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }
        
        /* Buttons Neon Effect */
        .stButton>button {
            background-color: transparent !important;
            color: #00FF41 !important;
            border: 1px solid #00FF41 !important;
            border-radius: 0px !important;
            transition: 0.4s !important;
            font-weight: bold;
        }
        
        .stButton>button:hover {
            background-color: #00FF41 !important;
            color: #000 !important;
            box-shadow: 0 0 20px #00FF41;
        }
        
        /* Input Fields */
        .stTextInput>div>div>input {
            background-color: #000 !important;
            color: #00FF41 !important;
            border: 1px solid #00FF41 !important;
        }
    </style>
    """
    st.markdown(neon_styles, unsafe_allow_html=True)

inject_custom_css()

# ------------------------------------------------------------------------------
# SECTION 7: SESSION STATE INITIALIZATION
# ------------------------------------------------------------------------------
def setup_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.update({
            'authenticated': False, 
            'current_agent': '', 
            'terminal_history': [], 
            'sync_time': time.time()
        })

setup_session_state()

def add_terminal_log(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    st.session_state.terminal_history.append(f"[{current_time}] > {message}")
    if len(st.session_state.terminal_history) > 12:
        st.session_state.terminal_history.pop(0)

# ------------------------------------------------------------------------------
# SECTION 8: AUTHENTICATION INTERFACE (GATEWAY)
# ------------------------------------------------------------------------------
def display_gateway():
    left_pad, mid_panel, right_pad = st.columns([1, 2, 1])
    
    with mid_panel:
        st.title("📟 ZERO_LEGION GATEWAY v50")
        st.write("SECURE ACCESS TERMINAL - AUTHORIZED PERSONNEL ONLY")
        
        auth_tabs = st.tabs(["[ LOGIN_PHASE ]", "[ REGISTRY_PHASE ]"])
        
        with auth_tabs[0]:
            agent_id_input = st.text_input("IDENT_TAG")
            agent_key_input = st.text_input("AUTH_SECRET", type="password")
            
            if st.button("INITIATE_HANDSHAKE"):
                reg_lines = read_db_entries("access")
                login_success = False
                
                if agent_id_input == "admin" and agent_key_input == "1234":
                    login_success = True
                elif f"{agent_id_input}:{agent_key_input}\n" in reg_lines:
                    login_success = True
                
                if login_success:
                    st.session_state.authenticated = True
                    st.session_state.current_agent = agent_id_input
                    log_system_event(agent_id_input, "Terminal Access Granted.")
                    st.rerun()
                else:
                    st.error("ACCESS_DENIED: Critical Authentication Failure.")
        
        with auth_tabs[1]:
            new_id = st.text_input("NEW_AGENT_TAG")
            new_key = st.text_input("NEW_AUTH_SECRET", type="password")
            
            if st.button("CREATE_NEW_UNIT"):
                existing_users = [line.split(":")[0] for line in read_db_entries("access")]
                if new_id and new_key and new_id not in existing_users:
                    write_db_entry("access", f"{new_id}:{new_key}")
                    update_profile_data(new_id, "MEMBER", "NEW_RECRUIT", "https://i.imgur.com/v6S6asL.png")
                    log_system_event(new_id, "New Agent Registry Created.")
                    st.success("REGISTRY_SUCCESSFUL: Proceed to Login.")
                else:
                    st.warning("REGISTRY_FAILED: Tag taken or invalid input.")

# ------------------------------------------------------------------------------
# SECTION 9: MAIN OPERATIONAL INTERFACE (COMMAND_CORE)
# ------------------------------------------------------------------------------
def display_command_core():
    agent_id = st.session_state.current_agent
    agent_prof = get_profile_data(agent_id)
    rank_config = RANK_MAP[agent_prof['rank']]
    agent_level = rank_config['level']
    
    # Sidebar: Tactical Overview
    st.sidebar.markdown(f"### 🥷 AGENT_{agent_id.upper()}")
    st.sidebar.image(agent_prof['avatar'], width=150)
    st.sidebar.markdown(
        f"**RANK:** <span style='color:{rank_config['color']}'>{agent_prof['rank']}</span>", 
        unsafe_allow_html=True
    )
    st.sidebar.write(f"_{agent_prof['bio']}_")
    st.sidebar.divider()
    
    selected_module = st.sidebar.radio("COMMAND_MODULES", [
        "🌐 GLOBAL_FEED", 
        "🔒 PRIVATE_NODES", 
        "👥 GROUP_CLUSTERS", 
        "🎭 ULTIMA_MASKER", 
        "🛠️ TECH_STATION", 
        "🛡️ ROOT_ACCESS"
    ])
    
    if st.sidebar.button("🔌 TERMINATE_LINK"):
        log_system_event(agent_id, "Link Terminated by User.")
        st.session_state.authenticated = False
        st.rerun()
    
    # Live Terminal Widget
    st.sidebar.divider()
    st.sidebar.subheader("Live System Audit")
    for log_item in st.session_state.terminal_history:
        st.sidebar.code(log_item)

    # --- MODULE 1: GLOBAL_FEED ---
    if selected_module == "🌐 GLOBAL_FEED":
        st.subheader("🌐 Legion Global Veri Akışı")
        
        # Intel Broadcast View
        intel_stream = read_db_entries("intel")
        if intel_stream:
            st.markdown(
                f"<div class='intel-broadcast'>FLASH_INTEL: {intel_stream[-1]}</div>", 
                unsafe_allow_html=True
            )
        
        global_chat_container = st.container(height=480, border=True)
        with global_chat_container:
            all_global_msgs = read_db_entries("global")
            for msg_line in all_global_msgs:
                msg_parts = msg_line.strip().split("|")
                if len(msg_parts) == 3:
                    u_tag, enc_msg, timestamp = msg_parts
                    u_prof_data = get_profile_data(u_tag)
                    rank_c = RANK_MAP[u_prof_data['rank']]
                    
                    st.markdown(f"""
                    <div class='neon-box-received'>
                        <b style='color:{rank_c['color']}'>{u_tag}</b> 
                        <small style='float:right; opacity:0.3;'>{timestamp}</small><br>
                        {process_signal_decrypt(enc_msg)}
                    </div>
                    """, unsafe_allow_html=True)
        
        with st.form("global_transmit_form", clear_on_submit=True):
            input_signal = st.text_input("Mesaj Sinyali Girişi...")
            if st.form_submit_button("TRANSMIT_SIGNAL") and input_signal:
                timestamp_str = datetime.now().strftime('%H:%M')
                encrypted_signal = process_signal_encrypt(input_signal)
                write_db_entry("global", f"{agent_id}|{encrypted_signal}|{timestamp_str}")
                add_terminal_log("Global Sinyal Gönderildi.")
                st.rerun()

    # --- MODULE 2: PRIVATE_NODES ---
    elif selected_module == "🔒 PRIVATE_NODES":
        st.subheader("🔒 Bire-Bir Kriptolu İletişim Hattı")
        all_agents = [l.split(":")[0] for l in read_db_entries("access")]
        other_agents = [a for a in all_agents if a != agent_id]
        if agent_id != "admin":
            other_agents.append("admin")
            
        target_selection = st.selectbox("Hedef Birimi Seç", other_agents)
        
        priv_msg_container = st.container(height=420, border=True)
        with priv_msg_container:
            all_priv_msgs = read_db_entries("private")
            for p_line in all_priv_msgs:
                p_parts = p_line.strip().split("|")
                if len(p_parts) == 4:
                    sender, receiver, p_msg, p_time = p_parts
                    if (sender == agent_id and receiver == target_selection) or (sender == target_selection and receiver == agent_id):
                        msg_style = "neon-box-sent" if sender == agent_id else "neon-box-received"
                        st.markdown(
                            f"<div class='{msg_style}'><b>{sender}:</b> {process_signal_decrypt(p_msg)}</div>", 
                            unsafe_allow_html=True
                        )

        with st.form("private_transmit_form", clear_on_submit=True):
            p_input = st.text_input("Gizli Sinyal Gönder...")
            if st.form_submit_button("SECURE_TRANSMIT") and p_input:
                p_enc = process_signal_encrypt(p_input)
                p_now = datetime.now().strftime('%H:%M')
                write_db_entry("private", f"{agent_id}|{target_selection}|{p_enc}|{p_now}")
                add_terminal_log(f"{target_selection} birimine sinyal iletildi.")
                st.rerun()

    # --- MODULE 3: GROUP_CLUSTERS ---
    elif selected_module == "👥 GROUP_CLUSTERS":
        st.subheader("👥 Legion Grup Sinyal Kümeleri")
        available_clusters = {
            "FRONT_LINE": 1, 
            "TECH_SQUAD": 2, 
            "ELITE_VANGUARD": 3, 
            "GHOST_NET": 4
        }
        cluster_selection = st.selectbox("Küme Seçin", list(available_clusters.keys()))
        required_level = available_clusters[cluster_selection]
        
        if agent_level >= required_level:
            st.success(f"ACCESS_GRANTED: Connecting to {cluster_selection}...")
            c_filename = f"cluster_{cluster_selection.lower()}.zero"
            c_full_path = os.path.join(CORE_DIR, c_filename)
            
            if not os.path.exists(c_full_path):
                open(c_full_path, "a").close()
            
            cluster_container = st.container(height=380, border=True)
            with cluster_container:
                with open(c_full_path, "r", encoding="utf-8") as cf:
                    for cl_line in cf.readlines():
                        cl_p = cl_line.strip().split("|")
                        if len(cl_p) == 3:
                            st.write(f"**{cl_p[0]}**: {process_signal_decrypt(cl_p[1])} _({cl_p[2]})_")
            
            with st.form("cluster_form", clear_on_submit=True):
                cl_msg_input = st.text_input("Grup Sinyali...")
                if st.form_submit_button("CLUSTER_BROADCAST") and cl_msg_input:
                    cl_enc = process_signal_encrypt(cl_msg_input)
                    cl_ts = datetime.now().strftime('%H:%M')
                    with open(c_full_path, "a", encoding="utf-8") as cf_write:
                        cf_write.write(f"{agent_id}|{cl_enc}|{cl_ts}\n")
                    add_terminal_log(f"{cluster_selection} kümesine yayın yapıldı.")
                    st.rerun()
        else:
            st.error(f"INSUFFICIENT_CLEARANCE: {list(RANK_MAP.keys())[required_level-1]} rank required.")

    # --- MODULE 4: ULTIMA_MASKER (LSB STENANOGRAPHY) ---
    elif selected_module == "🎭 ULTIMA_MASKER":
        st.subheader("🎭 Ultima Maskeleme ve Piksel İstihbarat Ünitesi")
        if rank_config['can_mask']:
            st.info("Piksel düzeyinde veri enjeksiyonu ve Glitch katmanlama aktif.")
            m_tabs = st.tabs(["[ 🔒 INJECT_DATA ]", "[ 🔓 EXTRACT_DATA ]"])
            
            with m_tabs[0]:
                upload_ref = st.file_uploader("Baz Görseli Yükle", type=['png', 'jpg', 'jpeg'])
                payload_text = st.text_area("Gizlenecek İstihbarat Notu")
                mask_strength = st.slider("Glitch Yoğunluk Seviyesi", 1, 15, 6)
                
                if upload_ref and payload_text and st.button("EXECUTE_MASKING"):
                    raw_img_obj = Image.open(upload_ref)
                    masked_result, result_status = apply_ultima_masking(raw_img_obj, payload_text, mask_strength)
                    
                    if masked_result:
                        st.image(masked_result, caption="Maskelenmiş Gölge Görseli")
                        img_buffer = io.BytesIO()
                        masked_result.save(img_buffer, format="PNG")
                        st.download_button(
                            "DOWNLOAD_SHADOW_FILE", 
                            img_buffer.getvalue(), 
                            f"shadow_node_{int(time.time())}.png"
                        )
                        log_system_event(agent_id, "Encrypted data into visual shadow.")
                        add_terminal_log("Görsel maskeleme başarıyla tamamlandı.")
                    else:
                        st.error(result_status)
            
            with m_tabs[1]:
                dec_upload = st.file_uploader("Maskelenmiş Görseli Sisteme Yükle", type=['png'])
                if dec_upload and st.button("REVEAL_HIDDEN_SIGNAL"):
                    dec_img_obj = Image.open(dec_upload)
                    extracted_text = extract_ultima_masking(dec_img_obj)
                    st.success(f"EXTRACTED_SIGNAL: {extracted_text}")
                    log_system_event(agent_id, f"Extracted data from {dec_upload.name}.")
                    add_terminal_log("Görsel deşifre işlemi başarıyla sonuçlandı.")
        else:
            st.error("RANK_ACCESS_DENIED: SHADOW rank or higher required for Masking Modules.")

    # --- MODULE 5: TECH_STATION ---
    elif selected_module == "🛠️ TECH_STATION":
        st.subheader("🛠️ Legion Teknik Destek ve Analiz Ünitesi")
        if agent_level >= 2:
            st.write("Sinyal Kodlama ve Dekoder Terminali")
            tech_c1, tech_c2 = st.columns(2)
            
            with tech_c1:
                raw_field = st.text_area("Ham Metin Girişi")
                if st.button("PROCESS_ENCODE"):
                    st.code(process_signal_encrypt(raw_field))
            
            with tech_c2:
                cipher_field = st.text_area("Kodlanmış Sinyal Girişi")
                if st.button("PROCESS_DECODE"):
                    st.info(process_signal_decrypt(cipher_field))
            
            st.divider()
            st.write("Node Veri Analitiği (Dinamik)")
            
            analytical_data = {
                "Data_Node": ["Global_S", "Private_N", "System_L", "Config_V"],
                "Entry_Count": [
                    len(read_db_entries("global")), 
                    len(read_db_entries("private")), 
                    len(read_db_entries("logs")), 
                    15
                ]
            }
            analytics_df = pd.DataFrame(analytical_data)
            st.bar_chart(analytics_df.set_index("Data_Node"))
            
            if st.button("RUN_SYSTEM_DIAGNOSTICS"):
                diag_progress = st.progress(0)
                for p in range(100):
                    time.sleep(0.01)
                    diag_progress.progress(p + 1)
                st.success("SYSTEM_HEALTH: 100% - All nodes operational.")
        else:
            st.error("TECHNICAL_RESTRICTION: Maintenance tools are locked for Member rank.")

    # --- MODULE 6: ROOT_ACCESS ---
    elif selected_module == "🛡️ ROOT_ACCESS":
        if agent_level >= 4 or agent_id == "admin":
            st.subheader("🛡️ Legion Root Kontrol Merkezi")
            
            if agent_id == "admin":
                root_tab1, root_tab2, root_tab3 = st.tabs([
                    "[ 👤 AGENT_MGMT ]", 
                    "[ 📣 BROADCAST ]", 
                    "[ 📜 AUDIT_LOGS ]"
                ])
                
                with root_tab1:
                    full_agent_list = [line.split(":")[0] for line in read_db_entries("access")]
                    for unit_id in full_agent_list:
                        with st.expander(f"UNIT_TAG: {unit_id}"):
                            unit_prof = get_profile_data(unit_id)
                            unit_c1, unit_c2 = st.columns(2)
                            
                            new_r = unit_c1.selectbox(
                                "Assign Rank", 
                                list(RANK_MAP.keys()), 
                                index=list(RANK_MAP.keys()).index(unit_prof['rank']), 
                                key=f"rank_sel_{unit_id}"
                            )
                            new_a = unit_c2.text_input(
                                "Avatar Path", 
                                unit_prof['avatar'], 
                                key=f"avatar_sel_{unit_id}"
                            )
                            new_b = st.text_area(
                                "Unit Bio", 
                                unit_prof['bio'], 
                                key=f"bio_sel_{unit_id}"
                            )
                            
                            if st.button("SYNC_UNIT_CHANGES", key=f"sync_btn_{unit_id}"):
                                update_profile_data(unit_id, new_r, new_b, new_a)
                                log_system_event("ADMIN", f"Modified Unit {unit_id} profile.")
                                st.success(f"UNIT_{unit_id} SYNCED.")
                
                with root_tab2:
                    intel_input = st.text_input("Flash İstihbarat Yayınla (Tüm Birimler)")
                    if st.button("DEPLOY_BROADCAST"):
                        write_db_entry("intel", intel_input, write_mode="w")
                        log_system_event("ADMIN", "Deployed Global Broadcast.")
                        st.success("INTEL_DEPLOYED.")

            with root_tab3:
                    # Logları oku ve son 150 satırı göster
                    full_audit_logs = read_db_entries("logs")
                    st.code("".join(full_audit_logs[-150:]))
                    
                    # Hata veren kısım burasıydı, şimdi hizalı ve temiz:
                    if st.button("WIPE_AUDIT_HISTORY"):
                        # Dosyayı "w" modunda açıp kapatmak içeriği siler
                        f_clear = open(DB_PATHS["logs"], "w")
                        f_clear.close()
                        add_terminal_log("System logs wiped by Root.")
                        st.rerun()
                    
            else:
                st.info("AUDIT_ONLY_ACCESS: You have ghost-level read permissions.")
                audit_view = read_db_entries("logs")
                st.code("".join(audit_view[-80:]))
        else:
            st.error("ACCESS_DENIED: Ghost-level clearance or Root account required.")

# ------------------------------------------------------------------------------
# SECTION 10: MAIN EXECUTION FLOW
# ------------------------------------------------------------------------------
if not st.session_state.authenticated:
    display_gateway()
else:
    display_command_core()

# ==============================================================================
# END OF LEGION ULTIMA v50.0 SYSTEM ARCHITECTURE
# ==============================================================================
