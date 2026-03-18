import streamlit as st
import json
import time
import math
import os

# --- CONFIG ---
st.set_page_config(page_title="DIAMOND EMPIRE: OVERDRIVE", layout="wide", initial_sidebar_state="collapsed")

# --- SAVING/LOADING ---
DB_FILE = "empire_grind_save.json"

def save_game():
    data = {
        'money': st.session_state.money, 
        'upgrades': st.session_state.upgrades,
        'surge_count': st.session_state.surge_count,
        'level': st.session_state.level,
        'total_earned': st.session_state.total_earned
    }
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

def load_game():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return None
    return None

# --- STATE INITIALIZATION ---
if 'money' not in st.session_state:
    loaded = load_game()
    default_upgrades = {str(k): 0 for k in range(12)} 
    if not loaded:
        st.session_state.update({'money': 0, 'upgrades': default_upgrades, 'surge_count': 0, 'surge_active': False, 'surge_end': 0, 'level': 1, 'total_earned': 0})
    else:
        st.session_state.update({
            'money': loaded.get('money', 0), 
            'upgrades': loaded.get('upgrades', default_upgrades), 
            'surge_count': loaded.get('surge_count', 0), 
            'level': loaded.get('level', 1),
            'total_earned': loaded.get('total_earned', 0),
            'surge_active': False, 'surge_end': 0
        })
    st.session_state.last_tick = time.time()

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

def get_current_mps():
    return sum(int(st.session_state.upgrades[t]) * b['pwr'] for t, b in BUILDINGS.items())

# --- THE GRIND LOGIC ---
# Every level increases the Surge requirement by a power of 1.8 (Harder Grind)
SURGE_GOAL = 150 * (st.session_state.level ** 1.8) 

# Progression for Leveling Up
next_level_cost = 5000 * (st.session_state.level ** 2.2)
if st.session_state.total_earned >= next_level_cost:
    st.session_state.level += 1

is_surging = st.session_state.surge_active and time.time() < st.session_state.surge_end
multiplier = 5 if is_surging else 1
accent = "#ff00ff" if is_surging else "#00ffcc"

