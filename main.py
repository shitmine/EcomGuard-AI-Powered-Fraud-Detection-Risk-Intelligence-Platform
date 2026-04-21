import streamlit as st
import pandas as pd
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta

st.set_page_config(page_title="EcomGuard - Fraud Intelligence", layout="wide")
st.title("🛡️ EcomGuard: AI-Powered Fraud Detection Dashboard")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "warehouse" / "ecommerce.db"
CSV_PATH = BASE_DIR / "output" / "processed_fraud_orders.csv"

def generate_demo_data(n=100):
    dates = [datetime.today() - timedelta(days=i) for i in range(n)]
    dates.sort()

    processed = pd.DataFrame({
        "order_id": [f"ORD{1000+i}" for i in range(n)],
        "total_amount": [round(random.uniform(200, 5000), 2) for _ in range(n)],
        "risk_score": [round(random.uniform(5, 95), 1) for _ in range(n)],
        "order_date": dates
    })

    processed["status"] = processed["risk_score"].apply(
        lambda x: "High Risk" if x >= 70 else "Medium Risk" if x >= 40 else "Low Risk"
    )

    raw_data = processed.copy()
    return raw_data, processed

raw_data = pd.DataFrame()
processed = pd.DataFrame()

try:
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        raw_data = pd.read_sql(
            "SELECT * FROM fact_orders ORDER BY order_date DESC LIMIT 500",
            conn
        )
        conn.close()
    else:
        raw_data, processed = generate_demo_data(120)

    if CSV_PATH.exists():
        processed = pd.read_csv(CSV_PATH)
    elif processed.empty:
        raw_data, processed = generate_demo_data(120)

except Exception as e:
    st.warning(f"⚠️ Real data not found, showing random demo data instead. Error: {e}")
    raw_data, processed = generate_demo_data(120)

col1, col2, col3 = st.columns(3)

high_risk_count = 0
if "status" in processed.columns:
    high_risk_count = len(processed[processed["status"] == "High Risk"])

avg_risk_score = "0.0%"
if "risk_score" in processed.columns and len(processed) > 0:
    avg_risk_score = f"{processed['risk_score'].mean():.1f}%"

col1.metric("Total Orders (Recent)", len(raw_data))
col2.metric("High Risk Orders", high_risk_count)
col3.metric("Avg Risk Score", avg_risk_score)

st.subheader("📋 Raw Orders (Last 10)")
st.dataframe(raw_data.tail(10), use_container_width=True)

st.subheader("🔍 Processed Fraud Data (Last 10)")
cols_to_show = ["order_id", "total_amount", "risk_score", "status"]

if all(col in processed.columns for col in cols_to_show):
    st.dataframe(processed[cols_to_show].tail(10), use_container_width=True)
else:
    st.dataframe(processed.tail(10), use_container_width=True)

st.subheader("🚨 Detected High-Risk Orders")

if "status" in processed.columns:
    high_risk = processed[processed["status"] == "High Risk"]
else:
    high_risk = pd.DataFrame()

if high_risk.empty:
    st.success("✅ No high-risk orders detected!")
else:
    st.warning(f"🚨 {len(high_risk)} high-risk orders found")
    st.dataframe(high_risk, use_container_width=True)

st.subheader("📈 Risk Score Trend")

if "risk_score" in processed.columns and len(processed) > 0:
    chart_data = processed.copy()

    if "order_date" in chart_data.columns:
        chart_data["order_date"] = pd.to_datetime(chart_data["order_date"], errors="coerce")
        chart_data = chart_data.dropna(subset=["order_date"]).sort_values("order_date")

        if not chart_data.empty:
            st.line_chart(chart_data.set_index("order_date")["risk_score"])
        else:
            st.info("No valid order dates available for plotting.")
    else:
        st.line_chart(chart_data["risk_score"])
else:
    st.info("No risk score data available yet.")

