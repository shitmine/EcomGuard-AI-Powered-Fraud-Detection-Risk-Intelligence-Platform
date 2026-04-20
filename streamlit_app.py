import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="EcomGuard - Fraud Intelligence", layout="wide")
st.title("🛡️ EcomGuard: AI-Powered Fraud Detection Dashboard")

# Load data (same pattern as Sap_project)
try:
    raw_data = pd.read_sql("SELECT * FROM fact_orders ORDER BY order_date DESC LIMIT 500", 
                           sqlite3.connect('data/warehouse/ecommerce.db'))
    processed = pd.read_csv('output/processed_fraud_orders.csv')
except:
    st.error("Please run main.py first to generate data and process fraud.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", len(raw_data))
col2.metric("High Risk Orders", len(processed[processed['status'] == "High Risk"]))
col3.metric("Avg Risk Score", f"{processed['risk_score'].mean():.1f}%")

st.subheader("Raw Orders (Last 10)")
st.dataframe(raw_data.tail(10), use_container_width=True)

st.subheader("Processed Fraud Data")
st.dataframe(processed[['order_id', 'total_amount', 'risk_score', 'status']].tail(10), use_container_width=True)

st.subheader("Detected High-Risk / Anomalies")
high_risk = processed[processed['status'] == "High Risk"]
if high_risk.empty:
    st.success("No high-risk orders detected!")
else:
    st.warning(f"{len(high_risk)} high-risk orders found")
    st.dataframe(high_risk, use_container_width=True)

st.subheader("Risk Score Trend")
st.line_chart(processed.set_index('order_date')['risk_score'] if 'order_date' in processed else processed['risk_score'])
