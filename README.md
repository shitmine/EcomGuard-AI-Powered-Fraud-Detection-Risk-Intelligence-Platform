# EcomGuard-AI-Powered-Fraud-Detection-Risk-Intelligence-Platform

EcomGuard extends the original 30-task educational e-commerce pipeline into a **production-grade AI fraud detection system**.  
It keeps the full original pipeline **100% untouched** while adding intelligent fraud scoring, anomaly detection, alerts, and a beautiful Streamlit dashboard.

##  What is EcomGuard?

EcomGuard automatically detects fraudulent orders in real-time, assigns AI risk scores (0–100), triggers alerts, and provides an interactive investigation dashboard — exactly like modern e-commerce platforms (Amazon, Flipkart, Shopify).

##  Key Features

**AI Risk Scoring** — Hybrid ML model (Isolation Forest + Random Forest) scores every order
**Anomaly Detection** — Catches unusual patterns (velocity spikes, amount outliers, odd timing)
**Real-time Alert Engine** — Processes live order streams (extends your existing Kafka simulation)
**Interactive Fraud Dashboard** — Clean Streamlit UI with live metrics, high-risk queue, and charts
**Automated Reports** — PDF + CSV exports of flagged transactions
**Zero breaking changes** — Original 30-task pipeline runs exactly as before

##  Project Structure 
Pipeline 
     ↓
01_generate_data → 02_etl → 03_analytics (RFM + cohorts) → 04_streaming
     ↓
SQLite Star-Schema Warehouse (data/warehouse/ecommerce.db)
     ↓
main.py
     ↓
processor.py          ← Loads warehouse → Runs AI fraud scoring & anomaly detection
     ↓
output/processed_fraud_orders.csv
     ↓
streamlit_app.py      ← Live fraud dashboard + visualizations

## Business Impact

**Reduces fraud losses by flagging high-risk orders instantly
**Improves customer experience with minimal false positives
**Audit-ready reports for compliance teams



