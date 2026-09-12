from app.camara.base_client import BaseCamaraClient
from app.camara.nokia_nac_client import NokiaNaCClient
from app.schemas.camara import NumberVerificationResult

nac = NokiaNaCClient()


class NumberVerificationClient(BaseCamaraClient):
    async def verify(self, phone_number: str) -> NumberVerificationResult:
        scenario = self.get_scenario(phone_number)
        if "number_verified" in scenario:
            return NumberVerificationResult(
                phone_number=phone_number,
                verified=scenario["number_verified"],
            )

        if nac.enabled:
            try:
                result = nac.client.number_verification.verify(
                    phone_number=phone_number,
                    hashed=False,
                )
                return NumberVerificationResult(
                    phone_number=phone_number,
                    verified=bool(result.device_phone_number_verified),
                )
            except Exception as e:
                print(f"[NaC NumberVerification error] {e}")

        return NumberVerificationResult(phone_number=phone_number, verified=True)