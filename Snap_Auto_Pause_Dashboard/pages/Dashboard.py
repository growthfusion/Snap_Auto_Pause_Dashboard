import streamlit as st
import requests


# ----------------------
# Config File Path
# ----------------------
API_BASE_URL = "https://gfcomp.pro"

# ----------------------
# Streamlit Dashboard
# ----------------------
if "user" not in st.session_state or st.session_state.user is None:
    st.error("❌ Please login first from the Login page.")
    st.stop()

st.set_page_config(page_title="Snap Campaign Control", layout="wide")
st.title("Snap Auto Pause Dashboard")

# ----------------------
# 🔹 Highlighted: Fetch latest config on page load
# ----------------------
if "config_fetched" not in st.session_state or not st.session_state.config_fetched:
    try:
        resp = requests.get(f"{API_BASE_URL}/config")
        if resp.status_code == 200:
            config = resp.json()
            st.session_state["auto_pause"] = config.get("active", False)
            st.session_state["global_profit_loss"] = config.get("alert_profit_threshold", 0)
            campaigns = config.get("campaign_loss_thresholds", {})
            st.session_state["campaign_conditions"] = [
                {"id": k, "value": v} for k, v in campaigns.items()
            ]
            st.session_state["config_fetched"] = True
        else:
            st.error(f"❌ Failed to fetch config: {resp.text}")
    except Exception as e:
        st.error(f"❌ Request failed: {e}")

# Initialize session state
if "auto_pause" not in st.session_state:
    st.session_state["auto_pause"] = False
if "global_profit_loss" not in st.session_state:
    st.session_state["global_profit_loss"] = 0
if "campaign_conditions" not in st.session_state:
    st.session_state["campaign_conditions"] = []


# ---------------------------
# Section 1: Snap Auto Pause
# ---------------------------
st.subheader("⚡ Snap Auto Pause")

auto_pause_toggle = st.toggle(
    "Enable Auto Pause",
    value=st.session_state["auto_pause"],
    key="auto_pause_toggle"
)

if st.button("Apply Auto Pause"):
    st.session_state["auto_pause"] = auto_pause_toggle
    # Save auto_pause immediately to server
    try:
        payload = {"active": auto_pause_toggle}
        resp = requests.post(f"{API_BASE_URL}/config", json=payload)
        if resp.status_code == 200:
            st.success(f"✅ Auto Pause set to {auto_pause_toggle}")
        else:
            st.error(f"❌ API Error: {resp.text}")
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
    st.rerun()

# ---------------------------
# Section 2: Global Profit/Loss Value
# ---------------------------
st.subheader("Active Campaign Profit Value")

profit_loss_value = st.number_input(
    "Set Profit/Loss Value",
    value=st.session_state["global_profit_loss"],
    step=1,             # integer step
    format="%d"         # force display as integer
)

if st.button("Submit"):
    st.session_state["global_profit_loss"] = profit_loss_value

    # ---- API call for global profit/loss ----
    payload = {
        "active": True,
        "alert_profit_threshold": -abs(profit_loss_value)
    }
    try:
        resp = requests.post(f"{API_BASE_URL}/config", json=payload)
        if resp.status_code == 200:
            # Always fetch what the server actually stored
            resp_check = requests.get(f"{API_BASE_URL}/config")
            if resp.status_code == 200:
            # 🔹 Refresh latest value from server
                resp_check = requests.get(f"{API_BASE_URL}/config")
                if resp_check.status_code == 200:
                    config = resp_check.json()
                    server_value = config.get("alert_profit_threshold")
                    st.session_state["global_profit_loss"] = server_value
                    st.success(f"✅ Server updated. Current Profit/Loss Threshold = {server_value}")
                else:
                    st.error(f"❌ Failed to fetch updated config: {resp_check.text}")
            else:
                st.error(f"❌ API Error: {resp.text}")
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
    st.rerun()

# ---------------------------
# Section 3: Add new campaign condition
# ---------------------------
st.subheader("➕ Add New Individual Campaign Condition")

campaign_id = st.text_input("Enter Campaign Name")
camp_value = st.number_input(
    "Set Profit/Loss Value",
    value=0,
    step=1,
    format="%d",        # integer format
    key="new_campaign_value"
)

if st.button("Add Campaign Condition"):
    if campaign_id.strip() == "":
        st.warning("⚠️ Please enter a campaign name.")
    else:
        try:
            # 1️⃣ Fetch current config
            resp_check = requests.get(f"{API_BASE_URL}/config")
            if resp_check.status_code == 200:
                config = resp_check.json()
                campaigns = config.get("campaign_loss_thresholds", {})
                # 2️⃣ Merge/update new campaign
                campaigns[campaign_id] = -abs(camp_value)
                payload = {"campaign_loss_thresholds": campaigns}
                # 3️⃣ Post updated campaigns back
                resp = requests.post(f"{API_BASE_URL}/config", json=payload)
                if resp.status_code == 200:
                    st.success(f"✅ Campaign `{campaign_id}` added/updated with value {-abs(camp_value)}")
                    # 🔹 Update local session state
                    st.session_state["campaign_conditions"] = [
                        {"id": k, "value": v} for k, v in campaigns.items()
                    ]
                else:
                    st.error(f"❌ API Error: {resp.text}")
            else:
                st.error(f"❌ Failed to fetch current config: {resp_check.text}")
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
    st.rerun()

st.markdown("---")

# ---------------------------
# Section 4: List existing campaign conditions
# ---------------------------
st.subheader("📋 Individual Campaign Conditions")

if len(st.session_state["campaign_conditions"]) == 0:
    st.info("No campaign conditions added yet.")
else:
    for idx, camp in enumerate(st.session_state["campaign_conditions"]):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{camp['id']}**")
        with col2:
            st.write(f"Profit/Loss: `{camp['value']}`")
        with col3:
            if st.button(f"❌ Delete", key=f"delete_{idx}"):
                removed = st.session_state["campaign_conditions"].pop(idx)
                try:
                    # 1️⃣ Fetch current config
                    resp_check = requests.get(f"{API_BASE_URL}/config")
                    if resp_check.status_code == 200:
                        config = resp_check.json()
                        campaigns = config.get("campaign_loss_thresholds", {})
                        # 2️⃣ Remove selected campaign
                        if removed["id"] in campaigns:
                            campaigns.pop(removed["id"])
                        # 3️⃣ Post updated campaigns back
                        payload = {"campaign_loss_thresholds": campaigns}
                        resp = requests.post(f"{API_BASE_URL}/config", json=payload)
                        if resp.status_code == 200:
                            st.success(f"🗑️ Deleted `{removed['id']}`")
                            # 🔹 Update session state
                            st.session_state["campaign_conditions"] = [
                                {"id": k, "value": v} for k, v in campaigns.items()
                            ]
                        else:
                            st.error(f"❌ API Error: {resp.text}")
                    else:
                        st.error(f"❌ Failed to fetch current config: {resp_check.text}")
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
                st.rerun()  # 🔹 Refresh automatically
