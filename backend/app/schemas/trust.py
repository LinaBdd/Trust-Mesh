"""
Schémas cœur du moteur de confiance : Trust Score explicable.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DecisionAction(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_MFA = "REQUIRE_MFA"
    REQUIRE_ADMIN_APPROVAL = "REQUIRE_ADMIN_APPROVAL"
    BLOCK = "BLOCK"


class SignalScore(BaseModel):
    """Score individuel (0-100) pour un signal donné, avec justification."""
    name: str                  # "sim", "device", "location", "behaviour"
    score: float = Field(ge=0, le=100)
    weight: float
    reason: str

class TrustScoreResult(BaseModel):
    user_id: str
    session_id: str
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signals: List[SignalScore]
    final_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    decision: DecisionAction
    explanation: Optional[str] = None
    session_count: Optional[int] = None
    agent_reasoning: Optional[str] = None      # <-- ajouté
    tools_called: Optional[List[str]] = None   # <-- ajouté