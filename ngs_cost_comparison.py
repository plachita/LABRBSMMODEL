import streamlit as st
import pandas as pd
import numpy as np
from math import floor

def main():
    st.set_page_config(page_title="NGS Cost Comparison", layout="centered")
    st.title("🧬 NGS Cost Comparison: SOPHiA vs Current Workflow")

    st.markdown("Compare per-sample cost and profitability using SOPHiA's wet+dry bench bundle versus your current workflow.")

    # --- Lab & Platform Inputs ---
    st.sidebar.header("🧪 Lab Configuration")

    platform = st.sidebar.selectbox("Sequencing Platform", ["NS550", "NS2000 P3", "Aviti High"])
    panel = st.sidebar.selectbox("Panel Type", {
        "Small Panel (160 genes)": 5,
        "Medium Panel (500 genes)": 6,
        "Large Panel (WES)": 45,
        "Genome (WGS)": 90
    }.keys())

    panel_size_gb = {
        "Small Panel (160 genes)": 5,
        "Medium Panel (500 genes)": 6,
        "Large Panel (WES)": 45,
        "Genome (WGS)": 90
    }[panel]

    flowcell_output_gb = st.sidebar.number_input("Flow Cell Output (Gb)", value=360)
    flowcell_cost = st.sidebar.number_input("Flow Cell Cost ($)", value=6335)

    reimbursement = st.sidebar.number_input("Expected Reimbursement ($)", value=650)

    # --- Cost Inputs ---
    st.sidebar.header("💰 Cost Inputs")

    current_wet_cost = st.sidebar.number_input("Current Wet Bench Cost/Test ($)", value=150)
    current_bio_cost = st.sidebar.number_input("Current Bioinformatics Cost/Test ($)", value=110)

    sophia_bundle_cost = st.sidebar.number_input("SOPHiA Reagent + DDM Bundle Cost/Test ($)", value=225)

    # --- Calculations ---
    samples_per_run = floor(flowcell_output_gb / panel_size_gb)
    flowcell_cost_per_sample = flowcell_cost / samples_per_run if samples_per_run > 0 else np.nan

    current_total_cost = flowcell_cost_per_sample + current_wet_cost + current_bio_cost
    sophia_total_cost = flowcell_cost_per_sample + sophia_bundle_cost

    current_profit = reimbursement - current_total_cost
    sophia_profit = reimbursement - sophia_total_cost

    profit_delta = sophia_profit - current_profit

    # --- Results Display ---
    results = pd.DataFrame([
        {
            "Workflow": "Current",
            "Flow Cell Cost/sample": round(flowcell_cost_per_sample, 2),
            "Wet Bench": current_wet_cost,
            "Bioinformatics": current_bio_cost,
            "Total Cost": round(current_total_cost, 2),
            "Reimbursement": reimbursement,
            "Profit/Test": round(current_profit, 2)
        },
        {
            "Workflow": "SOPHiA",
            "Flow Cell Cost/sample": round(flowcell_cost_per_sample, 2),
            "Wet Bench": sophia_bundle_cost,
            "Bioinformatics": 0,
            "Total Cost": round(sophia_total_cost, 2),
            "Reimbursement": reimbursement,
            "Profit/Test": round(sophia_profit, 2)
        }
    ])

    st.subheader(f"🧾 Results for {panel} on {platform}")
    st.dataframe(results)

    st.markdown(f"**Samples per Flow Cell Run:** `{samples_per_run}`")
    st.markdown(f"**Profit Delta (SOPHiA vs Current):** `${profit_delta:.2f}` per test")

if __name__ == "__main__":
    main()
