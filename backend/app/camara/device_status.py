"""
Mock de l'API CAMARA Device Status (connectivité + roaming).
https://github.com/camaraproject/DeviceStatus
"""
from app.camara.base_client import BaseCamaraClient
from app.schemas.camara import DeviceStatusResult


class DeviceStatusClient(BaseCamaraClient):
    async def check(self, phone_number: str) -> DeviceStatusResult:
        scenario = self.get_scenario(phone_number)

        return DeviceStatusResult(
            phone_number=phone_number,
            connectivity_status=scenario.get("connectivity_status", "CONNECTED_DATA"),
            roaming=scenario.get("roaming", False),
        )