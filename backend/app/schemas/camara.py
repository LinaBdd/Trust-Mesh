"""
Schémas représentant les réponses des APIs CAMARA (Open Gateway).
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NumberVerificationResult(BaseModel):
    phone_number: str
    verified: bool


class SimSwapResult(BaseModel):
    phone_number: str
    swapped: bool
    swapped_at: Optional[datetime] = None
    hours_since_swap: Optional[float] = None


class DeviceStatusResult(BaseModel):
    phone_number: str
    connectivity_status: str
    roaming: bool = False


class LocationVerificationResult(BaseModel):
    phone_number: str
    verified: bool
    country: Optional[str] = None
    matches_expected_area: Optional[bool] = None