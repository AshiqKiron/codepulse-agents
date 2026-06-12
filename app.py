import streamlit as st

# ✅ REMOVE set_page_config - causes mandatory rerun
# Use default config; title appears in browser tab via HTML below

# Pure static HTML - NO Streamlit widgets, NO Python logic
st.markdown("""
<!DOCTYPE html>
<html>
<head>
    <title>CodePulse</title>
    <style>
        body { margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }
        .hero { 
            padding:4rem 2rem; 
            background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            border-radius:16px; text-align:center; color:white; 
            margin:2rem auto; max-width:800px;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
        h1 { margin:0; font-size:3rem; font-weight:700; }
        p { font-size:1.3rem; opacity:0.95; margin-top:1rem; }
        .badge { display:inline-block; background:rgba(255,255,255,0.2); 
                 padding:0.3rem 0.8rem; border-radius:20px; font-size:0.9rem; margin-top:1.5rem; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🟦 CodePulse</h1>
        <p>VS Code Intelligence Platform</p>
        <span class="badge"> Progressive Loading • Zero Cold-Start Overhead</span>
    </div>
</body>
</html>
""", unsafe_allow_html=True)

# ONLY NOW add interactive elements (after static content renders)
if "stage" not in st.session_state:
    st.session_state.stage = "zero"

# Minimal sidebar - NO widgets until needed
with st.sidebar:
    if st.session_state.stage == "zero":
        st.markdown("### ️ Configuration")
        st.caption("Settings appear after first click")
    else:
        repo = st.text_input("Repo", "microsoft/vscode", key="repo")
        window = st.selectbox("Window", ["1H", "24H"], index=1, key="window")
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.stage = "zero"
            st.rerun()

# Single button - no other interactive elements in zero state
if st.session_state.stage == "zero":
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        st.session_state.stage = "preview"
        st.rerun()
else:
    # Rest of your progressive loading logic remains unchanged
    # [Insert preview → full analysis stages here]
    pass
