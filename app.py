import streamlit as st
import os

# Safe env loading for local + cloud
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

st.set_page_config(page_title="CodePulse", layout="wide")
st.title("🟦 CodePulse: VS Code Intelligence")

# --- CACHED AGENT INITIALIZATION ---
@st.cache_resource(show_spinner=False)
def init_agents():
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
    st.header("⚙️ Config")
    repo_name = st.text_input("Repo", "microsoft/vscode")
    search_term = st.text_input("Search Term", "VS Code")
    
    if st.button("🔄 Clear Cache"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# --- MAIN ANALYSIS ---
if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
    with st.status("Analyzing...", expanded=True) as status:
        try:
            agents["github"].repo = repo_name
            
            # LEANER FETCHING: Limit to 3 items for speed
            status.write("🔍 Fetching top 3 GitHub issues...")
            gh_issues = agents["github"].get_top_issues(label="bug", limit=3)
            
            status.write(" Scanning social discussions...")
            hn_posts = agents["social"].get_hn_discussions(search_term)
            reddit_posts = agents["social"].get_reddit_posts("vscode", limit=3)
            
            status.write("🧠 Generating insights...")
            gh_summary = agents["analyst"].summarize_pain_points("GitHub", gh_issues)
            social_items = hn_posts + reddit_posts
            social_summary = agents["analyst"].summarize_pain_points(
                "Social", social_items
            ) if social_items else "No social data."
            
            status.write("️ Creating roadmap...")
            roadmap = agents["pm"].create_roadmap(gh_summary, social_summary)
            
            status.update(label="Done!", state="complete")
            
            # DISPLAY RESULTS
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🐛 Top Issues")
                for i in gh_issues:
                    st.markdown(f"**{i['title']}** ({i['comments']} comments)")
                st.info(f"**Themes:**\n{gh_summary}")
            
            with c2:
                st.subheader("💬 Social Buzz")
                for p in hn_posts[:2]:
                    st.markdown(f"**HN:** {p['title']} (🔥{p['points']})")
                for p in reddit_posts[:2]:
                    st.markdown(f"**Reddit:** {p['title']} (⬆️{p['score']})")
                st.info(f"**Sentiment:**\n{social_summary}")
            
            st.divider()
            st.subheader("🎯 Roadmap")
            st.markdown(roadmap)
            
            # Optional DB Save
            if os.getenv("SUPABASE_URL"):
                try:
                    from db.supabase_client import SupabaseClient
                    db = SupabaseClient()
                    db.save_insight("github_live", gh_summary, "Neutral")
                    st.toast("✅ Saved to DB", icon="✅")
                except Exception:
                    pass
                    
        except Exception as e:
            status.update(label=f"Error: {str(e)[:60]}", state="error")
            st.error(str(e))

st.caption("CodePulse v2.0 | Lean & Fast | Python 3.12")
