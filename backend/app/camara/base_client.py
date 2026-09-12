"""
Interface commune pour tous les clients CAMARA.
En mode mock, simule des réponses réalistes sans appeler de vraie API opérateur.
Le jour où les vraies sandbox CAMARA sont disponibles, on remplace juste
l'implémentation interne — la signature reste identique.
"""
import random
from abc import ABC


class BaseCamaraClient(ABC):
    """Base commune : permet d'activer un scénario de simulation par numéro."""

    # Registre en mémoire des scénarios forcés pour la démo (phone_number -> scénario)
    _forced_scenarios: dict[str, dict] = {}

    @classmethod
    def force_scenario(cls, phone_number: str, **kwargs):
        """Force un scénario spécifique pour un numéro (utilisé pour la démo live SIM Swap)."""
        cls._forced_scenarios.setdefault(phone_number, {}).update(kwargs)

    @classmethod
    def clear_scenario(cls, phone_number: str):
        cls._forced_scenarios.pop(phone_number, None)

    @classmethod
    def get_scenario(cls, phone_number: str) -> dict:
        return cls._forced_scenarios.get(phone_number, {})