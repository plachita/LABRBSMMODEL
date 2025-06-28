# NGS Cost Comparison App

This is a Streamlit app to compare Next-Generation Sequencing (NGS) workflow profitability between a lab's current approach and SOPHiA GENETICS' wet+dry bench bundled solution.

## Features
- Input flow cell parameters and costs
- Enter lab-specific reagent, bioinformatics, and reimbursement values
- Compare total cost per test and profit/test
- Evaluate SOPHiA vs Current workflow

## How to Run

### Local
1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the app:
    ```bash
    streamlit run ngs_cost_comparison.py
    ```

### Cloud
- Deploy via [Streamlit Cloud](https://share.streamlit.io) or [Hugging Face Spaces](https://huggingface.co/spaces)
