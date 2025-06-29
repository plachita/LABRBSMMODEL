import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json

st.set_page_config(page_title="NGS Reimbursement Intelligence", layout="wide")

if 'saved_sessions' not in st.session_state:
    st.session_state['saved_sessions'] = {}

# --- Tabs ---
tabs = st.tabs(["Lab Profile", "Financials", "Risk Assessment", "Projections", "Workflow Comparison", "Export", "Glossary"])

# --- Lab Profile ---
with tabs[0]:
    st.header("Lab Profile Setup")
    backbone = st.selectbox("Test Backbone", ["Panel", "Exome", "Genome"], help="Select the assay platform used for sequencing.")
    reporting = st.radio("Reporting Strategy", ["Full Report", "Carve-out Panels"], help="Report full results or a targeted subset.")
    positioning = st.radio("Test Positioning", ["First-line", "Reflex"], help="Used upfront or as reflex.")
    region = st.selectbox("Region", ["National", "Northeast", "South", "Midwest", "West"], help="Region affects payer behavior.")
    batch_size = st.number_input("Batch Size", min_value=1, value=20, help="Samples run per sequencing batch.")
    cost_per_sample = st.number_input("Cost per Sample ($)", min_value=0.0, value=728.00, help="Includes reagents, labor, informatics, and overhead.")
    reimbursement = st.number_input("Reimbursement per Test ($)", min_value=0.0, value=1000.00, help="Expected payer reimbursement.")

# --- Risk Calculation ---
risk_map = {"Panel": 1.0, "Exome": 1.2, "Genome": 1.3}
pos_map = {"First-line": 1.3, "Reflex": 1.0}
region_map = {"National": 1.0, "Northeast": 1.1, "South": 1.2, "Midwest": 1.05, "West": 1.15}
risk_score = risk_map[backbone] * pos_map[positioning] * region_map[region]

# --- Financials ---
with tabs[1]:
    st.header("Financial Summary")
    profit = reimbursement - cost_per_sample
    roi = (profit / cost_per_sample) * 100 if cost_per_sample > 0 else 0
    payback = round(cost_per_sample / profit, 2) if profit > 0 else np.nan
    col1, col2, col3 = st.columns(3)
    col1.metric("Profit per Sample", f"${profit:.2f}")
    col2.metric("ROI", f"{roi:.1f}%")
    col3.metric("Payback Period (Samples)", f"{payback}" if not np.isnan(payback) else "N/A")

# --- Risk Assessment ---
with tabs[2]:
    st.header("Denial Risk Assessment")
    st.write("Risk score is derived from test type, positioning, and payer region.")
    st.progress(min(risk_score / 2, 1.0))
    st.write(f"**Risk Score:** {risk_score:.2f} (1.0 = low risk, >1.2 = high risk)")

# --- Projections ---
with tabs[3]:
    st.header("ROI Projection by Volume")
    volume = np.arange(1, 101)
    total_profit = volume * profit
    cost_total = volume * cost_per_sample
    revenue_total = volume * reimbursement
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=volume, y=revenue_total, mode='lines', name='Revenue'))
    fig.add_trace(go.Scatter(x=volume, y=cost_total, mode='lines', name='Cost'))
    fig.add_trace(go.Scatter(x=volume, y=total_profit, mode='lines', name='Profit'))
    fig.update_layout(title="Revenue, Cost, and Profit Projection", xaxis_title="Sample Volume", yaxis_title="Dollars ($)")
    st.plotly_chart(fig, use_container_width=True)

