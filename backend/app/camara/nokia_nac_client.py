"""
Client Nokia Network-as-Code (NaC) — wrapper bas niveau.
Utilise le SDK officiel: pip install network-as-code
Doc: https://networkascode.nokia.io
"""
import os
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Le SDK Nokia NaC
try:
    from network_as_code import NetworkAsCodeApi
    NAC_AVAILABLE = True
except ImportError:
    NAC_AVAILABLE = False
    logger.warning("SDK Nokia NaC non installé — fallback sur mocks")


class NokiaNaCClient:
    """Wrapper unique pour tous les appels Nokia NaC."""

    _instance: Optional["NokiaNaCClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self.api_key = os.getenv("NOKIA_NAC_API_KEY", "")
        self.rapidapi_host = os.getenv(
            "NOKIA_NAC_HOST", "network-as-code.nokia.rapidapi.com"
        )
        self.enabled = NAC_AVAILABLE and bool(self.api_key)

        if self.enabled:
            self.client = NetworkAsCodeApi(
                rapidapi_host=self.rapidapi_host,
                api_key=self.api_key,
            )
            logger.info("✅ Nokia NaC client initialisé")
        else:
            self.client = None
            logger.warning("⚠️ Nokia NaC désactivé — mode mock uniquement")