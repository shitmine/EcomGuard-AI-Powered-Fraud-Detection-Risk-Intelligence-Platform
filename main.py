import os
print(" Starting EcomGuard Fraud Detection System...")
print("Running E-commerce Pipeline...")
os.system("python -m scripts.01_generate_data")   
os.system("python -m scripts.02_etl_pipeline")
os.system("python -m scripts.03_analytics")
os.system("python -m scripts.04_streaming")

print("Processing Fraud Detection...")
os.system("python processor.py")

print("✅ Done! Check output/ folder and run: streamlit run streamlit_app.py")
