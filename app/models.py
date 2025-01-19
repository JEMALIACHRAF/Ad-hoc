from pydantic import BaseModel
from typing import Optional, Dict


class Score(BaseModel):
    user_id: int
    score_value: float
    segment: str
    timestamp: str

class AnalysisRequest(BaseModel):
    analysis_type: str
    parameters: Dict


class MLPipelineRequest(BaseModel):
    pipeline_name: str
    parameters: Dict
