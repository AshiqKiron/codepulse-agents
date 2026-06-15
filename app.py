import streamlit as st
import os
from datetime import datetime, timedelta

# ✅ ZERO MEMORY STATE
st.set_page_config(page_title="CodePulse", layout="wide")

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "zero"
if "preview_data" not in st.session_state:
    st.session_state.preview_data = None
if "full_results" not in st.session_state:
    st.session_state.full_results = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("️ Config")
    repo = st.text_input("Repo", "microsoft/vscode", key="repo")
    window = st.selectbox("Window", ["1H", "24H"], index=1, key="window")
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.stage = "zero"
        st.session_state.preview_data = None
        st.session_state.full_results = None
        st.rerun()

# --- HERO SECTION ---
st.markdown("""
<div style='padding:3rem 1rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
border-radius:16px;text-align:center;color:white;margin-bottom:2rem;
box-shadow:0 10px 30px rgba(0,0,0,0.3);'>
<h1 style='margin:0;font-size:2.8rem;font-weight:800'> CodePulse</h1>
<p style='font-size:1.3rem;opacity:0.95;margin-top:0.5rem;font-weight:500'>
VS Code Intelligence Platform
</p>
<span style='display:inline-block;background:rgba(255,255,255,0.2);
padding:0.4rem 1rem;border-radius:30px;font-size:0.9rem;margin-top:1.5rem;
backdrop-filter:blur(10px);'>
Progressive Loading • Zero Cold-Start Overhead
</span>
</div>
""", unsafe_allow_html=True)

# --- STAGE LOGIC ---
if st.session_state.stage == "zero":
    st.markdown("<div style='text-align:center;margin:2rem 0;'>", unsafe_allow_html=True)
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        st.session_state.stage = "preview"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)

elif st.session_state.stage == "preview":
    with st.spinner("Loading data sources..."):
        try:
            from agents.github_agent import GitHubAgent
            
            now = datetime.utcnow()
            since = (now - timedelta(hours=1)).isoformat() + "Z" \
                    if st.session_state.get("window", "24H") == "1H" \
                    else (now - timedelta(days=1)).isoformat() + "Z"
            
            gh = GitHubAgent()
            gh.repo = st.session_state.get("repo", "microsoft/vscode")
            issues = gh.get_top_issues(label="bug", limit=2, since=since)
            
            st.session_state.preview_data = {
                "issues": issues,
                "count": len(issues),
                "timestamp": now.strftime("%H:%M UTC")
            }
            st.session_state.stage = "preview_ready"
            st.rerun()
        except Exception as e:
            st.error(f"Preview failed: {str(e)[:100]}")
            st.session_state.stage = "zero"
            st.rerun()

elif st.session_state.stage == "preview_ready":
    d = st.session_state.preview_data
    
    if not d:
        st.error("Data lost. Please reset and try again.")
        st.session_state.stage = "zero"
        st.r
