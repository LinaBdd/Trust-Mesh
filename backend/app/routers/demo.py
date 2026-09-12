"""Endpoints de démonstration live pour le jury."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.camara.sim_swap import SimSwapClient
from app.camara.device_status import DeviceStatusClient
from app.camara.location_verification import LocationVerificationClient

router = APIRouter(prefix="/demo", tags=["demo"])
settings = get_settings()


def _ensure_demo_allowed():
    if settings.environment == "production":
        raise HTTPException(status_code=403, detail="Demo endpoints disabled in production")


class SimSwapScenario(BaseModel):
    phone_number: str
    hours_since_swap: float = 1.0
    real_country: str = "RU"
    device_id: str = "unknown-device"


@router.post("/trigger-sim-swap")
async def trigger_sim_swap(scenario: SimSwapScenario):
    """Déclenche un scénario SIM Swap pour la démo live."""
    _ensure_demo_allowed()
    SimSwapClient.force_scenario(
        scenario.phone_number,
        sim_swapped=True,
        hours_since_swap=scenario.hours_since_swap,
    )
    DeviceStatusClient.force_scenario(
        scenario.phone_number,
        connectivity_status="CONNECTED_DATA",
        roaming=True,
    )
    LocationVerificationClient.force_scenario(
        scenario.phone_number,
        real_country=scenario.real_country,
    )
    return {"status": "ok", "message": f"Scénario SIM Swap activé pour {scenario.phone_number}"}


@router.post("/reset")
async def reset_scenarios(phone_number: str):
    """Reset les scénarios après la démo."""
    _ensure_demo_allowed()
    SimSwapClient.clear_scenario(phone_number)
    DeviceStatusClient.clear_scenario(phone_number)
    LocationVerificationClient.clear_scenario(phone_number)
    return {"status": "ok", "message": f"Scénarios réinitialisés pour {phone_number}"}