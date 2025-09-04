import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="A/B Campaign Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---

def generate_campaign_data(users_sent):
    """Generates random performance data for a campaign."""
    # Ensure delivered is less than or equal to sent
    delivered = int(users_sent * np.random.uniform(0.90, 0.98))
    # Ensure displayed is less than or equal to delivered
    displayed = int(delivered * np.random.uniform(0.85, 0.95))
    # Ensure clicks is less than or equal to displayed
    clicks = int(displayed * np.random.uniform(0.05, 0.15))

    return {
        "Notification Sent": users_sent,
        "Notification Delivered": delivered,
        "Notification Displayed": displayed,
        "Notification Clicked": clicks
    }

def calculate_metrics(data):
    """Calculates key performance metrics for a campaign."""
    delivery_rate = (data["Notification Delivered"] / data["Notification Sent"]) * 100 if data["Notification Sent"] > 0 else 0
    display_rate = (data["Notification Displayed"] / data["Notification Delivered"]) * 100 if data["Notification Delivered"] > 0 else 0
    # Click-Through Rate (CTR) is based on delivered messages
    ctr = (data["Notification Clicked"] / data["Notification Delivered"]) * 100 if data["Notification Delivered"] > 0 else 0

    return {
        "Delivery Rate (%)": delivery_rate,
        "Display Rate (%)": display_rate,
        "Click-Through Rate (%)": ctr
    }

# --- Sidebar Controls ---
st.sidebar.header("Campaign Setup")
st.sidebar.markdown("""
Adjust the parameters for the A/B test simulation. The script will generate random data based on these settings.
""")

total_users = st.sidebar.number_input(
    "Total User Base",
    min_value=10000,
    max_value=1000000,
    value=100000,
    step=10000
)
ab_test_percentage = st.sidebar.slider(
    "A/B Test Group Size (%)",
    min_value=10,
    max_value=50,
    value=10,
    step=2
)

# Refresh button
if st.sidebar.button("🔄 Rerun Simulation"):
    st.rerun()


# --- Main Dashboard ---
st.title("📊 A/B Push Notification Campaign Dashboard")
st.markdown("""
This dashboard analyzes a simulated A/B test for a push notification campaign.
- An **A/B test** is sent to a small percentage of the total users.
- A **winner** is determined based on the Click-Through Rate (CTR).
- The **winning campaign** is then rolled out to the remaining user base.
""")

# --- Data Generation & A/B Test Phase ---
ab_test_users = int(total_users * (ab_test_percentage / 100))
campaign_a_users = ab_test_users // 2
campaign_b_users = ab_test_users // 2
remaining_users = total_users - ab_test_users

# Generate data for the A/B test
data_a = generate_campaign_data(campaign_a_users)
data_b = generate_campaign_data(campaign_b_users)

# Calculate metrics
metrics_a = calculate_metrics(data_a)
metrics_b = calculate_metrics(data_b)

# --- A/B Test Analysis Section ---
st.header(f"Phase 1: A/B Test Analysis ({ab_test_percentage}% of Users)")
st.markdown(f"The initial test was sent to **{ab_test_users:,}** users, split evenly between Campaign A and Campaign B.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Campaign A Performance")
    for key, value in data_a.items():
        st.metric(label=key, value=f"{value:,}")
    st.info(f"**Click-Through Rate: {metrics_a['Click-Through Rate (%)']:.2f}%**")


with col2:
    st.subheader("Campaign B Performance")
    for key, value in data_b.items():
        st.metric(label=key, value=f"{value:,}")
    st.info(f"**Click-Through Rate: {metrics_b['Click-Through Rate (%)']:.2f}%**")

# --- Winner Determination ---
st.header("Phase 2: Winner Determination")

if metrics_a['Click-Through Rate (%)'] > metrics_b['Click-Through Rate (%)']:
    winner_name = "Campaign A"
    winner_data = data_a
    winner_metrics = metrics_a
    loser_name = "Campaign B"
    loser_ctr = metrics_b['Click-Through Rate (%)']
    st.success(f"🏆 **Winner: Campaign A** had a higher Click-Through Rate ({winner_metrics['Click-Through Rate (%)']:.2f}%) and has been selected for the full rollout.")
