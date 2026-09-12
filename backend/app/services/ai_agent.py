"""
AI Agent Layer — orchestre intelligemment les APIs CAMARA.
Le LLM décide QUELS signaux collecter selon le contexte, puis explique la décision.
"""
import os
import json
import logging
from app.schemas.trust import TrustScoreResult

logger = logging.getLogger(__name__)

# --- LLM : utilise Groq (gratuit, rapide) ---
try:
    from groq import Groq
    _llm_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    _LLM_MODEL = "llama-3.3-70b-versatile"
    LLM_ENABLED = bool(os.getenv("GROQ_API_KEY"))
    if not LLM_ENABLED:
        logger.warning("GROQ_API_KEY manquant — AI Copilot désactivé")
except ImportError:
    LLM_ENABLED = False
    _llm_client = None
    logger.warning("Groq non installé — AI Copilot désactivé")


# ---------- 1. ORCHESTRATION INTELLIGENTE ----------

ORCHESTRATION_PROMPT = """Tu es un AI Agent de sécurité qui orchestre des APIs télécom CAMARA.
Contexte de la tentative de connexion :
{context}

APIs disponibles :
- sim_swap (détecte un remplacement récent de SIM) — CRITIQUE
- number_verification (vérifie que le numéro appartient bien à l'appareil) — CRITIQUE
- device_status (connectivité + roaming) — RECOMMANDÉ
- location_verification (pays réel vs déclaré) — RECOMMANDÉ

Retourne UNIQUEMENT un JSON de la forme :
{{"tools_to_call": ["sim_swap", "number_verification", ...], "reasoning": "explication courte"}}

Règles :
- Si c'est un nouvel appareil OU un nouveau pays → appelle TOUS les outils
- Si c'est un appareil et un pays connus → appelle sim_swap + number_verification uniquement
- Maximum 4 outils
"""


async def plan_orchestration(context: dict) -> dict:
    """Étape 2-4 du reasoning loop : Planning + Reasoning + Tool Selection."""
    if not LLM_ENABLED:
        # Fallback : règle déterministe
        tools = ["sim_swap", "number_verification"]
        if context.get("is_new_device") or context.get("is_new_country"):
            tools += ["device_status", "location_verification"]
        return {"tools_to_call": tools, "reasoning": "Fallback: règle déterministe"}

    try:
        prompt = ORCHESTRATION_PROMPT.format(context=json.dumps(context, indent=2))
        response = _llm_client.chat.completions.create(
            model=_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Erreur orchestration LLM: {e}")
        return {"tools_to_call": ["sim_swap", "number_verification"], "reasoning": "Fallback"}


# ---------- 2. EXPLICATION DE LA DÉCISION (AI Security Copilot) ----------

COPILOT_PROMPT = """Tu es l'AI Security Copilot de Trust Mesh.
Explique à un administrateur sécurité, en 3 phrases max, pourquoi cette tentative de connexion
a été classée "{risk}" et a reçu la décision "{decision}".

Détails :
- Utilisateur : {user_name}
- Score final : {score}/100
- Signaux détectés :
{signals}

Sois factuel, professionnel, style analyste SOC. Ne mentionne pas de données personnelles inventées.
"""


async def explain_decision(user_name: str, result: TrustScoreResult) -> str:
    """Génère l'explication en langage naturel (AI Security Copilot)."""
    if not LLM_ENABLED:
        return result.explanation or "Explication indisponible."

    signals_text = "\n".join(
        f"  • {s.name} : {s.score}/100 — {s.reason}" for s in result.signals
    )
    try:
        prompt = COPILOT_PROMPT.format(
            user_name=user_name,
            risk=result.risk_level.value,
            decision=result.decision.value,
            score=result.final_score,
            signals=signals_text,
        )
        response = _llm_client.chat.completions.create(
            model=_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erreur Copilot LLM: {e}")
        return result.explanation or "Explication indisponible."