# --- Workflow Comparison ---
with tabs[4]:
    st.header("Compare SOPHiA vs Current Workflow")

    st.subheader("Your Current Workflow")
    current_cost = st.number_input("Current Cost per Sample ($)", min_value=0.0, value=950.0)
    current_tat = st.number_input("Current Turnaround Time (days)", min_value=0.0, value=10.0)
    current_software_cost = st.number_input("Annual Software Cost ($)", min_value=0.0, value=20000.0)
    current_fte = st.number_input("Staff Needed (FTEs)", min_value=0, value=2)
    annual_volume = st.number_input("Annual Sample Volume", min_value=1, value=1000)

    st.subheader("SOPHiA Workflow (Predefined)")
    sophia_cost = 75.0
    sophia_tat = 5.0
    sophia_software_cost = 0
    sophia_fte = 1

    st.markdown("### Cost & Efficiency Comparison")
    df_compare = pd.DataFrame({
        'Metric': ["Cost per Sample", "Turnaround Time (days)", "Annual Software Cost", "FTE Required"],
        'Current Workflow': [f"${current_cost}", f"{current_tat} days", f"${current_software_cost}", current_fte],
        'SOPHiA Workflow': [f"${sophia_cost}", f"{sophia_tat} days", f"${sophia_software_cost}", sophia_fte]
    })
    st.table(df_compare)

    # --- Annual Savings Calculator ---
    st.markdown("### 📈 Annual Savings Summary")
    annual_cost_current = (current_cost * annual_volume) + current_software_cost
    annual_cost_sophia = (sophia_cost * annual_volume) + sophia_software_cost
    annual_savings = annual_cost_current - annual_cost_sophia

    st.metric("Annual Cost (Current)", f"${annual_cost_current:,.2f}")
    st.metric("Annual Cost (SOPHiA)", f"${annual_cost_sophia:,.2f}")
    st.metric("Projected Savings", f"${annual_savings:,.2f}")

    # --- Bar Chart ---
    fig_compare = go.Figure(data=[
        go.Bar(name='Current', x=['Cost'], y=[annual_cost_current]),
        go.Bar(name='SOPHiA', x=['Cost'], y=[annual_cost_sophia])
    ])
    fig_compare.update_layout(barmode='group', title="Annual Cost Comparison", yaxis_title="USD")
    st.plotly_chart(fig_compare, use_container_width=True)

    # --- Break-Even Calculator ---
    st.markdown("### 💸 Break-Even Volume Simulation")
    savings_per_sample = current_cost - sophia_cost
    if savings_per_sample > 0:
        breakeven_volume = current_software_cost / savings_per_sample
        st.success(f"You break even after ~{int(breakeven_volume)} samples.")
    else:
        st.warning("No break-even point — current workflow is cheaper per sample.")

# --- Export ---
with tabs[5]:
    st.header("Save or Export Session")
    if st.button("Save Session"):
        session_data = {
            "backbone": backbone, "reporting": reporting, "positioning": positioning,
            "region": region, "batch_size": batch_size,
            "cost_per_sample": cost_per_sample, "reimbursement": reimbursement,
            "profit": profit, "roi": roi, "payback": payback, "risk_score": risk_score
        }
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['saved_sessions'][timestamp] = session_data
        st.success("Session saved!")

    if st.session_state['saved_sessions']:
        selected = st.selectbox("Restore a session:", list(st.session_state['saved_sessions'].keys()))
        if st.button("Load Session"):
            st.json(st.session_state['saved_sessions'][selected])

    if st.button("Download JSON Report"):
        st.download_button(
            label="Download",
            file_name="ngs_report.json",
            mime="application/json",
            data=json.dumps(session_data, indent=2)
        )

# --- Glossary ---
with tabs[6]:
    st.header("Glossary & Definitions")
    st.markdown("""
    - **Test Backbone**: Sequencing method (Panel, Exome, Genome).
    - **Carve-out Panels**: Running a larger assay but reporting a targeted subset.
    - **Reflex Testing**: Ordered after initial results; may impact denial risk.
    - **ROI**: Return on Investment = (Profit / Cost) x 100.
    - **Payback Period**: Number of samples to recover cost.
    - **Risk Score**: Internal model to predict likelihood of payer denial.
    - **Batch Size**: Number of samples processed together to reduce cost.
    - **Export Options**: Save sessions or generate downloadable JSON reports.
    - **SOPHiA Workflow**: Unified platform including wet lab, informatics, and reporting without added software fees.
    - **Break-even Point**: Number of samples where SOPHiA workflow savings offset software cost.
    - **Annual Savings**: Total financial benefit projected over a year when switching workflows.
    """)
