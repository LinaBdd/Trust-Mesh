"""
Mock de l'API CAMARA Location Verification.
https://github.com/camaraproject/DeviceLocation
"""
from app.camara.base_client import BaseCamaraClient
from app.schemas.camara import LocationVerificationResult


class LocationVerificationClient(BaseCamaraClient):
    async def verify(self, phone_number: str, expected_country: str | None) -> LocationVerificationResult:
        scenario = self.get_scenario(phone_number)

        real_country = scenario.get("real_country", expected_country or "DZ")
        matches = (real_country == expected_country) if expected_country else None

        return LocationVerificationResult(
            phone_number=phone_number,
            verified=True,
            country=real_country,
            matches_expected_area=matches,
        )