import streamlit as st
import streamlit.components.v1 as components
import json
import time
import math
import os

# --- 1. ADSENSE INJECTION ---
components.html(
    """
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8679117636092243" 
    crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-8679117636092243">
    """,
    height=0,
)

# --- 2. CONFIG ---
st.set_page_config(page_title="DIAMOND EMPIRE: OVERDRIVE", layout="wide", initial_sidebar_state="collapsed")

# --- STATE INITIALIZATION ---
if 'money' not in st.session_state:
    st.session_state.update({
        'money': 0, 
        'upgrades': {str(k): 0 for k in range(12)}, 
        'prestige_points': 0,
        'surge_count': 0, 
        'surge_active': False, 
        'surge_end': 0, 
        'level': 1, 
        'total_earned': 0,
        'last_tick': time.time(),
        'ability_cooldown': 0
    })

# --- THE 12-ITEM ASSET LIST ---
BUILDINGS = {
    "0": {"name": "Diamond Siphon", "cost": 15, "pwr": 1, "icon": "💠", "anim": "stab 1s infinite"},
    "1": {"name": "Industrial Scrapper", "cost": 100, "pwr": 5, "icon": "⚙️", "anim": "spin 2s linear infinite"},
    "2": {"name": "Mining Nano-Bot", "cost": 1100, "pwr": 22, "icon": "🤖", "anim": "bounce 1.2s infinite"},
    "3": {"name": "Thermal Cyber-Drill", "cost": 12000, "pwr": 95, "icon": "🌀", "anim": "shake 0.1s infinite"},
    "4": {"name": "Automated Mega-Factory", "cost": 140000, "pwr": 500, "icon": "🏭", "anim": "pulse 3s infinite"},
    "5": {"name": "Satellite Laser Array", "cost": 1.5e6, "pwr": 2500, "icon": "🛰️", "anim": "float 5s infinite"},
    "6": {"name": "Void Siphon Core", "cost": 25e6, "pwr": 13000, "icon": "🌌", "anim": "spin 10s linear infinite"},
    "7": {"name": "Dyson Harvesting Swarm", "cost": 400e6, "pwr": 80000, "icon": "🌟", "anim": "float 2s infinite"},
    "8": {"name": "Dimensional Ripper", "cost": 6e9, "pwr": 500000, "icon": "⚡", "anim": "pulse 1s infinite"},
    "9": {"name": "Galaxy Crusher", "cost": 95e9, "pwr": 2.5e6, "icon": "🪐", "anim": "spin 5s linear infinite"},
    "10": {"name": "Time-Loop Miner", "cost": 1.8e12, "pwr": 18e6, "icon": "⏳", "anim": "bounce 0.6s infinite"},
    "11": {"name": "Universal Reset Core", "cost": 60e12, "pwr": 150e6, "icon": "💎", "anim": "pulse 0.2s infinite"},
}

# --- CALCULATIONS ---
prestige_mult = 1 + (st.session_state.prestige_points * 0.1)
def get_current_mps():
    base_mps = sum(int(st.session_state.upgrades[t]) * b['pwr'] for t, b in BUILDINGS.items())
    return base_mps * prestige_mult

# --- HACKER SIDEBAR ---
with st.sidebar:
    st.header("🛠️ ADMIN TOOLS")
    if st.button("🚀 ADD $1 TRILLION"):
        st.session_state.money += 1_000_000_000_000
        st.rerun()
    if st.button("🧹 RESET ALL"):
        st.session_state.clear()
        st.rerun()

# --- LOGIC ---
is_surging = st.session_state.surge_active and time.time() < st.session_state.surge_end
multiplier = 5 if is_surging else 1
accent = "#ff00ff" if is_surging else "#00ffcc"

# --- CSS (UI IMPROVEMENTS) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #020202; color: #f0f0f0; }}
    .prestige-box {{ background: linear-gradient(45deg, #440066, #110022); padding: 15px; border-radius: 10px; border: 1px solid #ff00ff; text-align: center; margin-bottom: 20px; }}
    .ability-btn {{ background: #222; border: 1px solid {accent}; color: white; padding: 10px; border-radius: 5px; width: 100%; cursor: pointer; }}
    </style>
    """, unsafe_allow_html=True)

l, m, r = st.columns([1, 1.8, 1.2])

with l:
    st.markdown(f"<div class='prestige-box'>✨ PRESTIGE LEVEL: {st.session_state.prestige_points}<br><small>Multiplier: {round(prestige_mult, 1)}x</small></div>", unsafe_allow_html=True)
    st.markdown(f"<h1>${st.session_state.money:,.0f}</h1>", unsafe_allow_html=True)
    
    # ABILITY BUTTON
    can_use_ability = time.time() > st.session_state.ability_cooldown
    if st.button("🌀 DIAMOND STORM (10x Click)", disabled=not can_use_ability):
        st.session_state.money += (get_current_mps() * 50)
        st.session_state.ability_cooldown = time.time() + 60 # 1 minute cooldown
        st.rerun()
    
    if not can_use_ability:
        st.caption(f"Ability recharging...")

    st.markdown(f'<div class="main-clicker" style="font-size:100px; text-align:center; cursor:pointer;">💎</div>', unsafe_allow_html=True)
    if st.button("MANUAL EXTRACT", use_container_width=True):
        st.session_state.money += (1 + (get_current_mps() * 0.1)) * multiplier
        st.rerun()

with m:
    st.markdown("### 🌌 PRODUCTION")
    # PRESTIGE BUTTON (Only shows if rich enough)
    if st.session_state.money >= 1_000_000_000_000:
        new_points = int(st.session_state.money / 1_000_000_000_000)
        if st.button(f"✨ PERFORM SUPERNOVA (Gain {new_points} Prestige Points)"):
            st.session_state.prestige_points += new_points
            st.session_state.money = 0
            st.session_state.upgrades = {str(k): 0 for k in range(12)}
            st.rerun()

    for tid, data in BUILDINGS.items():
        count = int(st.session_state.upgrades[tid])
        if count > 0:
            st.markdown(f"{data['icon']} **{data['name']}**: {count}")

with r:
    st.markdown("#### 🛒 SHOP")
    for tid, data in BUILDINGS.items():
        count = int(st.session_state.upgrades[tid])
        cost = int(data['cost'] * (1.15 ** count))
        if st.button(f"BUY {data['icon']} (${cost:,})", key=f"b_{tid}", use_container_width=True):
            if st.session_state.money >= cost:
                st.session_state.money -= cost
                st.session_state.upgrades[tid] += 1
                st.rerun()

# --- TICK ENGINE ---
now = time.time()
elapsed = now - st.session_state.last_tick
if elapsed >= 1.0:
    st.session_state.money += (get_current_mps() * multiplier * elapsed)
    st.session_state.last_tick = now
    st.rerun()
