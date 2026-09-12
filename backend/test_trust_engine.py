"""Test rapide du Trust Engine — sans DB, sans FastAPI."""
import asyncio
from app.camara.sim_swap import SimSwapClient
from app.camara.device_status import DeviceStatusClient
from app.camara.location_verification import LocationVerificationClient
from app.services.trust_engine import TrustEngine


class FakeDNA:
    """Simule un Trust DNA existant pour les tests."""
    known_devices = ["device-abc"]
    known_countries = ["DZ"]
    usual_login_hours = [9, 10, 14, 15]
    known_sim_ids = []
    session_count = 5


async def test_normal_login():
    print("\n=== TEST 1 : Login normal ===")
    engine = TrustEngine()
    result = await engine.compute(
        user_id="user-1",
        session_id="session-1",
        phone_number="+213555000111",
        device_id="device-abc",
        claimed_country="DZ",
        login_hour=10,
        trust_dna=FakeDNA(),
        user_name="Ahmed",
    )
    print(f"Score: {result.final_score}/100")
    print(f"Risque: {result.risk_level.value}")
    print(f"Décision: {result.decision.value}")
    print(f"Explication: {result.explanation}")
    for s in result.signals:
        print(f"  - {s.name}: {s.score} ({s.reason})")
    assert result.final_score >= 70, "Devrait être LOW risk"
    print("TEST 1 PASSÉ")


async def test_sim_swap_attack():
    print("\n=== TEST 2 : Attaque SIM Swap ===")
    phone = "+213555000222"
    SimSwapClient.force_scenario(phone, sim_swapped=True, hours_since_swap=2.0)
    DeviceStatusClient.force_scenario(phone, roaming=True)
    LocationVerificationClient.force_scenario(phone, real_country="RU")

    engine = TrustEngine()
    result = await engine.compute(
        user_id="user-1",
        session_id="session-2",
        phone_number=phone,
        device_id="unknown-device",
        claimed_country="RU",
        login_hour=3,
        trust_dna=FakeDNA(),
        user_name="Ahmed",
    )
    print(f"Score: {result.final_score}/100")
    print(f"Risque: {result.risk_level.value}")
    print(f"Décision: {result.decision.value}")
    print(f"Explication: {result.explanation}")
    for s in result.signals:
        print(f"  - {s.name}: {s.score} ({s.reason})")
    assert result.final_score < 45, "Devrait être HIGH risk"
    print("TEST 2 PASSÉ")

    SimSwapClient.clear_scenario(phone)
    DeviceStatusClient.clear_scenario(phone)
    LocationVerificationClient.clear_scenario(phone)


async def main():
    await test_normal_login()
    await test_sim_swap_attack()
    print("\nTOUS LES TESTS PASSENT")


if __name__ == "__main__":
    asyncio.run(main())