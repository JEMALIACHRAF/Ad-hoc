from fastapi import FastAPI
from app.routes import scores, analyses, ml,programs,netflix

import sys
import os

# Ajouter le chemin du dossier parent à sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()

app.include_router(netflix.router, prefix="/api/netflix", tags=["Netflix"])

app.include_router(scores.router, prefix="/api", tags=["Scores"])
app.include_router(netflix.router, prefix="/api/netflix", tags=["Netflix"])
app.include_router(programs.router, prefix="/api/programs", tags=["Programs"])
app.include_router(analyses.router, prefix="/api", tags=["Analyses"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML Pipelines"])


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de gestion des données"}
