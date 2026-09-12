"""
Schémas exposés par l'API Trust Mesh (entrée/sortie du endpoint d'authentification).
"""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.trust import TrustScoreResult


class LoginRequest(BaseModel):
    phone_number: str
    device_id: str
    ip_address: Optional[str] = None
    claimed_country: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LoginDecisionResponse(BaseModel):
    user_id: str
    session_id: str
    trust_score: TrustScoreResult
    message: str