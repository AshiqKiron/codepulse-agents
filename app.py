import streamlit as st

# ✅ ZERO MEMORY STATE
st.set_page_config(page_title="CodePulse", layout="wide")

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "zero"
if "preview_data" not in st.session_state:
    st.session_state.preview_data = None
if "full_results" not in st.session_state:
    st.session_state.full_results = None

# --- SIDEBAR (Minimal) ---
with st.sidebar:
    st.header("⚙️ Config")
    if st.session_state.stage == "zero":
        st.caption("Configure settings below")
    
    repo = st.text_input("Repo", "microsoft/vscode", key="repo")
    window = st.selectbox("Window", ["1H", "24H"], index=1, key="window")
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.stage = "zero"
        st.session_state.preview_data = None
        st.session_state.full_results = None
        st.rerun()

# --- MAIN CONTENT ---
# Force button visibility by placing it INSIDE the hero container
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

# STAGE-BASED RENDERING
if st.session_state.stage == "zero":
    # Button is NOW inside a visible container with clear spacing
    st.markdown("<div style='text-align:center;margin:2rem 0;'>", unsafe_allow_html=True)
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        st.session_state.stage = "preview"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add spacer to prevent content from hiding behind footer
    st.markdown("<br><br><br>", unsafe_allow_html=True)

elif st.session_state.stage == "preview":
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
    
    if st.button("🧠 Generate AI Insights", type="primary", use_container_width=True):
        st.session_state.stage = "loading_full"
        st.rerun()

elif st.session_state.stage == "loading_full":
    with st.status("Loading AI models & generating insights...", expanded=True) as status:
        try:
            import os
            from agents.social_agent import SocialAgent
            from agents.analyst_agent import AnalystAgent
            from agents.pm_agent import PM_AGENT
            
            status.write("Initializing LLM...")
            soc = SocialAgent()
            ana = AnalystAgent()
            pm = PM_AGENT()
            
            hn = soc.get_hn_discussions(
                st.session_state.get("repo", "vscode").split("/")[1], 
                limit=2
            )
            
            status.write("Analyzing pain points...")
            gh_sum = ana.summarize_pain_points("GitHub", d["issues"])
            hn_sum = ana.summarize_pain_points("Social", hn) if hn else "No recent discussions"
            
            status.write("Generating roadmap...")
            roadmap = pm.create_roadmap(gh_sum, hn_sum)
            
            st.session_state.full_results = {
                "gh": gh_sum, "hn": hn_sum, 
                "roadmap": roadmap,
                "hn_count": len(hn)
            }
            st.session_state.stage = "full"
            
            if os.getenv("SUPABASE_URL"):
                try:
                    from db.supabase_client import SupabaseClient
                    db = SupabaseClient()
                    db.save_insight("github_24h", gh_sum, "Neutral")
                    db.save_insight("social_24h", hn_sum, "Neutral")
                except Exception:
                    pass
                    
            st.rerun()
        except Exception as e:
            st.error(f"AI analysis failed: {str(e)[:100]}")
            st.session_state.stage = "preview_ready"
            st.rerun()

elif st.session_state.stage == "full":
    r = st.session_state.full_results
    d = st.session_state.preview_data
    
    c1, c2 = st.columns(2)
    c1.markdown(f"**🐛 GitHub ({d['count']} issues):**\n{r['gh']}")
    c2.markdown(f"**💬 Social ({r['hn_count']} posts):**\n{r['hn']}")
    st.divider()
    st.markdown(f"**🎯 Roadmap:**\n{r['roadmap']}")
    st.caption(f"Updated: {d['timestamp']}")
    
    if st.button("🔄 New Analysis", use_container_width=True):
        st.session_state.stage = "zero"
        st.session_state.preview_data = None
        st.session_state.full_results = None
        st.rerun()
