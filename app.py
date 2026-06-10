import streamlit as st
import os
from dotenv import load_dotenv

# Load env vars (works locally; on Streamlit Cloud, use Secrets UI)
load_dotenv()

# --- Page Config & Styling ---
st.set_page_config(
    page_title="CodePulse: VS Code Intelligence",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for faster perceived load
st.markdown("""
<style>
    .stSpinner > div { min-height: 2rem !important; }
    section[data-testid="stSidebar"] { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("🟦 CodePulse: Multi-Agent VS Code Intelligence")
st.caption("Real-time pain point analysis powered by Mistral-7B | Data sources: GitHub, HN, Reddit")

# --- Lazy Agent Initialization (Critical for Fast Startup) ---
@st.cache_resource(show_spinner=False)
def init_agents():
    """Only imports and initializes agents ONCE per session."""
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

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    repo_name = st.text_input("GitHub Repo", "microsoft/vscode")
    search_term = st.text_input("Social Search Term", "VS Code")
    
    st.divider()
    st.subheader("📊 Historical Data")
    show_history = st.checkbox("Show last saved analysis", value=True)
    
    if st.button("🔄 Force Refresh Cache", type="secondary"):
        st.cache_resource.clear()
        st.rerun()

# --- Main Content Area ---
# Tab 1: Live Analysis | Tab 2: Historical Trends
tab_live, tab_history = st.tabs([" Live Analysis", "📈 Historical Trends"])

with tab_live:
    if st.button("🚀 Run Live Analysis", type="primary", use_container_width=True):
        with st.spinner("Agents are gathering live data... (30-60s)"):
            try:
                # Update config dynamically
                agents["github"].repo = repo_name
                
                # 1. Fetch Data
                gh_issues = agents["github"].get_top_issues
