import streamlit as st
import os
from dotenv import load_dotenv
from agents.github_agent import GitHubAgent
from agents.social_agent import SocialAgent
from agents.analyst_agent import AnalystAgent
from agents.pm_agent import PM_AGENT

load_dotenv()

st.set_page_config(page_title="CodePulse: VS Code Intelligence", layout="wide")
st.title("🟦 CodePulse: Multi-Agent VS Code Intelligence")

st.markdown("""
This system uses live data from GitHub, Hacker News, and Reddit to analyze 
user pain points and generate product strategies for Visual Studio Code.
""")

if st.button("🚀 Run Live Analysis"):
    with st.spinner("Agents are collaborating..."):
        # 1. Initialize
        gh = GitHubAgent()
        social = SocialAgent()
        analyst = AnalystAgent()
        pm = PM_AGENT()

        # 2. Fetch Data
        gh_issues = gh.get_top_issues(label="bug", limit=5)
        hn_posts = social.get_hn_discussions("VS Code")
        reddit_posts = social.get_reddit_posts("vscode", limit=5)

        # 3. Analyze
        gh_summary = analyst.summarize_pain_points("GitHub Issues", gh_issues)
        social_summary = analyst.summarize_pain_points("Social Discussions", hn_posts + reddit_posts)

        # 4. Strategize
        roadmap = pm.create_roadmap(gh_summary, social_summary)

        # 5. Display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🐛 Top GitHub Bugs")
            for issue in gh_issues:
                st.markdown(f"**{issue['title']}** ({issue['comments']} comments)")
            st.info(f"**Key Themes:**\n{gh_summary}")

        with col2:
            st.subheader("💬 Social Buzz")
            for post in hn_posts[:3]:
                st.markdown(f"**HN:** {post['title']} (🔥 {post['points']})")
            for post in reddit_posts[:3]:
                st.markdown(f"**Reddit:** {post['title']} (⬆️ {post['score']})")
            st.info(f"**Key Themes:**\n{social_summary}")

        st.divider()
        st.subheader("🎯 Strategic Roadmap Recommendation")
        st.markdown(roadmap)
