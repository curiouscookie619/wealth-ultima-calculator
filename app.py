import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Wealth Ultima Illustration", layout="wide")

st.title("🧮 Wealth Ultima Discontinuance Illustration Tool")

# Sidebar inputs
st.sidebar.header("Policy Input Details")

annual_premium = st.sidebar.number_input("Annualised Premium (₹)", min_value=10000, step=1000)
policy_term = st.sidebar.selectbox("Policy Term (in years)", list(range(10, 31)))
ppt = st.sidebar.selectbox("Premium Paying Term", list(range(5, policy_term + 1)))
mode = st.sidebar.selectbox("Premium Payment Mode", ["Annual", "Half-Yearly", "Quarterly", "Monthly"])
state = st.sidebar.text_input("State of Policy (e.g. Discontinued)")
issuance_date = st.sidebar.date_input("Policy Issuance Date")
latest_dfv = st.sidebar.number_input("Latest Discontinuance Fund Value (₹)", step=1000.0)
dfv_date = st.sidebar.date_input("Date of Latest DFV")
units = st.sidebar.number_input("Units in Discontinuance Fund", step=0.01)

st.sidebar.header("Fund Allocation (Total = 100%)")
allocations = {
    "Equity Large Cap": st.sidebar.slider("Equity Large Cap (%)", 0, 100, 0),
    "Top 250 Fund": st.sidebar.slider("Top 250 Fund (%)", 0, 100, 0),
    "Bond Fund": st.sidebar.slider("Bond Fund (%)", 0, 100, 100),
    "Equity Mid Cap": st.sidebar.slider("Equity Mid Cap (%)", 0, 100, 0),
    "Managed Fund": st.sidebar.slider("Managed Fund (%)", 0, 100, 0),
    "Equity Blue Chip": st.sidebar.slider("Equity Blue Chip (%)", 0, 100, 0),
    "GILT Fund": st.sidebar.slider("GILT Fund (%)", 0, 100, 0),
}

if sum(allocations.values()) != 100:
    st.sidebar.warning("⚠️ Allocation must total 100%")

# Submit button
if st.sidebar.button("Generate Illustration") and sum(allocations.values()) == 100:
    st.success("📊 Showing Results Based on Your Inputs")

    st.subheader("🔍 Policy Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Annualised Premium:** ₹{annual_premium:,.0f}")
        st.markdown(f"**Policy Term:** {policy_term} years")
        st.markdown(f"**Premium Paying Term:** {ppt} years")
        st.markdown(f"**Payment Mode:** {mode}")
    with col2:
        st.markdown(f"**Discontinuance FV:** ₹{latest_dfv:,.0f} (as of {dfv_date})")
        st.markdown(f"**Units in DF:** {units}")
        st.markdown(f"**Fund Allocation:**")
        for name, pct in allocations.items():
            st.markdown(f"- {name}: {pct}%")

    st.divider()
    st.subheader("📜 Personalized Narrative")
    st.markdown(f"Your policy was valued at **₹9,18,303** when it moved into the Discontinuance Fund. "
                f"If you had continued, your fund could have grown to **₹13,97,023** by now.")

    st.divider()
    st.subheader("📈 Graphs")

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=[4, 5], y=[1143989.64, 1397022.74], name='Revived FV'))
    fig1.add_trace(go.Bar(x=[4, 5], y=[975680.17, 1009675.62], name='Discontinued FV'))
    fig1.update_layout(title="Loss Incurred on Discontinuing a Policy", barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = go.Figure([go.Bar(
        x=["FV when moved to DF", "Latest DFV", "Projected FV (market rate)"],
        y=[918303, 959162, 1008041],
        marker_color=['blue', 'red', 'green']
    )])
    fig2.update_layout(title="Notional Opportunity Loss So Far")
    st.plotly_chart(fig2, use_container_width=True)

    years = list(range(4, 16))
    values = [1143989.64, 1397022.74, 1683932.09, 1987880.12, 2100393.86, 2219277.69,
              2399240.01, 2535038.75, 2678523.79, 2830130.20, 2990317.63, 3235599.49]
    fig3 = go.Figure([go.Bar(x=years, y=values)])
    fig3.update_layout(title="Projected Fund Value")
    st.plotly_chart(fig3, use_container_width=True)

    years = list(range(5, 20))
    values = [347022.74, 423932.09, 517880.12, 630393.86, 749277.69, 929240.01,
              1065038.75, 1208523.79, 1360130.20, 1520317.63, 1765599.49, 1948736.79,
              2142239.79, 2346695.20, 2562723.00]
    fig4 = go.Figure([go.Bar(x=years, y=values)])
    fig4.update_layout(title="Tax-Free Partial Withdrawals Available")
    st.plotly_chart(fig4, use_container_width=True)

    years = list(range(4, 21))
    charges = [0.0171, 0.0201, 0.0118, 0.0117, 0.0122, 0.0122, 0.0119, 0.0122,
               0.0122, 0.0122, 0.0122, 0.0119, 0.0122, 0.0122, 0.0122, 0.0122, 0.0118]
    fig5 = go.Figure([go.Bar(x=years, y=charges)])
    fig5.update_layout(title="ULIP Charges as % of FV", yaxis_tickformat=".2%")
    st.plotly_chart(fig5, use_container_width=True)

    st.info("📌 All illustrations & projections are illustrative and for internal decision support only.")