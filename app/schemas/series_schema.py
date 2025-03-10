from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class SeriesData(BaseModel):
    labels: List[str]
    generated: List[float]
    ideal: List[float]
    error: List[float]

class SeriesRequest(BaseModel):
    type: str  # "sine", "cosine", "tangent", "custom"
    points: int
    avgError: float
    maxError: float
    data: SeriesData

class SeriesResponseh(SeriesRequest):
    id: str
    uid: str
    date: datetime
    
class SeriesResponse(BaseModel):
    type: str
    points: int
    avgError: float
    maxError: float
    minError: float
    stdError: float
    data: SeriesData
    
class SaveResultsRequest(BaseModel):
    uid: str  # 🔹 Ahora `uid` se espera en el body
    seriesId: str