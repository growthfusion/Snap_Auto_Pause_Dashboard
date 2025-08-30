import streamlit as st
import requests
from pages.log import log_action


API_BASE_URL = "https://gfcomp.pro"

if "user" not in st.session_state or st.session_state.user is None:
    st.error("❌ Please login first from the Login page.")
    st.stop()

st.set_page_config(page_title="Snap Campaign Control", layout="wide")
st.title("Snap Auto Pause Dashboard")

# --- Initialize session ---
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
    except Exception as e:
        st.error(f"❌ Request failed: {e}")

# --------------------------------
# Section 1: Snap Auto Pause
# --------------------------------
st.subheader("⚡ Snap Auto Pause")
auto_pause_toggle = st.toggle("Enable Auto Pause", value=st.session_state["auto_pause"])
if st.button("Apply Auto Pause"):
    try:
        payload = {"active": auto_pause_toggle}
        resp = requests.post(f"{API_BASE_URL}/config", json=payload)
        if resp.status_code == 200:
            st.success(f"✅ Auto Pause set to {auto_pause_toggle}")
            st.session_state["auto_pause"] = auto_pause_toggle

            # 🔹 Log event
            log_action(
                st.session_state.user.user.id,
                "toggle_auto_pause",
                {"new_value": auto_pause_toggle}
            )
        else:
            st.error(f"❌ API Error: {resp.text}")
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
    st.rerun()

# --------------------------------
# Section 2: Global Profit/Loss Value
# --------------------------------
st.subheader("Active Campaign Profit Value")
profit_loss_value = st.number_input("Set Profit/Loss Value",
                                    value=st.session_state["global_profit_loss"],
                                    step=1, format="%d")

if st.button("Submit"):
    try:
        payload = {"active": True, "alert_profit_threshold": -abs(profit_loss_value)}
        resp = requests.post(f"{API_BASE_URL}/config", json=payload)
        if resp.status_code == 200:
            st.session_state["global_profit_loss"] = -abs(profit_loss_value)
            st.success(f"✅ Updated Active Campaign Profit Value to {-abs(profit_loss_value)}")

            # 🔹 Log event
            log_action(
                st.session_state.user.user.id,
                "update_global_threshold",
                {"Overall_value": -abs(profit_loss_value)}
            )
        else:
            st.error(f"❌ API Error: {resp.text}")
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
    st.rerun()

# --------------------------------
# Section 3: Add new campaign condition
# --------------------------------
st.subheader("➕ Add New Individual Campaign Condition")
campaign_id = st.text_input("Enter Campaign Name")
camp_value = st.number_input("Set Profit/Loss Value", value=0, step=1, format="%d")

if st.button("Add Campaign Condition"):
    if campaign_id.strip() == "":
        st.warning("⚠️ Please enter a campaign name.")
    else:
        try:
            resp_check = requests.get(f"{API_BASE_URL}/config")
            if resp_check.status_code == 200:
                config = resp_check.json()
                campaigns = config.get("campaign_loss_thresholds", {})
                campaigns[campaign_id] = -abs(camp_value)
                payload = {"campaign_loss_thresholds": campaigns}
                resp = requests.post(f"{API_BASE_URL}/config", json=payload)
                if resp.status_code == 200:
                    st.success(f"✅ Campaign `{campaign_id}` added with value {-abs(camp_value)}")
                    st.session_state["campaign_conditions"] = [
                        {"id": k, "value": v} for k, v in campaigns.items()
                    ]

                    # 🔹 Log event
                    log_action(
                        st.session_state.user.user.id,
                        "add_campaign",
                        {"campaign": campaign_id, "value": -abs(camp_value)}
                    )
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
    st.rerun()

# --------------------------------
# Section 4: List existing campaigns
# --------------------------------
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
            if st.button(f"❌ Delete {camp['id']}", key=f"delete_{idx}"):
                removed = st.session_state["campaign_conditions"].pop(idx)
                try:
                    resp_check = requests.get(f"{API_BASE_URL}/config")
                    if resp_check.status_code == 200:
                        config = resp_check.json()
                        campaigns = config.get("campaign_loss_thresholds", {})
                        if removed["id"] in campaigns:
                            campaigns.pop(removed["id"])
                        payload = {"campaign_loss_thresholds": campaigns}
                        resp = requests.post(f"{API_BASE_URL}/config", json=payload)
                        if resp.status_code == 200:
                            st.success(f"🗑️ Deleted `{removed['id']}`")
                            st.session_state["campaign_conditions"] = [
                                {"id": k, "value": v} for k, v in campaigns.items()
                            ]

                            # 🔹 Log event
                            log_action(
                                st.session_state.user.user.id,
                                "delete_campaign",
                                {"campaign": removed["id"]}
                            )
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
                st.rerun()
