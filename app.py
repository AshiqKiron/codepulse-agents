import streamlit as st
import os
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

st.set_page_config(page_title="CodePulse", layout="wide")
st.title("🟦 CodePulse: VS Code Intelligence")

# --- ZERO-API INITIAL LOAD ---
# Only loads if user explicitly requests history; default tab is empty/instant
@st.cache_data(ttl=3600)
def get_cached_summary():
    if not os.getenv("SUPABASE_URL"):
        return None
    try:
        from db.supabase_client import SupabaseClient
        db = SupabaseClient()
        gh = db.get_recent_insights(limit=1, source="github_24h")
        social = db.get_recent_insights(limit=1, source="social_24h")
        return {"gh": gh[0]["content"] if gh else None, 
                "social": social[0]["content"] if social else None,
                "updated": gh[0]["created_at"][:10] if gh else None}
    except Exception:
        return None

cached = get_cached_summary()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Config")
    time_window = st.selectbox("Time Window", ["Last 1 Hour", "Last 24 Hours"], index=1)
    repo_name = st.text_input("Repo", "microsoft/vscode")
    
    if st.button("Clear Cache"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# --- INSTANT DEFAULT VIEW ---
st.markdown("""
<div style='padding:2rem;background:#f0f2f6;border-radius:8px;text-align:center'>
<h3> Ready for Live Analysis</h3>
<p>Click below to analyze VS Code pain points from the selected time window.<br>
Results appear in <strong>&lt;5 seconds</strong>.</p>
</div>
""", unsafe_allow_html=True)

if cached and cached["gh"]:
    st.info(f"📅 Last 24h summary available (Updated: {cached['updated']})")
    c1, c2 = st.columns(2)
    c1.markdown(f"**GitHub:**\n{cached['gh']}")
    c2.markdown(f"**Social:**\n{cached['social']}")

# --- ULTRA-LEAN LIVE ANALYSIS ---
if st.button("🔍 Analyze Now", type="primary", use_container_width=True):
    with st.status("Analyzing...", expanded=False) as status:
        try:
            # Lazy imports - zero overhead until button click
            from agents.github_agent import GitHubAgent
            from agents.social_agent import SocialAgent
            from agents.analyst_agent import AnalystAgent
            from agents.pm_agent import PM_AGENT
            
            # Calculate time filter
            now = datetime.utcnow()
            since = (now - timedelta(hours=1)).isoformat() + "Z" if time_window == "Last 1 Hour" \
                    else (now - timedelta(days=1)).isoformat() + "Z"
            
            gh = GitHubAgent(); gh.repo = repo_name
            soc = SocialAgent()
            ana = AnalystAgent()
            pm = PM_AGENT()
            
            # MINIMAL DATA POINTS (2 each)
            status.write("Fetching recent issues...")
            issues = gh.get_top_issues(label="bug", limit=2, since=since)
            
            status.write("Scanning HN...")
            hn = soc.get_hn_discussions(repo_name.split("/")[1], limit=2)
            
            status.write("Generating insights...")
            gh_sum = ana.summarize_pain_points("GitHub", issues)
            soc_sum = ana.summarize_pain_points("Social", hn) if hn else "No recent discussions"
            
            roadmap = pm.create_roadmap(gh_sum, soc_sum)
            
            status.update(label="Done!", state="complete")
            
            # Compact display
            c1, c2 = st.columns(2)
            c1.markdown(f"**🐛 Issues ({len(issues)}):**\n{gh_sum}")
            c2.markdown(f"**💬 Social ({len(hn)}):**\n{soc_sum}")
            st.divider()
            st.markdown(f"** Roadmap:**\n{roadmap}")
            
            # Silent save for next instant load
            if os.getenv("SUPABASE_URL"):
                try:
                    from db.supabase_client import SupabaseClient
                    db = SupabaseClient()
                    db.save_insight("github_24h", gh_sum, "Neutral")
                    db.save_insight("social_24h", soc_sum, "Neutral")
                except Exception:
                    pass
                    
        except Exception as e:
            st.error(f"Error: {str(e)[:100]}")
