import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

MODEL_PATH = "telco_churn_model.pkl"

def train_churn_model_from_file(file_path):
    """
    Train the churn prediction model using the dataset from the specified file path.
    """
    # Load the data
    df = pd.read_csv(file_path)

    # Preprocessing: Encode categorical variables and ensure numeric fields
    categorical_columns = [
        "gender", "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
        "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod"
    ]
    for col in categorical_columns:
        df[col] = df[col].astype("category").cat.codes  # Convert categories to numeric codes

    # Convert TotalCharges to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

    # Define features and target variable
    X = df.drop(columns=["customerID", "Churn"])  # Exclude customerID and target variable
    y = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)  # Encode Churn as binary

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy}")

    # Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    return accuracy


def predict_churn_from_file(file_path):
    """
    Predict churn likelihood using the trained model for data in a specified file.
    """
    # Load the model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file '{MODEL_PATH}' not found. Train the model first.")

    model = joblib.load(MODEL_PATH)

    # Load data from the file
    df = pd.read_csv(file_path)

    # Preprocessing: Encode categorical variables and ensure numeric fields
    categorical_columns = [
        "gender", "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
        "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod"
    ]
    for col in categorical_columns:
        df[col] = df[col].astype("category").cat.codes  # Convert categories to numeric codes

    # Convert TotalCharges to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

    # Ensure only features used during training are passed to the model
    required_columns = model.feature_names_in_
    df_features = df[required_columns]

    # Predict churn
    predictions = model.predict(df_features)

    # Add predictions to the original DataFrame
    df["ChurnPrediction"] = predictions

    return df