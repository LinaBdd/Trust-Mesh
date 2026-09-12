"""
Configuration centralisée — chargée depuis .env via pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Base de données ---
    database_url: str = "postgresql+asyncpg://trustmesh:trustmesh@localhost:5432/trustmesh"

    # --- App ---
    app_name: str = "Trust Mesh"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change_me_in_production"

    # --- Nokia Network-as-Code ---
    nokia_nac_api_key: str = ""
    nokia_nac_host: str = "network-as-code.nokia.rapidapi.com"

    # --- RapidAPI (optionnel) ---
    rapidapi: str = ""

    # --- LLM (AI Security Copilot) ---
    groq_api_key: str = ""

    # --- CORS ---
    cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",   # <-- ignore les variables non déclarées
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()