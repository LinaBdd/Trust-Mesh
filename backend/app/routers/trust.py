"""Endpoints Trust DNA + logs pour le dashboard admin."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, TrustDNAModel, TrustScoreLog

router = APIRouter(prefix="/trust", tags=["trust"])


def _parse_user_id(user_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="user_id invalide (UUID attendu)")


@router.get("/dna/{user_id}")
async def get_trust_dna(user_id: str, db: AsyncSession = Depends(get_db)):
    uid = _parse_user_id(user_id)
    result = await db.execute(select(TrustDNAModel).where(TrustDNAModel.user_id == uid))
    dna = result.scalar_one_or_none()
    if not dna:
        raise HTTPException(status_code=404, detail="Trust DNA not found")
    return {
        "user_id": str(dna.user_id),
        "known_countries": dna.known_countries,
        "known_devices": dna.known_devices,
        "usual_login_hours": dna.usual_login_hours,
        "session_count": dna.session_count,
        "last_updated": dna.last_updated,
    }


@router.get("/logs/{user_id}")
async def get_logs(user_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    uid = _parse_user_id(user_id)
    result = await db.execute(
        select(TrustScoreLog)
        .where(TrustScoreLog.user_id == uid)
        .order_by(desc(TrustScoreLog.computed_at))
        .limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "session_id": log.session_id,
            "score": log.final_score,
            "risk_level": log.risk_level,
            "decision": log.decision,
            "explanation": log.explanation,
            "signals": log.signals,
            "computed_at": log.computed_at,
        }
        for log in logs
    ]