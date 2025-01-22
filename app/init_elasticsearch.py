import pandas as pd
from app.services.elasticsearch_service import create_index, index_data

# Define index name
index_name = 'telco_customer_churn_index'

# Define Elasticsearch mappings
mappings = {
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

# Function to load, preprocess, and index Telco data
def load_and_index_telco_data():
    # File path to the Telco dataset
    file_path = 'C:/Users/jemal/Downloads/archive1/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    df = pd.read_csv(file_path)

    # Preprocess TotalCharges column
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)

    # Encode Churn column as boolean
    df['Churn'] = df['Churn'].apply(lambda x: True if x == "Yes" else False)

    # Create Elasticsearch index with mappings
    create_index(index_name, mappings)

    # Convert the DataFrame to a list of dictionaries
    records = df.to_dict(orient='records')

    # Prepare actions for indexing
    for record in records:
        # Adjust document fields for exact matching (use .keyword for specified fields)
        adjusted_record = {}
        for key, value in record.items():
            # Apply .keyword for fields that are of keyword type
            if key in ['gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines', 'InternetService', 'Contract', 'PaymentMethod', 'StreamingTV', 'StreamingMovies', 'DeviceProtection', 'TechSupport', 'OnlineSecurity', 'OnlineBackup', 'PaperlessBilling']:
                # Ensure that fields like 'gender' are treated as strings, not objects
                if isinstance(value, str):
                    adjusted_record[key] = value
                else:
                    adjusted_record[key] = value
            else:
                adjusted_record[key] = value

        try:
            # Index the document using the index_data function
            index_data(index_name, adjusted_record)
        except Exception as e:
            print(f"Error indexing document with customerID {record.get('customerID', 'Unknown ID')}: {e}")

# Run the function to load and index data
if __name__ == "__main__":
    load_and_index_telco_data()
