from fastapi import FastAPI
from app.routes import scores, analyses, ml,programs,Telco

import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to terminal
        logging.FileHandler("app.log")  # Save to app.log
    ]
)


# Ajouter le chemin du dossier parent à sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()

app.include_router(Telco.router, prefix="/api/Telco", tags=["Telco"])

app.include_router(scores.router, prefix="/api", tags=["Scores"])
app.include_router(Telco.router, prefix="/api/Telco", tags=["Telco"])
app.include_router(programs.router, prefix="/api/programs", tags=["Programs"])
app.include_router(analyses.router, prefix="/api", tags=["Analyses"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML Pipelines"])


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de gestion des données"}
