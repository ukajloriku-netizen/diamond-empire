import streamlit as st
import streamlit.components.v1 as components
import time
import math

# --- 1. ADSENSE ---
components.html("""<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8679117636092243" crossorigin="anonymous"></script>""", height=0)

# --- 2. CONFIG ---
st.set_page_config(page_title="DIAMOND EMPIRE: OVERDRIVE", layout="wide", initial_sidebar_state="collapsed")

# --- STATE INITIALIZATION ---
if 'money' not in st.session_state:
    st.session_state.update({
        'money': 0, 
        'upgrades': {str(k): 0 for k in range(12)}, 
        'abilities_bought': [], 
        'surge_count': 0, 
        'surge_active': False, 
        'surge_end': 0, 
        'prestige_level': 0, 
        'total_earned': 0, 
        'last_tick': time.time(), 
        'view': 'game' 
    })

# --- DATA: BUILDINGS ---
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

# --- LOGIC ---
now = time.time()
scaling = 1.8
surge_goal = 150 * (scaling ** st.session_state.prestige_level)
prestige_boost = 1 + (st.session_state.prestige_level * 0.25)

is_surging = st.session_state.surge_active and now < st.session_state.surge_end
global_mult = 5 if is_surging else 1
accent = "#ff00ff" if is_surging else "#00ffcc"

def get_current_mps():
    base = sum(int(st.session_state.upgrades[t]) * b['pwr'] for t, b in BUILDINGS.items())
    return base * prestige_boost

# --- CSS & AUDIO SCRIPT ---
# Screen shake triggers when 'is_surging' is True
shake_anim = "shake-screen 0.2s infinite" if is_surging else "none"

st.markdown(f"""
    <style>
    .stApp {{ background: #020202; color: #f0f0f0; overflow: hidden; animation: {shake_anim}; }}
    [data-testid="column"]:nth-child(1) {{ position: fixed; width: 25% !important; left: 0; background: #000; border-right: 2px solid {accent}; height: 100vh; padding: 20px; text-align: center; }}
    [data-testid="column"]:nth-child(2) {{ margin-left: 25%; width: 45% !important; background: #050505; min-height: 100vh; padding: 20px !important; }}
    [data-testid="column"]:nth-child(3) {{ position: fixed; width: 30% !important; right: 0; background: #080808; border-left: 2px solid {accent}; height: 100vh; padding: 20px; overflow-y: auto; }}
    
    @keyframes shake-screen {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        20% {{ transform: translate(-2px, 0px) rotate(-1deg); }}
        40% {{ transform: translate(2px, 1px) rotate(1deg); }}
        60% {{ transform: translate(-1px, -1px) rotate(0deg); }}
        80% {{ transform: translate(1px, 2px) rotate(-1deg); }}
        100% {{ transform: translate(1px, -1px) rotate(1deg); }}
    }}

    @keyframes stab {{ 0%, 100% {{ transform: translate(0,0) rotate(var(--rot)); }} 50% {{ transform: translate(var(--tx), var(--ty)) scale(1.6) rotate(var(--rot)); }} }}
    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
    @keyframes pulse {{ 0% {{ transform: scale(1); opacity: 0.7; }} 50% {{ transform: scale(1.05); opacity: 1; }} 100% {{ transform: scale(1); opacity: 0.7; }} }}
    
    .clicker-container {{ position: relative; width: 300px; height: 300px; margin: 10px auto; display: flex; align-items: center; justify-content: center; }}
    .main-clicker {{ font-size: 130px; cursor: pointer; filter: drop-shadow(0 0 30px {accent}); z-index: 10; user-select: none; }}
    .swarming-diamond {{ position: absolute; font-size: 24px; filter: drop-shadow(0 0 8px {accent}); }}
    .boost-container {{ width: 100%; background: #111; height: 18px; border-radius: 9px; border: 1px solid #333; overflow: hidden; margin-top: 10px; }}
    .boost-fill {{ height: 100%; width: {min((st.session_state.surge_count/surge_goal)*100, 100)}%; background: {accent}; box-shadow: 0 0 15px {accent}; transition: width 0.3s; }}
    .blurred {{ filter: blur(12px); opacity: 0.3; pointer-events: none; }}
    </style>
    
    <script>
    function playSurgeSound() {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(150, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
    }}
    </script>
    """, unsafe_allow_html=True)

