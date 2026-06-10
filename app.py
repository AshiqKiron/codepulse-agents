import streamlit as st
import os
from dotenv import load_dotenv
from agents.github_agent import GitHubAgent
from agents.social_agent import SocialAgent
from agents.analyst_agent import AnalystAgent
from agents.pm_agent import PM_AGENT

# Load env vars (works locally; on HF, these come from Secrets)
load_dotenv()

st.set_page_config(page_title="CodePulse: VS Code Intelligence", layout="wide")
st.title("🟦 CodePulse: Multi-Agent VS Code Intelligence")
st.markdown("""
Analyze real-time user pain points for Visual Studio Code using live data from 
GitHub Issues, Hacker News, and Reddit. Powered by Mistral-7B via Hugging Face Inference API.
""")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
repo_name = st.sidebar.text_input("GitHub Repo", "microsoft/vscode")
search_term = st.sidebar.text_input("Social Search Term", "VS Code")
days_back = st.sidebar.slider("Trend Analysis (Days)", 1, 30, 7)

# Initialize Agents
@st.cache_resource
def init_agents():
    return {
        "github": GitHubAgent(),
        "social": SocialAgent(),
        "analyst": AnalystAgent(),
        "pm": PM_AGENT()
    }

agents = init_agents()

# Main Analysis Button
if st.button("🚀 Run Live Analysis", type="primary"):
    with st.spinner("Agents are gathering live data... This may take 30-60 seconds."):
        try:
            # Update repo name dynamically
            agents["github"].repo = repo_name
            
            # 1. Fetch Data
            gh_issues = agents["github"].get_top_issues(label="bug", limit=5)
            hn_posts = agents["social"].get_hn_discussions(search_term)
            reddit_posts = agents["social"].get_reddit_posts("vscode", limit=5)
            
            # 2. Analyze Themes
            gh_summary = agents["analyst"].summarize_pain_points("GitHub Issues", gh_issues)
            social_items = hn_posts + reddit_posts
            social_summary = agents["analyst"].summarize_pain_points("Social Discussions", social_items) if social_items else "No social data found."
            
            # 3. Generate Roadmap
            roadmap = agents["pm"].create_roadmap(gh_summary, social_summary)
            
            # 4. Display Results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(" Top GitHub Bugs")
                if gh_issues:
                    for issue in gh_issues:
                        st.markdown(f"**{issue['title']}** ({issue['comments']} comments)")
                        st.caption(issue['url'])
                    st.info(f"**Key Technical Themes:**\n{gh_summary}")
                else:
                    st.warning("No issues fetched. Check repo name or API limits.")
            
            with col2:
                st.subheader(" Social Buzz")
                if hn_posts:
                    for post in hn_posts[:3]:
                        st.markdown(f"**HN:** {post['title']} (🔥 {post['points']})")
                if reddit_posts:
                    for post in reddit_posts[:3]:
                        st.markdown(f"**Reddit:** {post['title']} (⬆️ {post['score']})")
                if not hn_posts and not reddit_posts:
                    st.warning("No social data found.")
                else:
                    st.info(f"**Key User Sentiment Themes:**\n{social_summary}")
            
            st.divider()
            st.subheader("🎯 Strategic Roadmap Recommendation")
            st.markdown(roadmap)
            
            # Optional: Save to Supabase if configured
            if os.getenv("SUPABASE_URL"):
                from db.supabase_client import SupabaseClient
                try:
                    db = SupabaseClient()
                    db.save_insight("github_summary", gh_summary, "Neutral")
                    db.save_insight("social_summary", social_summary, "Neutral")
                    st.success("✅ Insights saved to Supabase database.")
                except Exception as e:
                    st.warning(f"⚠️ Could not save to DB: {str(e)[:100]}")
                    
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.code(str(e), language="python")

# Footer
st.divider()
st.caption("CodePulse v1.0 | Free Tier Deployment | Data refreshed on each run")
