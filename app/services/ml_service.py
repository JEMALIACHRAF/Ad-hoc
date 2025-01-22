import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, average_precision_score, accuracy_score
import os

MODEL_PATH = "telco_churn_model.pkl"

def train_churn_model_from_file(file_path):
    """
    Train the churn prediction model using the dataset from the specified file path.
    Evaluates the model using precision, recall, and AUC-PR score.
    """
    df = pd.read_csv(file_path)

    # Preprocessing: Encode categorical variables and ensure numeric fields
    categorical_columns = [
        "gender", "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
        "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod"
    ]
    for col in categorical_columns:
        df[col] = df[col].astype("category").cat.codes

    # Convert TotalCharges to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

    # Define features and target variable
    X = df.drop(columns=["customerID", "Churn"])
    y = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]  # Get probabilities for the positive class

    # Calculate the metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    auc_pr = average_precision_score(y_test, y_pred_proba)  # Precision-Recall AUC

    print(f"Model Accuracy: {accuracy}")
    print(f"Model Precision: {precision}")
    print(f"Model Recall: {recall}")
    print(f"Model AUC-PR: {auc_pr}")

    # Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    return accuracy, precision, recall, auc_pr


def predict_churn_from_file(file_path):
    """
    Predict churn likelihood using the trained model for data in a specified file.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file '{MODEL_PATH}' not found. Train the model first.")

    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(file_path)

    # Preprocessing: Encode categorical variables and ensure numeric fields
    categorical_columns = [
        "gender", "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
        "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod"
    ]
    for col in categorical_columns:
        df[col] = df[col].astype("category").cat.codes

    # Convert TotalCharges to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

    # Ensure only features used during training are passed to the model
    required_columns = model.feature_names_in_
    df_features = df[required_columns]

    # Predict churn probabilities
    churn_probs = model.predict_proba(df_features)[:, 1]

    # Add predictions and categorize risk levels
    df["ChurnRiskScore"] = churn_probs
    df["RiskLevel"] = df["ChurnRiskScore"].apply(lambda x: "High" if x > 0.7 else "Medium" if x > 0.3 else "Low")

    return df
