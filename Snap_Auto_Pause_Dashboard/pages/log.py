import streamlit as st

# ----------------------
# Streamlit Dashboard
# ----------------------
if "user" not in st.session_state or st.session_state.user is None:
    st.error("❌ Please login first from the Login page.")
    st.stop()