import pandas as pd
from app.services.elasticsearch_service import create_index, index_data

def load_and_index_telco_data():
    # File path to the Telco dataset
    file_path = 'C:/Users/jemal/Downloads/archive1/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    df = pd.read_csv(file_path)

    # Preprocess TotalCharges column
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)

    # Encode Churn column as boolean
    df['Churn'] = df['Churn'].apply(lambda x: True if x == "Yes" else False)

    # Define Elasticsearch mapping
    telco_mapping = {
        "mappings": {
            "properties": {
                "customerID": {"type": "keyword"},
                "gender": {"type": "keyword"},
                "SeniorCitizen": {"type": "integer"},
                "Partner": {"type": "keyword"},
                "Dependents": {"type": "keyword"},
                "tenure": {"type": "integer"},
                "PhoneService": {"type": "keyword"},
                "MultipleLines": {"type": "keyword"},
                "InternetService": {"type": "keyword"},
                "OnlineSecurity": {"type": "keyword"},
                "OnlineBackup": {"type": "keyword"},
                "DeviceProtection": {"type": "keyword"},
                "TechSupport": {"type": "keyword"},
                "StreamingTV": {"type": "keyword"},
                "StreamingMovies": {"type": "keyword"},
                "Contract": {"type": "keyword"},
                "PaperlessBilling": {"type": "keyword"},
                "PaymentMethod": {"type": "keyword"},
                "MonthlyCharges": {"type": "float"},
                "TotalCharges": {"type": "float"},
                "Churn": {"type": "boolean"}
            }
        }
    }

    # Create Elasticsearch index
    create_index("telco_customer_churn_index", telco_mapping)

    # Index each row as a document
    for _, row in df.iterrows():
        doc = row.to_dict()
        try:
            index_data("telco_customer_churn_index", doc)
        except Exception as e:
            print(f"Error indexing document {doc.get('customerID', 'Unknown ID')}: {e}")

if __name__ == "__main__":
    load_and_index_telco_data()


