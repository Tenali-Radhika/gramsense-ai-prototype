from datetime import date, datetime
from typing import List, Optional, Any

from pydantic import BaseModel


class Location(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None


class PriceData(BaseModel):
    crop: str
    market: str
    location: Location
    price: float
    unit: str
    timestamp: datetime
    source: str
    quality: str  # 'A' | 'B' | 'C'


class PricePrediction(BaseModel):
    date: date
    price: float
    confidence: Optional[float]


class ForecastFactor(BaseModel):
    name: str
    impact: float
    description: Optional[str]


class Forecast(BaseModel):
    crop: str
    location: Location
    predictions: List[PricePrediction]
    confidenceLevel: float
    methodology: str
    factors: List[ForecastFactor]
    generatedAt: datetime
    validUntil: datetime


class Recommendation(BaseModel):
    type: str  # 'SELL_NOW' | 'WAIT' | 'CHANGE_MARKET' | 'PLAN_CROP' | 'MONITOR'
    priority: str  # 'HIGH' | 'MEDIUM' | 'LOW'
    explanation: str
    supportingData: Any = None
    confidence: float = 0.0
    validityPeriod: Optional[Any] = None
    disclaimers: List[str] = []


class UserContext(BaseModel):
    userId: str
    location: Location
    preferredCrops: List[str]
    language: str
    literacyLevel: str  # 'LOW' | 'MEDIUM' | 'HIGH'
    deviceCapabilities: Optional[Any]