# --- CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background: #020202; color: #f0f0f0; overflow: hidden; }}
    [data-testid="column"]:nth-child(1) {{ position: fixed; width: 25% !important; left: 0; background: #000; border-right: 2px solid {accent}; height: 100vh; padding: 20px; text-align: center; }}
    [data-testid="column"]:nth-child(2) {{ margin-left: 25%; width: 45% !important; background: #050505; min-height: 100vh; padding: 20px !important; }}
    [data-testid="column"]:nth-child(3) {{ position: fixed; width: 30% !important; right: 0; background: #080808; border-left: 2px solid {accent}; height: 100vh; padding: 20px; overflow-y: auto; }}

    @keyframes stab {{ 0%, 100% {{ transform: translate(0,0) rotate(var(--rot)); }} 50% {{ transform: translate(var(--tx), var(--ty)) scale(1.6) rotate(var(--rot)); }} }}
    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
    @keyframes pulse {{ 0% {{ transform: scale(1); opacity: 0.7; }} 50% {{ transform: scale(1.05); opacity: 1; }} 100% {{ transform: scale(1); opacity: 0.7; }} }}

    .clicker-container {{ position: relative; width: 340px; height: 340px; margin: 20px auto; display: flex; align-items: center; justify-content: center; }}
    .main-clicker {{ font-size: 140px; cursor: pointer; filter: drop-shadow(0 0 30px {accent}); transition: 0.1s; z-index: 10; user-select: none; }}
    .swarming-diamond {{ position: absolute; font-size: 24px; filter: drop-shadow(0 0 8px {accent}); }}

    .boost-container {{ width: 100%; background: #111; height: 18px; border-radius: 9px; border: 1px solid #333; overflow: hidden; margin-top: 10px; }}
    .boost-fill {{ height: 100%; width: {min((st.session_state.surge_count/SURGE_GOAL)*100, 100)}%; background: {accent}; box-shadow: 0 0 15px {accent}; transition: 0.2s; }}
    
    .shop-card {{ background: #111; padding: 12px; border-radius: 4px; border-left: 4px solid {accent}; margin-bottom: 8px; }}
    .blurred {{ filter: blur(8px); opacity: 0.2; }}
    </style>
    """, unsafe_allow_html=True)

l, m, r = st.columns([1, 1.8, 1.2])

with l:
    st.markdown(f"<small style='color:gold;'>LEVEL {st.session_state.level}</small>", unsafe_allow_html=True)
    st.markdown(f"<h1>${st.session_state.money:,.0f}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{accent}; font-weight:bold;'>MPS: ${round(get_current_mps() * multiplier, 1)}</p>", unsafe_allow_html=True)
    
    # SWARMING EFFECT
    siphons = int(st.session_state.upgrades["0"])
    swarm_html = "".join([f'<div class="swarming-diamond" style="left:calc(50% + {150*math.cos(math.radians(i*(360/min(siphons,30))))}px - 12px); top:calc(50% + {150*math.sin(math.radians(i*(360/min(siphons,30))))}px - 12px); --rot:{i*(360/min(siphons,30))+45}deg; --tx:{-30*math.cos(math.radians(i*(360/min(siphons,30))))}px; --ty:{-30*math.sin(math.radians(i*(360/min(siphons,30))))}px; animation: stab 1s infinite {i*0.03}s;">💠</div>' for i in range(min(siphons, 30))])
    st.markdown(f'<div class="clicker-container">{swarm_html}<div class="main-clicker">💎</div></div>', unsafe_allow_html=True)

    # SURGE BOOST BAR (GETS HARDER PER LEVEL)
    st.markdown(f"<small>5X SURGE PROGRESS (LV.{st.session_state.level})</small>", unsafe_allow_html=True)
    st.markdown(f'<div class="boost-container"><div class="boost-fill"></div></div>', unsafe_allow_html=True)

    if st.button("MANUAL EXTRACT", use_container_width=True):
        st.session_state.money += (1 + (get_current_mps() * 0.1)) * multiplier
        st.session_state.total_earned += (1 + (get_current_mps() * 0.1)) * multiplier
        st.session_state.surge_count += 2.5 # Manual clicks charge the 5x boost
        st.rerun()

with m:
    st.markdown("<h3 style='color:#333;'>PRODUCTION SECTORS</h3>", unsafe_allow_html=True)
    for tid, data in BUILDINGS.items():
        count = int(st.session_state.upgrades[tid])
        if count > 0:
            icons = "".join([f'<div style="font-size:30px; display:inline-block; animation: {data["anim"]}; margin:2px;">{data["icon"]}</div>' for _ in range(min(count, 40))])
            st.markdown(f'<div style="background:rgba(255,255,255,0.02); padding:10px; margin-bottom:10px; border-bottom:1px solid #222;">{icons}</div>', unsafe_allow_html=True)

with r:
    st.markdown("<h4 style='text-align:center; color:#444;'>MARKET</h4>", unsafe_allow_html=True)
    for tid, data in BUILDINGS.items():
        count = int(st.session_state.upgrades[tid])
        cost = int(data['cost'] * (1.15 ** count))
        unlocked = st.session_state.total_earned >= (data['cost'] * 0.5) or count > 0
        
        st.markdown(f"""
            <div class="shop-card {"blurred" if not unlocked else ""}">
                <div style="display:flex; justify-content:space-between;">
                    <b>{data['name'] if unlocked else "???"}</b> <span>x{count}</span>
                </div>
                <div style="font-size:18px; font-weight:bold;">${cost:,}</div>
                <div style="font-size:11px; color:{accent};">{f"+${data['pwr']}/s" if unlocked else "LOCKED"}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"BUY {data['icon'] if unlocked else '🔒'}", key=f"acq_{tid}", use_container_width=True):
            if st.session_state.money >= cost:
                st.session_state.money -= cost
                st.session_state.upgrades[tid] += 1
                save_game()
                st.rerun()

# --- TICK ENGINE ---
now = time.time()
elapsed = now - st.session_state.last_tick
if elapsed >= 1.0:
    st.session_state.money += (get_current_mps() * multiplier * elapsed)
    st.session_state.total_earned += (get_current_mps() * multiplier * elapsed)
    
    if not is_surging:
        # Siphons charge the boost bar automatically
        st.session_state.surge_count += (siphons * 0.5 * elapsed)
        if st.session_state.surge_count >= SURGE_GOAL:
            st.session_state.surge_active, st.session_state.surge_end, st.session_state.surge_count = True, now + 15, 0
            
    st.session_state.last_tick = now
    st.rerun()