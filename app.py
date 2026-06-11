import streamlit as st
import os

# Safe env loading
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

st.set_page_config(page_title="CodePulse", layout="wide")
st.title("🟦 CodePulse: VS Code Intelligence")

# --- INSTANT HISTORICAL DATA LOAD ---
@st.cache_data(ttl=1800)
def load_historical_insights():
    if not os.getenv("SUPABASE_URL"):
        return None
    try:
        from db.supabase_client import SupabaseClient
        db = SupabaseClient()
        gh = db.get_recent_insights(limit=1, source="github_weekly")
        social = db.get_recent_insights(limit=1, source="social_weekly")
        trends = db.get_sentiment_trends(days=30)
        return {"gh": gh, "social": social, "trends": trends}
    except Exception:
        return None

historical = load_historical_insights()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Config")
    repo_name = st.text_input("Repo", "microsoft/vscode")
    search_term = st.text_input("Search", "VS Code")
    
    if st.button("Clear All Cache"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# --- TABS FOR LAZY LOADING ---
tab_cached, tab_live = st.tabs(["📊 Latest Insights (Instant)", "🚀 Run Live Analysis"])

# TAB 1: INSTANT CACHED VIEW
with tab_cached:
    if historical and historical["gh"] and historical["social"]:
        st.success(f" Last updated: {historical['gh'][0]['created_at'][:10]}")
        c1, c2 = st.columns(2)
        c1.markdown(f"**GitHub Themes:**\n{historical['gh'][0]['content']}")
        c2.markdown(f"**Social Sentiment:**\n{historical['social'][0]['content']}")
        
        if sum(historical["trends"].values()) > 0:
            import plotly.express as px
            import pandas as pd
            df = pd.DataFrame([historical["trends"]]).melt(var_name="Sentiment", value_name="Count")
            fig = px.bar(df, x="Sentiment", y="Count", color="Sentiment",
                        title="30-Day Trend", height=300,
                        color_discrete_map={"Positive":"#2ecc71","Negative":"#e74c3c","Neutral":"#95a5a6"})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data yet. Click 'Run Live Analysis' to generate first report.")

# TAB 2: LIVE ANALYSIS (Lazy Init)
with tab_live:
    if st.button("🔍 Analyze Now", type="primary", use_container_width=True):
        with st.status("Processing...", expanded=False) as status:
            try:
                # Lazy imports - only run when button clicked
                from agents.github_agent import GitHubAgent
                from agents.social_agent import SocialAgent
                from agents.analyst_agent import AnalystAgent
                from agents.pm_agent import PM_AGENT
                
                gh = GitHubAgent(); gh.repo = repo_name
                soc = SocialAgent()
                ana = AnalystAgent()
                pm = PM_AGENT()
                
                status.write("Fetching top 3 issues...")
                issues = gh.get_top_issues(label="bug", limit=3)
                
                status.write("Scanning Hacker News...")
                hn = soc.get_hn_discussions(search_term)
                
                status.write("Generating insights...")
                gh_sum = ana.summarize_pain_points("GitHub", issues)
                soc_sum = ana.summarize_pain_points("Social", hn) if hn else "No data"
                
                roadmap = pm.create_roadmap(gh_sum, soc_sum)
                
                status.update(label="Complete!", state="complete")
                
                c1, c2 = st.columns(2)
                c1.markdown(f"**Issues:**\n{gh_sum}")
                c2.markdown(f"**Sentiment:**\n{soc_sum}")
                st.divider()
                st.markdown(roadmap)
                
                # Silent DB save
                if os.getenv("SUPABASE_URL"):
                    try:
                        from db.supabase_client import SupabaseClient
                        db = SupabaseClient()
                        db.save_insight("github_live", gh_sum, "Neutral")
                        db.save_insight("social_live", soc_sum, "Neutral")
                    except Exception:
                        pass
                        
            except Exception as e:
                st.error(f"Error: {str(e)[:100]}")
