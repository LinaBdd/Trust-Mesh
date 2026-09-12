"""
Trust Engine — calcule le Trust Score explicable à partir des signaux CAMARA
et du profil comportemental (Trust DNA) de l'utilisateur.

Pondération : 40% SIM + 20% Device + 20% Location + 20% Behaviour
"""
from app.camara import SimSwapClient, DeviceStatusClient, LocationVerificationClient
from app.models import TrustDNAModel
from app.schemas.trust import SignalScore, TrustScoreResult, RiskLevel, DecisionAction
from app.services.ai_agent import plan_orchestration, explain_decision

sim_swap_client = SimSwapClient()
device_status_client = DeviceStatusClient()
location_client = LocationVerificationClient()


class TrustEngine:
    """Calcule le Trust Score d'une tentative de connexion."""

    SIM_WEIGHT = 0.4
    DEVICE_WEIGHT = 0.2
    LOCATION_WEIGHT = 0.2
    BEHAVIOUR_WEIGHT = 0.2

    # ------------------------------------------------------------------
    # Signaux individuels
    # ------------------------------------------------------------------

    async def compute_sim_signal(self, phone_number: str) -> SignalScore:
        result = await sim_swap_client.check(phone_number)

        if not result.swapped:
            score, reason = 100.0, "Aucun SIM swap détecté"
        elif result.hours_since_swap is not None and result.hours_since_swap < 24:
            score = 10.0
            reason = f"SIM swap détecté il y a {result.hours_since_swap:.0f}h — risque élevé"
        elif result.hours_since_swap is not None and result.hours_since_swap < 72:
            score = 50.0
            reason = f"SIM swap détecté il y a {result.hours_since_swap:.0f}h — vigilance"
        else:
            score = 80.0
            reason = "SIM swap ancien, risque réduit"

        return SignalScore(name="sim", score=score, weight=self.SIM_WEIGHT, reason=reason)

    async def compute_device_signal(
        self,
        phone_number: str,
        device_id: str,
        trust_dna: TrustDNAModel | None,
    ) -> SignalScore:
        status = await device_status_client.check(phone_number)

        known_devices = trust_dna.known_devices if trust_dna else []
        is_known_device = device_id in known_devices

        if not status.connectivity_status.startswith("CONNECTED"):
            score, reason = 20.0, "Appareil non connecté au réseau opérateur — suspect"
        elif is_known_device and not status.roaming:
            score, reason = 100.0, "Appareil connu, pas de roaming"
        elif is_known_device and status.roaming:
            score, reason = 70.0, "Appareil connu mais en roaming"
        elif not is_known_device and not status.roaming:
            score, reason = 60.0, "Nouvel appareil, pas de roaming"
        else:
            score, reason = 30.0, "Nouvel appareil ET en roaming — cumul de risques"

        return SignalScore(name="device", score=score, weight=self.DEVICE_WEIGHT, reason=reason)

    async def compute_location_signal(
        self,
        phone_number: str,
        claimed_country: str | None,
        trust_dna: TrustDNAModel | None,
    ) -> SignalScore:
        result = await location_client.verify(phone_number, claimed_country)

        known_countries = trust_dna.known_countries if trust_dna else []

        if result.matches_expected_area is False:
            score = 15.0
            reason = (
                f"Pays déclaré ({claimed_country}) ne correspond pas "
                f"au pays réel ({result.country})"
            )
        elif result.country in known_countries:
            score, reason = 100.0, f"Connexion depuis un pays habituel ({result.country})"
        elif result.country:
            score = 55.0
            reason = f"Connexion depuis un nouveau pays ({result.country})"
        else:
            score, reason = 50.0, "Localisation non vérifiable"

        return SignalScore(
            name="location", score=score, weight=self.LOCATION_WEIGHT, reason=reason
        )

    def compute_behaviour_signal(
        self, login_hour: int, trust_dna: TrustDNAModel | None
    ) -> SignalScore:
        usual_hours = trust_dna.usual_login_hours if trust_dna else []

        if not usual_hours:
            score, reason = 70.0, "Pas encore d'historique comportemental — score neutre"
        elif login_hour in usual_hours or any(abs(login_hour - h) <= 2 for h in usual_hours):
            score, reason = 100.0, "Heure de connexion cohérente avec les habitudes"
        else:
            score, reason = 45.0, "Heure de connexion inhabituelle"

        return SignalScore(
            name="behaviour", score=score, weight=self.BEHAVIOUR_WEIGHT, reason=reason
        )

    # ------------------------------------------------------------------
    # Décision
    # ------------------------------------------------------------------

    @staticmethod
    def decide(final_score: float) -> tuple[RiskLevel, DecisionAction]:
        if final_score >= 70:
            return RiskLevel.LOW, DecisionAction.ALLOW
        elif final_score >= 40:
            return RiskLevel.MEDIUM, DecisionAction.REQUIRE_MFA
        elif final_score >= 20:
            return RiskLevel.HIGH, DecisionAction.REQUIRE_ADMIN_APPROVAL
        else:
            return RiskLevel.HIGH, DecisionAction.BLOCK

    # ------------------------------------------------------------------
    # Orchestration complète
    # ------------------------------------------------------------------

    async def compute(
        self,
        user_id: str,
        session_id: str,
        phone_number: str,
        device_id: str,
        claimed_country: str | None,
        login_hour: int,
        trust_dna: TrustDNAModel | None,
        user_name: str = "Utilisateur",
    ) -> TrustScoreResult:
        # 1. AI Agent orchestration — décide quels signaux collecter
        context = {
            "device_id": device_id,
            "claimed_country": claimed_country,
            "login_hour": login_hour,
            "is_new_device": device_id
            not in (trust_dna.known_devices if trust_dna else []),
            "is_new_country": claimed_country
            not in (trust_dna.known_countries if trust_dna else []),
        }
        plan = await plan_orchestration(context)
        agent_reasoning = plan.get("reasoning", "")
        tools_called = plan.get("tools_to_call", [])

        # 2. Collecte uniquement les signaux sélectionnés par l'agent
        signals: list[SignalScore] = []

        if "sim_swap" in plan["tools_to_call"]:
            signals.append(await self.compute_sim_signal(phone_number))
        if "device_status" in plan["tools_to_call"]:
            signals.append(
                await self.compute_device_signal(phone_number, device_id, trust_dna)
            )
        if "location_verification" in plan["tools_to_call"]:
            signals.append(
                await self.compute_location_signal(
                    phone_number, claimed_country, trust_dna
                )
            )
        # number_verification n'apporte pas de score ici (informatif uniquement)

        # 3. Toujours le signal comportemental (pas d'API externe)
        signals.append(self.compute_behaviour_signal(login_hour, trust_dna))

        # 4. Recalcul des poids normalisés (au cas où certains signaux sont absents)
        total_weight = sum(s.weight for s in signals)
        final_score = (
            sum(s.score * s.weight for s in signals) / total_weight
            if total_weight
            else 0.0
        )

        risk_level, decision = self.decide(final_score)

        # 5. Explication — fallback local puis enrichissement par le Copilot
        fallback_explanation = self._build_explanation(signals, risk_level, decision)
        partial_result = TrustScoreResult(
            user_id=user_id,
            session_id=session_id,
            signals=signals,
            final_score=round(final_score, 1),
            risk_level=risk_level,
            decision=decision,
            explanation=fallback_explanation,
            agent_reasoning=agent_reasoning,
            tools_called=tools_called,
        )

        explanation = await explain_decision(user_name, partial_result)

        # 6. Résultat final
    
        return TrustScoreResult(
          user_id=user_id,
          session_id=session_id,
          signals=signals,
          final_score=round(final_score, 1),
          risk_level=risk_level,
          decision=decision,
          explanation=explanation,
          agent_reasoning=agent_reasoning,
          tools_called=tools_called,
          session_count=trust_dna.session_count if trust_dna else 0,
      )

    # ------------------------------------------------------------------
    # Fallback local (si le LLM est indisponible)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_explanation(
        signals: list[SignalScore],
        risk_level: RiskLevel,
        decision: DecisionAction,
    ) -> str:
        """Génère une explication lisible — utilisée si le Copilot LLM échoue."""
        weak_signals = [s for s in signals if s.score < 60]

        recommendation = {
            DecisionAction.ALLOW: "Aucune action requise.",
            DecisionAction.REQUIRE_MFA: (
                "Recommandation : valider l'identité via un second facteur "
                "avant d'autoriser l'accès."
            ),
            DecisionAction.REQUIRE_ADMIN_APPROVAL: (
                "Recommandation : notifier un administrateur pour validation "
                "manuelle avant tout accès."
            ),
            DecisionAction.BLOCK: (
                "Recommandation : bloquer la session et notifier l'utilisateur "
                "via un canal de confiance (SMS/email vérifié)."
            ),
        }.get(decision, "")

        if weak_signals:
            weakest = min(weak_signals, key=lambda s: s.score)
            return (
                f"Risque {risk_level.value} → {decision.value}. "
                f"Le signal le plus préoccupant est « {weakest.name} » : "
                f"{weakest.reason}. {recommendation}"
            )
        return (
            f"Risque {risk_level.value} → {decision.value}. "
            f"Tous les signaux sont cohérents avec le profil habituel. "
            f"{recommendation}"
        )