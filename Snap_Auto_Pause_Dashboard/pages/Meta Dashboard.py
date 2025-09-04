import streamlit as st
import requests
from pages.log import log_action

API_BASE_URL = "https://gfcomp.pro"

# Redirect if not logged in
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("Login.py")

st.set_page_config(page_title="Meta Campaign Control", layout="wide")
st.title("Meta Auto Pause Dashboard")

# --- Initialize session ---
if "meta_config_fetched" not in st.session_state or not st.session_state.meta_config_fetched:
    try:
        resp = requests.get(f"{API_BASE_URL}/config?platform=meta")
        if resp.status_code == 200:
            meta_config = resp.json()
            st.session_state["auto_pause"] = meta_config.get("active", False)
            st.session_state["global_profit_loss"] = meta_config.get("alert_profit_threshold", 0)
            campaigns = meta_config.get("campaign_loss_thresholds", {})
            st.session_state["campaign_conditions"] = [
                {"id": k, "value": v} for k, v in campaigns.items()
            ]
            st.session_state["config_fetched"] = True
    except Exception as e:
        st.error(f"❌ Request failed: {e}")

# --------------------------------
# Section 1: Snap Auto Pause
# --------------------------------
st.subheader("⚡ Meta Auto Pause")
auto_pause_toggle = st.toggle("Enable Auto Pause", value=st.session_state["auto_pause"])
if st.button("Apply Auto Pause"):
    try:
        payload = {"active": auto_pause_toggle}
        resp = requests.post(f"{API_BASE_URL}/config?platform=meta", json=payload)
        if resp.status_code == 200:
            st.success(f"✅ Auto Pause set to {auto_pause_toggle}")
            st.session_state["auto_pause"] = auto_pause_toggle
            # Log event
            log_action(
                st.session_state.user.user.id,
                "Meta_toggle_auto_pause",
                {"Meta_toggle_value": auto_pause_toggle}
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
profit_loss_value = st.number_input(
    "Set Profit/Loss Value",
    value=st.session_state["global_profit_loss"],
    step=1,
    format="%d"
)
if st.button("Submit"):
    try:
        payload = {"active": True, "alert_profit_threshold": -abs(profit_loss_value)}
        resp = requests.post(f"{API_BASE_URL}/config?platform=meta", json=payload)
        if resp.status_code == 200:
            st.session_state["meta_global_profit_loss"] = -abs(profit_loss_value)
            st.success(f"✅ Updated Active Campaign Profit Value to {-abs(profit_loss_value)}")
            # Log event
            log_action(
                st.session_state.user.user.id,
                "Meta_update_global_threshold",
                {"Meta_Overall_value": -abs(profit_loss_value)}
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
            payload = {"campaign": campaign_id, "threshold": -abs(camp_value)}
            resp = requests.post(f"{API_BASE_URL}/config/campaigns?platform=meta", json=payload)
            if resp.status_code == 200:
                updated_config = resp.json()
                st.session_state["campaign_conditions"] = [
                    {"id": k, "value": v} for k, v in updated_config.get("campaign_loss_thresholds", {}).items()
                ]
                st.success(f"✅ Campaign `{campaign_id}` added with value {-abs(camp_value)}")
                # Log event
                log_action(
                    st.session_state.user.user.id,
                    "Meta_add_campaign",
                    {"Meta_campaign": campaign_id, "value": -abs(camp_value)}
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
                try:
                    payload = {"campaign": camp["id"]}
                    resp = requests.delete(f"{API_BASE_URL}/config/campaigns?platform=meta", json=payload)
                    if resp.status_code == 200:
                        updated_config = resp.json()
                        st.session_state["meta_campaign_conditions"] = [
                            {"id": k, "value": v} for k, v in updated_config.get("campaign_loss_thresholds", {}).items()
                        ]
                        st.success(f"🗑️ Deleted `{camp['id']}`")
                        # Log event
                        log_action(
                            st.session_state.user.user.id,
                            "Meta_delete_campaign",
                            {"Meta_"
                             ""
                             "8campaign": camp["id"]}
                        )
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
                st.rerun()
