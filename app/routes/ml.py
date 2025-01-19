from app.services.ml_service import train_churn_model_from_file,predict_churn_from_file
from typing import List
from fastapi import APIRouter, UploadFile, HTTPException
router = APIRouter()

# File path to the Telco dataset
FILE_PATH = "C:/Users/jemal/Downloads/archive1/WA_Fn-UseC_-Telco-Customer-Churn.csv"

@router.post("/train/")
async def train_model():
    """
    Train the churn prediction model using the Telco dataset from the file.
    """
    try:
        # Train the model using the Telco dataset file
        accuracy = train_churn_model_from_file(FILE_PATH)
        return {"message": "Model trained successfully", "accuracy": accuracy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during training: {str(e)}")


@router.post("/predict/file/")
async def predict_from_file(file: UploadFile):
    """
    Predict churn likelihood for Telco users from an uploaded CSV file.
    """
    try:
        # Save the uploaded file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Perform predictions from the file
        predictions_df = predict_churn_from_file(file_path)

        # Return the results as a JSON response
        return predictions_df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))