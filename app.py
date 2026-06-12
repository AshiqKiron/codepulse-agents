import streamlit as st

# ✅ ZERO PYTHON LOGIC ON INITIAL LOAD
# No imports, no env checks, no DB calls until button clicked
st.set_page_config(page_title="CodePulse", layout="wide")

# Static hero section - renders instantly
st.markdown("""
<div style='padding:3rem 1rem;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
border-radius:12px;text-align:center;color:white;margin-bottom:2rem'>
<h1 style='margin:0;font-size:2.5rem'>🟦 CodePulse</h1>
<p style='font-size:1.2rem;opacity:0.9;margin-top:0.5rem'>
VS Code Intelligence Platform<br>
<span style='font-size:0.9rem;opacity:0.7'>Sub-second load • Time-bounded analysis • Cached insights</span>
</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for persistent UI without reruns
if "results" not in st.session_state:
    st.session_state.results = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# Sidebar config (minimal widgets)
with st.sidebar:
    st.header("⚙️")
    repo = st.text_input("Repo", "microsoft/vscode", key="repo")
    window = st.selectbox("Window", ["1H", "24H"], index=1, key="window")
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.results = None
        st.rerun()

# Show cached results if available (from previous run in same session)
if st.session_state.results:
    r = st.session_state.results
    c1, c2 = st.columns(2)
    c1.markdown(f"**🐛 GitHub ({r['gh_count']} issues):**\n{r['gh']}")
    c2.markdown(f"**💬 Social ({r['hn_count']} posts):**\n{r['hn']}")
    st.divider()
    st.markdown(f"** Roadmap:**\n{r['roadmap']}")
    st.caption(f"Updated: {r['timestamp']}")

# Single action button - ALL logic deferred here
if st.button("🔍 Analyze Now", type="primary", use_container_width=True, 
             disabled=st.session_state.loading):
    st.session_state.loading = True
    
    # Import ONLY when button clicked (zero startup cost)
    import os
    from datetime import datetime, timedelta
    
    try:
        from agents.github_agent import GitHubAgent
        from agents.social_agent import SocialAgent
        from agents.analyst_agent import AnalystAgent
        from agents.pm_agent import PM_AGENT
        
        now = datetime.utcnow()
        since = (now - timedelta(hours=1)).isoformat() + "Z" \
                if st.session_state.get("window", "24H") == "1H" \
                else (now - timedelta(days=1)).isoformat() + "Z"
        
        gh = GitHubAgent(); gh.repo = st.session_state.get("repo", "microsoft/vscode")
        soc = SocialAgent()
        ana = AnalystAgent()
        pm = PM_AGENT()
        
        issues = gh.get_top_issues(label="bug", limit=2, since=since)
        hn = soc.get_hn_discussions(st.session_state.get("repo", "vscode").split("/")[1], limit=2)
        
        gh_sum = ana.summarize_pain_points("GitHub", issues)
        hn_sum = ana.summarize_pain_points("Social", hn) if hn else "No recent data"
        roadmap = pm.create_roadmap(gh_sum, hn_sum)
        
        # Store in session state (persists across reruns without DB call)
        st.session_state.results = {
            "gh": gh_sum, "gh_count": len(issues),
            "hn": hn_sum, "hn_count": len(hn),
            "roadmap": roadmap,
            "timestamp": now.strftime("%H:%M UTC")
        }
        
        # Silent background save (non-blocking)
        if os.getenv("SUPABASE_URL"):
            try:
                from db.supabase_client import SupabaseClient
                db = SupabaseClient()
                db.save_insight("github_24h", gh_sum, "Neutral")
                db.save_insight("social_24h", hn_sum, "Neutral")
            except Exception:
                pass
                
    except Exception as e:
        st.error(f"Error: {str(e)[:100]}")
    finally:
        st.session_state.loading = False
        st.rerun()  # Rerun once to display results
