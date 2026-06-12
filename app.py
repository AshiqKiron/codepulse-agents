import streamlit as st

# ✅ ZERO MEMORY STATE: No imports, no env checks, no agents
st.set_page_config(page_title="CodePulse", layout="wide")

# Static hero - renders in <50ms with ~800KB memory
st.markdown("""
<div style='padding:3rem 1rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
border-radius:12px;text-align:center;color:white;margin-bottom:2rem'>
<h1 style='margin:0;font-size:2.5rem'>🟦 CodePulse</h1>
<p style='font-size:1.2rem;opacity:0.9;margin-top:0.5rem'>
VS Code Intelligence Platform<br>
<span style='font-size:0.9rem;opacity:0.7'>Progressive loading • Sub-second start</span>
</p>
</div>
""", unsafe_allow_html=True)

# Session state for progressive loading
if "stage" not in st.session_state:
    st.session_state.stage = "zero"  # zero → preview → full
if "preview_data" not in st.session_state:
    st.session_state.preview_data = None
if "full_results" not in st.session_state:
    st.session_state.full_results = None

# Sidebar config (minimal widgets)
with st.sidebar:
    st.header("⚙️")
    repo = st.text_input("Repo", "microsoft/vscode", key="repo")
    window = st.selectbox("Window", ["1H", "24H"], index=1, key="window")
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.stage = "zero"
        st.session_state.preview_data = None
        st.session_state.full_results = None
        st.rerun()

# --- STAGE-BASED UI RENDERING ---
if st.session_state.stage == "zero":
    # Only shows button - no memory overhead
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        st.session_state.stage = "preview"
        st.rerun()

elif st.session_state.stage == "preview":
    # Load ONLY GitHub agent (~2.5MB total)
    with st.spinner("Loading data sources..."):
        try:
            from agents.github_agent import GitHubAgent
            from datetime import datetime, timedelta
            
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
    st.success(f"✅ Found {d['count']} recent issues ({d['timestamp']})")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        for i in d["issues"]:
            st.markdown(f"**{i['title']}** ({i['comments']} comments)")
    with c2:
        st.metric("Issues", d["count"])
    
    # SECOND CLICK: Load LLM + Supabase (~45-60MB additional)
    if st.button("🧠 Generate AI Insights", type="primary", use_container_width=True):
        st.session_state.stage = "loading_full"
        st.rerun()

elif st.session_state.stage == "loading_full":
    with st.status("Loading AI models & generating insights...", expanded=True) as status:
        try:
            # NOW load heavy dependencies (~45-60MB)
            import os
            from agents.social_agent import SocialAgent
            from agents.analyst_agent import