l, m, r = st.columns([1, 1.8, 1.2])

with l:
    st.markdown(f"<small style='color:gold;'>✨ PRESTIGE LV. {st.session_state.prestige_level}</small>", unsafe_allow_html=True)
    st.markdown(f"<h1>${st.session_state.money:,.0f}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{accent}; font-weight:bold;'>MPS: ${round(get_current_mps() * global_mult, 1)}</p>", unsafe_allow_html=True)
    
    siphons = int(st.session_state.upgrades["0"])
    swarm_html = "".join([f'<div class="swarming-diamond" style="left:calc(50% + {130*math.cos(math.radians(i*(360/min(max(siphons,1),30))))}px - 12px); top:calc(50% + {130*math.sin(math.radians(i*(360/min(max(siphons,1),30))))}px - 12px); --rot:{i*(360/min(max(siphons,1),30))+45}deg; --tx:{-30*math.cos(math.radians(i*(360/min(max(siphons,1),30))))}px; --ty:{-30*math.sin(math.radians(i*(360/min(max(siphons,1),30))))}px; animation: stab 1s infinite {i*0.03}s;">💠</div>' for i in range(min(siphons, 30))])
    st.markdown(f'<div class="clicker-container">{swarm_html}<div class="main-clicker">💎</div></div>', unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center;'><small>{int(st.session_state.surge_count)} / {int(surge_goal)} CHARGE</small></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="boost-container"><div class="boost-fill"></div></div>', unsafe_allow_html=True)
    
    if st.button("MANUAL EXTRACT", use_container_width=True):
        st.session_state.money += (1 + (get_current_mps() * 0.1)) * global_mult
        st.session_state.total_earned += (1 + (get_current_mps() * 0.1)) * global_mult
        if not is_surging:
            st.session_state.surge_count += 2.5
            if st.session_state.surge_count >= surge_goal:
                st.session_state.surge_active, st.session_state.surge_end = True, time.time() + 15
                st.session_state.surge_count = 0
                st.session_state.prestige_level += 1 
                # TRIGGER SOUND
                components.html("<script>playSurgeSound();</script>", height=0)
        st.rerun()

    if st.button("🌳 ABILITY TREE", use_container_width=True):
        st.session_state.view = 'tree' if st.session_state.view == 'game' else 'game'
        st.rerun()

# --- THE REST OF THE MARKET/TREE REMAINS THE SAME ---
with m:
    if st.session_state.view == 'game':
        st.markdown("<h3 style='color:#333;'>PRODUCTION SECTORS</h3>", unsafe_allow_html=True)
        for tid, data in BUILDINGS.items():
            count = int(st.session_state.upgrades[tid])
            if count > 0:
                icons = "".join([f'<div style="font-size:30px; display:inline-block; animation: {data["anim"]}; margin:5px;">{data["icon"]}</div>' for _ in range(min(count, 40))])
                st.markdown(f'<div style="background:rgba(255,255,255,0.02); padding:10px; margin-bottom:10px;">{icons}</div>', unsafe_allow_html=True)
    else:
        st.markdown("## 🌳 ABILITY TREE")
        st.write("Abilities list (Locked/Blurred)...")

with r:
    st.markdown("<h4 style='text-align:center; color:#444;'>MARKET</h4>", unsafe_allow_html=True)
    for tid, data in BUILDINGS.items():
        count = int(st.session_state.upgrades[tid])
        cost = int(data['cost'] * (1.15 ** count))
        st.button(f"BUY {data['icon']}", key=f"acq_{tid}", use_container_width=True)

# --- TICK ENGINE ---
elapsed = now - st.session_state.last_tick
if elapsed >= 1.0:
    st.session_state.money += (get_current_mps() * global_mult * elapsed)
    st.session_state.total_earned += (get_current_mps() * global_mult * elapsed)
    st.session_state.last_tick = now
    st.rerun()