else:
    winner_name = "Campaign B"
    winner_data = data_b
    winner_metrics = metrics_b
    loser_name = "Campaign A"
    loser_ctr = metrics_a['Click-Through Rate (%)']
    st.success(f"🏆 **Winner: Campaign B** had a higher Click-Through Rate ({winner_metrics['Click-Through Rate (%)']:.2f}%) and has been selected for the full rollout.")

# --- Visualization ---
st.subheader("A/B Test Funnel Comparison")
col_vis1, col_vis2 = st.columns(2)

with col_vis1:
    fig_a = go.Figure(go.Funnel(
        y = ["Sent", "Delivered", "Displayed", "Clicked"],
        x = [data_a["Notification Sent"], data_a["Notification Delivered"], data_a["Notification Displayed"], data_a["Notification Clicked"]],
        textposition = "inside",
        textinfo = "value+percent initial",
        marker = {"color": "rgb(26, 118, 255)"}
        ))
    fig_a.update_layout(title_text="Campaign A Funnel")
    st.plotly_chart(fig_a, use_container_width=True)

with col_vis2:
    fig_b = go.Figure(go.Funnel(
        y = ["Sent", "Delivered", "Displayed", "Clicked"],
        x = [data_b["Notification Sent"], data_b["Notification Delivered"], data_b["Notification Displayed"], data_b["Notification Clicked"]],
        textposition = "inside",
        textinfo = "value+percent initial",
        marker = {"color": "rgb(55, 83, 109, 0.8)"}
        ))
    fig_b.update_layout(title_text="Campaign B Funnel")
    st.plotly_chart(fig_b, use_container_width=True)


# --- Rollout Phase ---
st.header(f"Phase 3: Rollout of {winner_name}")
st.markdown(f"The winning campaign was sent to the remaining **{remaining_users:,}** users.")

rollout_data = generate_campaign_data(remaining_users)
rollout_metrics = calculate_metrics(rollout_data)

r_col1, r_col2, r_col3, r_col4 = st.columns(4)
r_col1.metric("Notification Sent", f"{rollout_data['Notification Sent']:,}")
r_col2.metric("Notification Delivered", f"{rollout_data['Notification Delivered']:,}")
r_col3.metric("Notification Displayed", f"{rollout_data['Notification Displayed']:,}")
r_col4.metric("Notification Clicked", f"{rollout_data['Notification Clicked']:,}")
st.info(f"**Rollout Click-Through Rate: {rollout_metrics['Click-Through Rate (%)']:.2f}%**")


# --- Final Summary ---
st.header("🚀 Overall Campaign Performance Summary")

# Combine A/B test data of the winner with the rollout data
total_sent = winner_data["Notification Sent"] + rollout_data["Notification Sent"]
total_delivered = winner_data["Notification Delivered"] + rollout_data["Notification Delivered"]
total_displayed = winner_data["Notification Displayed"] + rollout_data["Notification Displayed"]
total_clicks = winner_data["Notification Clicked"] + rollout_data["Notification Clicked"]

final_ctr = (total_clicks / total_delivered) * 100 if total_delivered > 0 else 0

st.markdown(f"By using an A/B test, we successfully identified **{winner_name}** as the better-performing creative. The combined results from both phases are shown below.")

f_col1, f_col2, f_col3, f_col4 = st.columns(4)
f_col1.metric("Total Notifications Sent", f"{total_sent:,}")
f_col2.metric("Total Notifications Delivered", f"{total_delivered:,}")
f_col3.metric("Total Notifications Displayed", f"{total_displayed:,}")
f_col4.metric("Total Notifications Clicked", f"{total_clicks:,}")

st.success(f"**Final Blended Click-Through Rate for the campaign: {final_ctr:.2f}%**")

