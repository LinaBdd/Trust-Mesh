"""
Endpoints d'authentification Trust Mesh.
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, TrustDNAModel, TrustScoreLog
from app.schemas.auth import LoginRequest, LoginDecisionResponse
from app.services import TrustEngine
from app.models.login_attempt import LoginAttempt

router = APIRouter(prefix="/auth", tags=["auth"])
trust_engine = TrustEngine()


@router.post("/login", response_model=LoginDecisionResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. Récupère ou crée l'utilisateur + son Trust DNA
    result = await db.execute(select(User).where(User.phone_number == payload.phone_number))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(phone_number=payload.phone_number)
        db.add(user)
        await db.flush()

        trust_dna = TrustDNAModel(user_id=user.id)
        db.add(trust_dna)
        await db.flush()
    else:
        dna_result = await db.execute(select(TrustDNAModel).where(TrustDNAModel.user_id == user.id))
        trust_dna = dna_result.scalar_one_or_none()
        if trust_dna is None:
            trust_dna = TrustDNAModel(user_id=user.id)
            db.add(trust_dna)
            await db.flush()

    session_id = str(uuid.uuid4())
    login_hour = payload.timestamp.hour

    # 2. Calcul réel du Trust Score via le Trust Engine + clients CAMARA mockés
    trust_score = await trust_engine.compute(
        user_id=str(user.id),
        session_id=session_id,
        phone_number=payload.phone_number,
        device_id=payload.device_id,
        claimed_country=payload.claimed_country,
        login_hour=login_hour,
        trust_dna=trust_dna,
    )

    # 3. Log en base
    log = TrustScoreLog(
        user_id=user.id,
        session_id=session_id,
        device_id=payload.device_id,
        ip_address=payload.ip_address,
        claimed_country=payload.claimed_country,
        final_score=trust_score.final_score,
        risk_level=trust_score.risk_level.value,
        decision=trust_score.decision.value,
        signals=[s.model_dump() for s in trust_score.signals],
        explanation=trust_score.explanation,
    )
    db.add(log)

    # 4. Met à jour le Trust DNA (apprentissage) — seulement si la décision est ALLOW,
    #    pour éviter d'apprendre un comportement frauduleux comme "normal".
    if trust_score.decision.value == "ALLOW":
        if payload.device_id not in trust_dna.known_devices:
            trust_dna.known_devices = [*trust_dna.known_devices, payload.device_id]
        if payload.claimed_country and payload.claimed_country not in trust_dna.known_countries:
            trust_dna.known_countries = [*trust_dna.known_countries, payload.claimed_country]
        if login_hour not in trust_dna.usual_login_hours:
            trust_dna.usual_login_hours = [*trust_dna.usual_login_hours, login_hour]
        trust_dna.session_count += 1

    attempt = LoginAttempt(
        user_id=user.id,
        session_id=session_id,
        device_id=payload.device_id,
        ip_address=payload.ip_address,
        claimed_country=payload.claimed_country,
    )
    db.add(attempt)
    await db.commit()

    return LoginDecisionResponse(
        user_id=str(user.id),
        session_id=session_id,
        trust_score=trust_score,
        message=f"Décision : {trust_score.decision.value} (score {trust_score.final_score}/100)",
    )