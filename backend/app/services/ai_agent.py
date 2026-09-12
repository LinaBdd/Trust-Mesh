"""
AI Agent Layer — orchestre intelligemment les APIs CAMARA via function-calling natif.
"""
import json
import logging
from app.config import get_settings
from app.schemas.trust import TrustScoreResult

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    from groq import Groq
    _llm_client = Groq(api_key=settings.groq_api_key)
    _LLM_MODEL = "llama-3.3-70b-versatile"
    LLM_ENABLED = bool(settings.groq_api_key)
    if not LLM_ENABLED:
        logger.warning("GROQ_API_KEY manquant — AI Copilot désactivé")
except ImportError:
    LLM_ENABLED = False
    _llm_client = None
    logger.warning("Groq non installé — AI Copilot désactivé")
# ---------- Définition des CAMARA APIs comme de vrais "tools" pour le LLM ----------

CAMARA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "sim_swap",
            "description": "Vérifie si un remplacement de carte SIM récent a été détecté sur ce numéro (signal CRITIQUE pour la fraude).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "device_status",
            "description": "Vérifie la connectivité et le statut de roaming de l'appareil.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "location_verification",
            "description": "Vérifie si le pays réel de l'utilisateur correspond au pays déclaré.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

ORCHESTRATION_SYSTEM_PROMPT = """Tu es un AI Agent de sécurité qui orchestre des APIs télécom CAMARA (SIM Swap, 
Device Status, Location Verification) pour détecter les fraudes lors de connexions.

Analyse le contexte de connexion fourni et appelle UNIQUEMENT les outils (tools) réellement nécessaires :
- Si l'appareil et le pays sont déjà connus → appelle seulement sim_swap.
- Si c'est un nouvel appareil OU un nouveau pays → appelle tous les outils disponibles.
- N'appelle jamais un outil qui n'apporte pas d'information utile dans ce contexte.
"""


async def plan_orchestration(context: dict) -> dict:
    """L'agent utilise le vrai function-calling pour décider quels signaux CAMARA appeler."""
    if not LLM_ENABLED:
        tools = ["sim_swap"]
        if context.get("is_new_device") or context.get("is_new_country"):
            tools += ["device_status", "location_verification"]
        return {"tools_to_call": tools, "reasoning": "Fallback: règle déterministe"}

    try:
        response = _llm_client.chat.completions.create(
            model=_LLM_MODEL,
            messages=[
                {"role": "system", "content": ORCHESTRATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Contexte de connexion :\n{json.dumps(context, indent=2)}"},
            ],
            tools=CAMARA_TOOLS,
            tool_choice="auto",
            temperature=0.1,
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls or []
        tools_to_call = [tc.function.name for tc in tool_calls]

        return {
            "tools_to_call": tools_to_call,
            "reasoning": message.content or "Sélection via function-calling natif",
        }
    except Exception as e:
        logger.error(f"Erreur orchestration LLM: {e}")
        return {"tools_to_call": ["sim_swap"], "reasoning": "Fallback après erreur"}


# ---------- 2. EXPLICATION DE LA DÉCISION (inchangé) ----------

COPILOT_PROMPT = """Tu es l'AI Security Copilot de Trust Mesh, un moteur de confiance adaptatif basé sur des signaux CAMARA (télécom).

Contexte de la tentative de connexion :
- Utilisateur : {user_name}
- Score final : {score}/100
- Risque : {risk} → Décision : {decision}
- Signaux détectés :
{signals}

Rédige une explication en 3 phrases MAXIMUM, destinée à un analyste sécurité (SOC), qui :
1. Résume la décision en une phrase factuelle (ne répète pas les scores bruts, ils sont déjà visibles).
2. Met en perspective le signal le plus déterminant.
3. Propose UNE recommandation concrète et actionnable pour l'analyste.

Ne mentionne jamais de données personnelles inventées. Reste factuel, concis, style analyste SOC senior.
"""


async def explain_decision(user_name: str, result: TrustScoreResult) -> str:
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