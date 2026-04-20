import pandas as pd
import sqlite3
import joblib
import os

def process_fraud():
    # Load your existing warehouse (reuses everything from original pipeline)
    conn = sqlite3.connect('data/warehouse/ecommerce.db')
    df = pd.read_sql("SELECT * FROM fact_orders", conn)
    conn.close()

    # Load pre-trained models (from 05_fraud_detection.py)
    model = joblib.load('models/fraud_model.pkl')
    iso = joblib.load('models/anomaly_model.pkl')

    # Feature engineering (same as training)
    df['order_hour'] = pd.to_datetime(df['order_date']).dt.hour
    df['amount_per_item'] = df['total_amount'] / df['num_items'].clip(lower=1)
    df['velocity_24h'] = 999  # simplified for batch

    features = ['total_amount', 'num_items', 'order_hour', 'amount_per_item', 'velocity_24h']
    X = df[features].fillna(0)

    # Fraud scoring + anomaly flag
    df['risk_score'] = model.predict_proba(X)[:, 1] * 100
    df['anomaly_flag'] = iso.predict(X) == -1
    df['status'] = df['risk_score'].apply(lambda x: "High Risk" if x > 70 else "Normal")

    # Save to output/ (exactly like Sap_project)
    os.makedirs('output', exist_ok=True)
    df.to_csv('output/processed_fraud_orders.csv', index=False)
    print(df[['order_id', 'total_amount', 'risk_score', 'status']].tail(10))
    print(f"✅ Fraud processing complete! High-risk orders: {len(df[df['status'] == 'High Risk'])}")

if __name__ == "__main__":
    process_fraud()
