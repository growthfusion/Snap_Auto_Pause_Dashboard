from supabase import create_client
import streamlit as st
import pandas as pd

SUPABASE_URL = "https://mhxrmrvruifwcdxrlvpy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1oeHJtcnZydWlmd2NkeHJsdnB5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjQ1NTEyMSwiZXhwIjoyMDcyMDMxMTIxfQ.bfQ44c2J6zwAEChRVO_zhh6xcgvm8r7BSkFZOACykZo"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Check login ---
if "user" not in st.session_state or st.session_state.user is None:
    st.error("❌ Please login first from the Login page.")
    st.stop()

# --- Function to log actions ---
def log_action(user_id: str, action: str, details: dict = None, email: str = None):
    """Store a user action in Supabase logs table"""
    if details is None:
        details = {}

    # ✅ always extract email from session user object
    if email is None:
        try:
            email = st.session_state.user.email   # correct way
        except Exception:
            email = None

    try:
        supabase.table("logs").insert({
            "user_id": user_id,
            "email": email,
            "action": action,
            "details": details
        }).execute()
    except Exception as e:
        st.error(f"⚠️ Failed to log action: {e}")

# --- UI: Display Logs ---
st.title("📜 User Activity Logs")

try:
    logs_response = (
        supabase.table("logs")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    logs = logs_response.data if logs_response.data else []

    if logs:
        df = pd.DataFrame(logs)
        # remove login/logout noise
        df = df[~df["action"].isin(["login", "logout"])]
        # show only selected columns
        if "email" in df.columns:
            df = df[["email", "action", "details", "created_at"]]

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No logs found yet.")
except Exception as e:
    st.error(f"⚠️ Failed to fetch logs: {e}")

