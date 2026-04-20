"""
EcomGuard - Fraud Detection Model Training
Script 05: Trains AI models for fraud risk scoring
"""

import pandas as pd
import sqlite3
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime

def train_fraud_models():
    print("🔄 Connecting to e-commerce warehouse...")
    
    # Connect to your existing SQLite database
    conn = sqlite3.connect('data/warehouse/ecommerce.db')
    
    # Load orders + RFM features (created by your 03_analytics.py)
    query = """
        SELECT 
            o.order_id,
            o.customer_id,
            o.total_amount,
            o.num_items,
            o.order_date,
            o.payment_method,
            o.channel,
            COALESCE(r.recency, 365) as recency,
            COALESCE(r.frequency, 1) as frequency,
            COALESCE(r.monetary, 0) as monetary
        FROM fact_orders o
        LEFT JOIN rfm_analysis r ON o.customer_id = r.customer_id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    print(f"✅ Loaded {len(df)} orders for training.")

    # Feature Engineering
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['order_hour'] = df['order_date'].dt.hour
    df['order_dayofweek'] = df['order_date'].dt.dayofweek
    df['amount_per_item'] = df['total_amount'] / df['num_items'].clip(lower=1)
    
    # Velocity (simplified - time since last order in hours)
    df = df.sort_values(['customer_id', 'order_date'])
    df['time_since_last'] = df.groupby('customer_id')['order_date'].diff().dt.total_seconds() / 3600
    df['velocity_24h'] = df['time_since_last'].fillna(999)

    # Final features for model
    features = [
        'total_amount', 'num_items', 'recency', 'frequency', 'monetary',
        'order_hour', 'order_dayofweek', 'amount_per_item', 'velocity_24h'
    ]

    X = df[features].fillna(0)

    # 1. Unsupervised Anomaly Detection
    print("Training Isolation Forest for anomaly detection...")
    iso_forest = IsolationForest(
        contamination=0.02,   # Assume ~2% fraud
        random_state=42,
        n_estimators=100
    )
    iso_forest.fit(X)

    # 2. Supervised Risk Classifier (using anomaly as proxy label for demo)
    print("Training Random Forest for risk scoring...")
    df['fraud_label'] = (iso_forest.predict(X) == -1).astype(int)  # 1 = suspicious

    X_train, X_test, y_train, y_test = train_test_split(
        X, df['fraud_label'], test_size=0.2, random_state=42, stratify=df['fraud_label']
    )

    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    rf_model.fit(X_train, y_train)

    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(rf_model, 'models/fraud_model.pkl')
    joblib.dump(iso_forest, 'models/anomaly_model.pkl')

    print("✅ Fraud detection models trained successfully!")
    print(f"   • Models saved in: models/")
    print(f"   • Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Quick performance summary
    train_score = rf_model.score(X_train, y_train)
    print(f"   • Training Accuracy: {train_score:.4f}")

if __name__ == "__main__":
    train_fraud_models()
