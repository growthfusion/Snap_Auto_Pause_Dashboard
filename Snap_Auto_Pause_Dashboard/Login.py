import streamlit as st
from supabase import create_client, Client

# Supabase setup
SUPABASE_URL = "https://mhxrmrvruifwcdxrlvpy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1oeHJtcnZydWlmd2NkeHJsdnB5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0NTUxMjEsImV4cCI6MjA3MjAzMTEyMX0.HwIcEWHgTRh7lAvp9q881K_6_H0-vVAT-TprbXlUtNo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Session State for Login ---
if "user" not in st.session_state:
    st.session_state.user = None
if "jwt" not in st.session_state:
    st.session_state.jwt = None

def login(email, password):
    try:
        # Supabase Auth with JWT
        result = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return result
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.jwt = None

# --- UI ---
st.title("Dashboard Login")

if not st.session_state.user:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)
        if user and user.user:
            st.session_state.user = user
            st.session_state.jwt = user.session.access_token  # Save JWT token
            st.success("✅ Logged in successfully!")

            st.switch_page("pages/Dashboard.py")
else:
    st.success(f"Welcome {st.session_state.user.user.email}")

    if st.button("Logout"):
        logout()
        st.rerun()

