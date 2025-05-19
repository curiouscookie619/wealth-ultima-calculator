import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import date, timedelta
from jinja2 import Template
import pdfkit
import uuid
import os

st.set_page_config(page_title="Wealth Ultima PDF Generator", layout="wide")

# Constants
today_minus_1 = date.today() - timedelta(days=1)
state_options = [
    "Premium Paying (During Lock -in)",
    "Premium Paying (Post Lock -in)",
    "Discontinuance Within Lock-in",
    "Paid Up"
]

# Input UI
st.title("📄 Wealth Ultima Illustration (Charts + PDF)")
st.sidebar.header("Enter Policy Details")

annual_premium = st.sidebar.number_input("Annualised Premium (₹)", min_value=10000, step=1000)
policy_term = st.sidebar.selectbox("Policy Term (in years)", list(range(10, 31)))
ppt = st.sidebar.selectbox("Premium Paying Term", list(range(5, policy_term + 1)))
mode = st.sidebar.selectbox("Premium Payment Mode", ["Annual", "Half-Yearly", "Quarterly", "Monthly"])
state_selected = st.sidebar.selectbox("State of Policy", state_options)
issuance_date = st.sidebar.date_input("Policy Issuance Date")
latest_dfv = st.sidebar.number_input("Latest Discontinuance Fund Value (₹)", step=1000.0)
units = st.sidebar.number_input("Units in Discontinuance Fund", step=0.01)

st.sidebar.markdown("### Fund Allocation (Total = 100%)")
alloc_df = pd.DataFrame({
    "Fund": [
        "Equity Large Cap", "Top 250 Fund", "Bond Fund", "Equity Mid Cap",
        "Managed Fund", "Equity Blue Chip", "GILT Fund"
    ],
    "Allocation %": [0, 0, 100, 0, 0, 0, 0]
})
edited_df = st.sidebar.data_editor(alloc_df, num_rows="fixed")
total_alloc = edited_df["Allocation %"].sum()
if total_alloc != 100:
    st.sidebar.error(f"Allocation total = {total_alloc}%. Must be exactly 100%.")

# Narrations
narration_1 = "Your policy entered the Discontinuance Fund in Year 4. If left as is, it may grow to ₹10,09,676 and be auto-surrendered. But if revived, your funds stay invested and could grow to ₹13,97,023 — an additional ₹3,87,347 in just 1 year."
narration_2 = "Your policy was valued at ₹9,18,303 when it entered the Discontinuance Fund. Today it has grown to ₹9,59,162, but had it stayed in the market, it could’ve reached ₹10,08,041 — a missed gain of ₹48,879."
narration_3 = "With an annual premium of ₹2,00,000, your funds have already grown to ₹9,59,162. If you continue, they could grow to ₹43,91,471 by the end of the policy. To unlock this, you only need to pay ₹7,66,667 more over the next 4 years. (Note: The graph shows growth only till Year 15, but your policy runs till 20 years.)"
narration_4 = "Need funds? Use Partial Withdrawals — your money stays invested, your life cover stays intact, and you still get what you need. If you surrender the policy, you lose all of it — your protection, market exposure, and future growth."
narration_5 = "ULIPs have higher charges in the first 5 years, but these drop significantly after that. You've already crossed the high-cost phase — now is the time to stay invested and benefit from compounding, not exit early."

# Chart generation
def save_chart(fig, filename):
    pio.write_image(fig, filename, width=800, height=500)

def generate_charts():
    chart_paths = []
    # Chart 1
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=[4, 5], y=[1143989.64, 1397022.74], name='Revived FV'))
    fig1.add_trace(go.Bar(x=[4, 5], y=[975680.17, 1009675.62], name='Discontinued FV'))
    fig1.update_layout(title="Loss Incurred on Discontinuing a Policy", barmode='group')
    chart1_path = f"chart1_{uuid.uuid4().hex}.png"
    save_chart(fig1, chart1_path)
    chart_paths.append(chart1_path)

    # Chart 2
    fig2 = go.Figure([go.Bar(
        x=["FV when moved to DF", "Latest DFV", "Projected FV (market rate)"],
        y=[918303, 959162, 1008041],
        marker_color=['blue', 'red', 'green']
    )])
    fig2.update_layout(title="Notional Opportunity Loss So Far")
    chart2_path = f"chart2_{uuid.uuid4().hex}.png"
    save_chart(fig2, chart2_path)
    chart_paths.append(chart2_path)

    # Chart 3
    years = list(range(4, 16))
    values = [1143989.64, 1397022.74, 1683932.09, 1987880.12, 2100393.86, 2219277.69,
              2399240.01, 2535038.75, 2678523.79, 2830130.20, 2990317.63, 3235599.49]
    fig3 = go.Figure([go.Bar(x=years, y=values)])
    fig3.update_layout(title="Projected Fund Value")
    chart3_path = f"chart3_{uuid.uuid4().hex}.png"
    save_chart(fig3, chart3_path)
    chart_paths.append(chart3_path)

    # Chart 4
    years = list(range(5, 20))
    values = [347022.74, 423932.09, 517880.12, 630393.86, 749277.69, 929240.01,
              1065038.75, 1208523.79, 1360130.20, 1520317.63, 1765599.49, 1948736.79,
              2142239.79, 2346695.20, 2562723.00]
    fig4 = go.Figure([go.Bar(x=years, y=values)])
    fig4.update_layout(title="Tax-Free Partial Withdrawals Available")
    chart4_path = f"chart4_{uuid.uuid4().hex}.png"
    save_chart(fig4, chart4_path)
    chart_paths.append(chart4_path)

    # Chart 5
    years = list(range(4, 21))
    charges = [0.0171, 0.0201, 0.0118, 0.0117, 0.0122, 0.0122, 0.0119, 0.0122,
               0.0122, 0.0122, 0.0122, 0.0119, 0.0122, 0.0122, 0.0122, 0.0122, 0.0118]
    fig5 = go.Figure([go.Bar(x=years, y=charges)])
    fig5.update_layout(title="ULIP Charges as % of FV", yaxis_tickformat=".2%")
    chart5_path = f"chart5_{uuid.uuid4().hex}.png"
    save_chart(fig5, chart5_path)
    chart_paths.append(chart5_path)

    return chart_paths

# PDF generation logic
if st.sidebar.button("Generate PDF"):
    st.success("🔄 Generating PDF...")

    chart_imgs = generate_charts()

    with open("template.html", "r", encoding="utf-8") as file:
        template_str = file.read()

    template = Template(template_str)
    rendered_html = template.render(
        premium=f"₹{annual_premium:,.0f}",
        term=policy_term,
        ppt=ppt,
        mode=mode,
        issuance_date=str(issuance_date),
        state=state_selected,
        units=units,
        dfv=f"₹{latest_dfv:,.0f}",
        fund_allocation=edited_df.values.tolist(),
        narration_1=narration_1,
        narration_2=narration_2,
        narration_3=narration_3,
        narration_4=narration_4,
        narration_5=narration_5,
        chart1=chart_imgs[0],
        chart2=chart_imgs[1],
        chart3=chart_imgs[2],
        chart4=chart_imgs[3],
        chart5=chart_imgs[4]
    )

    html_file = f"report_{uuid.uuid4().hex}.html"
    pdf_file = html_file.replace(".html", ".pdf")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    pdfkit.from_file(html_file, pdf_file)

    with open(pdf_file, "rb") as f:
        st.download_button("📥 Download PDF", f, file_name="Wealth_Ultima_Illustration.pdf", mime="application/pdf")

    os.remove(html_file)
    os.remove(pdf_file)
    for img in chart_imgs:
        os.remove(img)