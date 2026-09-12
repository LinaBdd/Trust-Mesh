"""
API CAMARA SIM Swap — intégration Nokia NaC avec fallback mock.
"""
from datetime import datetime, timedelta
from app.camara.base_client import BaseCamaraClient
from app.camara.nokia_nac_client import NokiaNaCClient
from app.schemas.camara import SimSwapResult

nac = NokiaNaCClient()


class SimSwapClient(BaseCamaraClient):
    async def check(self, phone_number: str) -> SimSwapResult:
        # 1. Scénario forcé (démo live) prioritaire
        scenario = self.get_scenario(phone_number)
        if scenario.get("sim_swapped") is not None:
            hours_ago = scenario.get("hours_since_swap", 1.0)
            return SimSwapResult(
                phone_number=phone_number,
                swapped=scenario["sim_swapped"],
                swapped_at=datetime.utcnow() - timedelta(hours=hours_ago) if scenario["sim_swapped"] else None,
                hours_since_swap=hours_ago if scenario["sim_swapped"] else None,
            )

        # 2. Appel réel Nokia NaC
        if nac.enabled:
            try:
                result = nac.client.sim_swap.check(
                    phone_number=phone_number,
                    max_age=24,
                )
                swapped = bool(result.swapped)
                hours_ago = None
                if swapped and getattr(result, "latest_sim_change", None):
                    delta = datetime.utcnow() - result.latest_sim_change
                    hours_ago = delta.total_seconds() / 3600
                return SimSwapResult(
                    phone_number=phone_number,
                    swapped=swapped,
                    swapped_at=getattr(result, "latest_sim_change", None),
                    hours_since_swap=hours_ago,
                )
            except Exception as e:
                # Log + fallback mock
                print(f"[NaC SIM Swap error] {e}")

        # 3. Fallback mock par défaut
        return SimSwapResult(phone_number=phone_number, swapped=False, hours_since_swap=None)