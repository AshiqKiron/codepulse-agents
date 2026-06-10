import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="CodePulse: VS Code Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for perceived performance
st.markdown("""
<style>
    .stSpinner > div { min-height: 2rem !important; }
    section[data-testid="stSidebar"] { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("🟦 CodePulse: Multi-Agent VS Code Intelligence")
st.caption("Real-time pain point analysis | GitHub + HN + Reddit | Mistral-7B")

# --- LAZY AGENT INITIALIZATION (Critical for Speed) ---
@st.cache_resource(show_spinner=False)
def init_agents():
    """Imports happen ONLY here, not at module level"""
    from agents.github_agent import GitHubAgent
    from agents.social_agent import SocialAgent
    from agents.analyst_agent import AnalystAgent
    from agents.pm_agent import PM_AGENT
    
    return {
        "github": GitHubAgent(),
        "social": SocialAgent(),
        "analyst": AnalystAgent(),
        "pm": PM_AGENT()
    }

agents = init_agents()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    repo_name = st.text_input("GitHub Repo", "microsoft/vscode")
    search_term = st.text_input("Social Search Term", "VS Code")
    
    st.divider()
    if st.button("🔄 Clear Cache & Reload", type="secondary"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# --- MAIN TABS ---
tab_live, tab_history = st.tabs(["🚀 Live Analysis", " Historical Trends"])

# === TAB 1: LIVE ANALYSIS WITH PROGRESSIVE DISCLOSURE ===
with tab_live:
    if st.button("Run Live Analysis", type="primary", use_container_width=True):
        # Progressive status container
        with st.status("Gathering intelligence...", expanded=True) as status:
            try:
                agents["github"].repo = repo_name
                
                # Step 1: GitHub
                status.write("🔍 Fetching GitHub issues...")
                gh_issues = agents["github"].get_top_issues(label="bug", limit=5)
                
                # Step 2: Social
                status.write("💬 Scanning Hacker News & Reddit...")
                hn_posts = agents["social"].get_hn_discussions(search_term)
                reddit_posts = agents["social"].get_reddit_posts("vscode", limit=5)
                
                # Step 3: Analysis
                status.write("🧠 Analyzing pain points with AI...")
                gh_summary = agents["analyst"].summarize_pain_points("GitHub Issues", gh_issues)
                social_items = hn_posts + reddit_posts
                social_summary = agents["analyst"].summarize_pain_points(
                    "Social Discussions", social_items
                ) if social_items else "No social data found."
                
                # Step 4: Roadmap
                status.write(" Generating strategic roadmap...")
                roadmap = agents["pm"].create_roadmap(gh_summary, social_summary)
                
                status.update(label="Analysis complete!", state="complete")
                
                # Display Results
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🐛 Top GitHub Bugs")
                    for issue in gh_issues:
                        st.markdown(f"**{issue['title']}** ({issue['comments']} comments)")
                        st.caption(issue['url'])
                    st.info(f"**Themes:**\n{gh_summary}")
                
                with col2:
                    st.subheader("💬 Social Buzz")
                    for post in hn_posts[:3]:
                        st.markdown(f"**HN:** {post['title']} (🔥 {post['points']})")
                    for post in reddit_posts[:3]:
                        st.markdown(f"**Reddit:** {post['title']} (⬆️ {post['score']})")
                    st.info(f"**Sentiment:**\n{social_summary}")
                
                st.divider()
                st.subheader(" Strategic Roadmap")
                st.markdown(roadmap)
                
                # Non-blocking DB save
                if os.getenv("SUPABASE_URL"):
                    try:
                        from db.supabase_client import SupabaseClient
                        db = SupabaseClient()
                        db.save_insight("github_live", gh_summary, "Neutral")
                        db.save_insight("social_live", social_summary, "Neutral")
                        st.toast("✅ Saved to database", icon="✅")
                    except Exception:
                        pass
                        
            except Exception as e:
                status.update(label=f"Failed: {str(e)[:80]}", state="error")
                st.error(str(e))

# === TAB 2: HISTORICAL TRENDS (Instant Load
