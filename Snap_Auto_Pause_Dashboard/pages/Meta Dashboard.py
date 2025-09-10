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

            if "snap" in meta_config:
                st.session_state["ad_accounts"] = meta_config["snap"].get("ad_accounts", {})
            else:
                st.session_state["ad_accounts"] = meta_config.get("ad_accounts", {})

            st.session_state["config_fetched"] = True
    except Exception as e:
        st.error(f"❌ Request failed: {e}")


# # --- Section 1: Manage Ad Accounts ---
# st.subheader("📂 Meta Ad Accounts")
#
# # Fetch ad accounts initially if not in session
# if "ad_accounts" not in st.session_state:
#     try:
#         resp = requests.get(f"{API_BASE_URL}/config/adaccounts?platform=meta")
#         if resp.status_code == 200:
#             st.session_state["ad_accounts"] = resp.json().get("ad_accounts", {})
#         else:
#             st.error(f"❌ Failed to fetch ad accounts: {resp.text}")
#             st.session_state["ad_accounts"] = {}
#     except Exception as e:
#         st.error(f"❌ Request failed: {e}")
#         st.session_state["ad_accounts"] = {}
#
# # ---- Add New Ad Account ----
# with st.expander("➕ Add New Ad Account", expanded=False):
#     ad_account_name = st.text_input("Enter Ad Account Name", key="new_ad_name")
#     ad_account_id = st.text_input("Enter Ad Account ID", key="new_ad_id")
#
#     if st.button("Add Ad Account"):
#         if not ad_account_name.strip() or not ad_account_id.strip():
#             st.warning("⚠️ Please provide both ad account name and ID.")
#         else:
#             try:
#                 payload = {
#                     "ad_account_name": ad_account_name.strip(),
#                     "ad_account_id": ad_account_id.strip()
#                 }
#                 resp = requests.post(
#                     f"{API_BASE_URL}/config/adaccounts?platform=meta",
#                     json=payload,
#                     headers={"Content-Type": "application/json"}
#                 )
#                 if resp.status_code == 200:
#                     updated_config = resp.json()
#                     st.session_state["ad_accounts"] = updated_config.get("ad_accounts", {})
#                     st.success(f"✅ Ad Account `{ad_account_name}` added successfully.")
#                     # Log the action
#                     log_action(
#                         st.session_state.user.user.id,
#                         "Meta_add_ad_account",
#                         {"ad_account_name": ad_account_name}
#                     )
#                 else:
#                     st.error(f"❌ API Error: {resp.text}")
#             except Exception as e:
#                 st.error(f"❌ Request failed: {e}")
#             st.rerun()  # Refresh to update list
#
# # ---- Delete Ad Account ----
# with st.expander("❌ Delete Ad Account", expanded=False):
#     ad_account_to_delete = st.selectbox(
#         "Select Ad Account to Delete",
#         options=list(st.session_state.get("ad_accounts", {}).keys()),
#         key="delete_ad_account_select"
#     )
#
#     if st.button("Delete Ad Account"):
#         if not ad_account_to_delete:
#             st.warning("⚠️ Please select an ad account to delete.")
#         else:
#             try:
#                 payload = {"ad_account_name": ad_account_to_delete}
#                 resp = requests.delete(
#                     f"{API_BASE_URL}/config/adaccounts?platform=meta",
#                     json=payload,
#                     headers={"Content-Type": "application/json"}
#                 )
#                 if resp.status_code == 200:
#                     updated_config = resp.json()
#                     st.session_state["ad_accounts"] = updated_config.get("ad_accounts", {})
#                     st.success(f"✅ Ad Account `{ad_account_to_delete}` deleted successfully.")
#                     # Log the action
#                     log_action(
#                         st.session_state.user.user.id,
#                         "Meta_delete_ad_account",
#                         {"ad_account_name": ad_account_to_delete}
#                     )
#                 else:
#                     st.error(f"❌ API Error: {resp.text}")
#             except Exception as e:
#                 st.error(f"❌ Request failed: {e}")
#             st.rerun()  # Refresh to update list
#
# # ---- Display Current Ad Accounts ----
# st.subheader("Current Snap Ad Accounts")
# if st.session_state.get("ad_accounts"):
#     for name, ad_id in st.session_state["ad_accounts"].items():
#         st.write(f"**{name}** : `{ad_id}`")
# else:
#     st.info("No ad accounts found.")


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
                {"toggle_value": auto_pause_toggle}
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
        # Create the drawer using st.expander
        with st.expander(f"Campaign: {camp['id']}", expanded=False):
            # Display current profit/loss
            st.write(f"**Current Profit/Loss Value:** `{camp['value']}`")

            # --- Edit Campaign Profit/Loss ---
            new_value = st.number_input(
                "Edit Profit/Loss Value",
                value=camp['value'],
                step=1,
                format="%d",
                key=f"edit_value_{idx}"
            )
            if st.button(f"💾 Update {camp['id']}", key=f"update_{idx}"):
                try:
                    payload = {"campaign": camp["id"], "threshold": new_value}
                    resp = requests.post(f"{API_BASE_URL}/config/campaigns?platform=meta", json=payload)
                    if resp.status_code == 200:
                        updated_config = resp.json()
                        st.session_state["campaign_conditions"] = [
                            {"id": k, "value": v} for k, v in updated_config.get("campaign_loss_thresholds", {}).items()
                        ]
                        st.success(f"✅ Updated `{camp['id']}` to {new_value}")
                        # Log event
                        log_action(
                            st.session_state.user.user.id,
                            "Meta_update_campaign",
                            {"campaign": camp["id"], "value": new_value}
                        )
                    else:
                        st.error(f"❌ API Error: {resp.text}")
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
                st.rerun()

            # --- Delete Campaign ---
            if st.button(f"❌ Delete {camp['id']}", key=f"delete_{idx}"):
                try:
                    payload = {"campaign": camp["id"]}
                    resp = requests.delete(f"{API_BASE_URL}/config/campaigns?platform=meta", json=payload)
                    if resp.status_code == 200:
                        updated_config = resp.json()
                        st.session_state["campaign_conditions"] = [
                            {"id": k, "value": v} for k, v in updated_config.get("campaign_loss_thresholds", {}).items()
                        ]
                        st.success(f"🗑️ Deleted `{camp['id']}`")
                        # Log event
                        log_action(
                            st.session_state.user.user.id,
                            "Meta_delete_campaign",
                            {"campaign": camp["id"]}
                        )
                    else:
                        st.error(f"❌ API Error: {resp.text}")
                except Exception as e:
                    st.error(f"❌ Request failed: {e}")
                st.rerun()