"""
Script de préparation démo — crée un utilisateur avec un historique mature
(plusieurs connexions légitimes) pour un contraste fort avant/après attaque.

À lancer une fois avant la présentation :
    cd backend
    python seed_demo_user.py
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models import User, TrustDNAModel
from sqlalchemy import select

DEMO_PHONE = "+213555000111"
DEMO_DEVICE = "device-abc"
DEMO_COUNTRY = "DZ"
DEMO_HOURS = [9, 10, 14, 15, 16]  # heures de connexion habituelles


async def seed():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.phone_number == DEMO_PHONE))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(phone_number=DEMO_PHONE, full_name="Ahmed Benali")
            db.add(user)
            await db.flush()
            print(f"✅ Utilisateur créé : {user.id}")
        else:
            print(f"ℹ️ Utilisateur existant : {user.id}")

        dna_result = await db.execute(
            select(TrustDNAModel).where(TrustDNAModel.user_id == user.id)
        )
        dna = dna_result.scalar_one_or_none()

        if dna is None:
            dna = TrustDNAModel(user_id=user.id)
            db.add(dna)

        dna.known_devices = [DEMO_DEVICE]
        dna.known_countries = [DEMO_COUNTRY]
        dna.usual_login_hours = DEMO_HOURS
        dna.session_count = 12  # historique "mature"

        await db.commit()
        print(f"✅ Trust DNA préparé — user_id={user.id}")
        print(f"   Garde ce user_id pour le dashboard admin pendant la démo !")


if __name__ == "__main__":
    asyncio.run(seed())