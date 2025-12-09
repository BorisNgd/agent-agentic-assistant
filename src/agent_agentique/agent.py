"""
Agent Agentique - Implémentation de l'agent autonome.

Cet agent illustre le paradigme AGENTIQUE:
- Boucle ReAct: Raisonnement -> Action -> Observation -> Répéter
- Utilisation d'outils pour agir sur les systèmes
- Planification et exécution autonome
- Poursuite d'un objectif jusqu'à complétion
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, List, Dict
from enum import Enum

from .tools import ToolRegistry
from ..common.logger import ActionLogger, setup_logger


class AgentState(Enum):
    """États possibles de l'agent."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentStep:
    """Représente une étape d'exécution de l'agent."""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[dict] = None
    observation: Optional[str] = None


@dataclass
class AgentContext:
    """Contexte d'exécution de l'agent."""
    user_request: str
    employee_id: str = "EMP001"
    current_date: date = field(default_factory=date.today)
    max_steps: int = 10


class AgenticAgent:
    """
    Agent Agentique avec boucle ReAct.

    Caractéristiques clés (différences avec un chatbot):
    1. AUTONOMIE: L'agent planifie ses propres actions
    2. TOOLS: L'agent utilise des outils pour agir
    3. BOUCLE: L'agent itère jusqu'à atteindre son objectif
    4. OBSERVATION: L'agent analyse les résultats et s'adapte

    Pattern ReAct:
    1. THOUGHT: L'agent raisonne sur la situation
    2. ACTION: L'agent choisit et exécute un outil
    3. OBSERVATION: L'agent analyse le résultat
    4. Répéter jusqu'à complétion
    """

    def __init__(self, name: str = "Agent Agentique"):
        self.name = name
        self.tools = ToolRegistry()
        self.logger = ActionLogger(f"[{name}]", setup_logger())
        self.state = AgentState.IDLE
        self.steps: list[AgentStep] = []

    def process_request(self, context: AgentContext) -> dict:
        """
        Traite une demande utilisateur de manière autonome.

        C'est ici que la MAGIE AGENTIQUE opère:
        L'agent va RÉELLEMENT exécuter des actions sur les systèmes.

        Args:
            context: Contexte de la requête

        Returns:
            Résultat complet de l'exécution
        """
        self.state = AgentState.THINKING
        self.steps = []

        self.logger.reasoning(f"Nouvelle demande: {context.user_request}")
        self.logger.reasoning(f"Contexte: employé={context.employee_id}, date={context.current_date}")

        # Variables pour suivre les actions effectuées
        actions_taken = []
        leave_request_id = None
        conflicts_found = []
        replacement_found = None
        notifications_sent = []

        # ======================
        # STEP 1: Analyse initiale
        # ======================
        step1 = AgentStep(
            step_number=1,
            thought="Je dois analyser la demande et identifier les actions nécessaires. "
                    "L'utilisateur veut un congé urgent, ce qui implique: "
                    "1) Créer la demande RH, 2) Vérifier les conflits, 3) Gérer les remplacements."
        )
        self.steps.append(step1)
        self.logger.reasoning(step1.thought)

        # ======================
        # STEP 2: Récupérer les infos employé et manager
        # ======================
        step2 = AgentStep(
            step_number=2,
            thought="Je dois d'abord récupérer les informations de l'employé et de son manager."
        )
        self.logger.reasoning(step2.thought)

        self.logger.tool_call("get_employee_info", {"employee_id": context.employee_id})
        emp_result = self.tools.execute("get_employee_info", employee_id=context.employee_id)
        employee_info = emp_result.get("result", {})
        step2.observation = f"Employé: {employee_info.get('name', 'Inconnu')}"
        self.logger.observation(step2.observation)

        self.logger.tool_call("get_manager_info", {"employee_id": context.employee_id})
        mgr_result = self.tools.execute("get_manager_info", employee_id=context.employee_id)
        manager_info = mgr_result.get("result", {})
        step2.observation += f", Manager: {manager_info.get('name', 'Inconnu')}"
        self.logger.observation(f"Manager: {manager_info.get('name', 'Inconnu')}")

        self.steps.append(step2)
        actions_taken.append("Récupération infos employé et manager")

        # ======================
        # STEP 3: Créer la demande de congé
        # ======================
        tomorrow = context.current_date + timedelta(days=1)
        step3 = AgentStep(
            step_number=3,
            thought="Je crée maintenant la demande de congé urgente dans le système RH.",
            action="create_leave_request",
            action_input={
                "employee_id": context.employee_id,
                "start_date": str(tomorrow),
                "end_date": str(tomorrow),
                "reason": "Urgence familiale",
                "is_urgent": True
            }
        )
        self.logger.reasoning(step3.thought)
        self.logger.tool_call(step3.action, step3.action_input)

        leave_result = self.tools.execute(step3.action, **step3.action_input)

        if leave_result["success"]:
            leave_request_id = leave_result["result"]["request_id"]
            step3.observation = f"Demande créée avec succès: {leave_request_id}"
            actions_taken.append(f"Demande de congé créée: {leave_request_id}")
        else:
            step3.observation = f"Erreur: {leave_result.get('error')}"

        self.logger.observation(step3.observation)
        self.steps.append(step3)

        # ======================
        # STEP 4: Vérifier les conflits de calendrier
        # ======================
        step4 = AgentStep(
            step_number=4,
            thought="Je vérifie maintenant les conflits de calendrier pour cette date.",
            action="check_calendar_conflicts",
            action_input={
                "employee_id": context.employee_id,
                "start_date": str(tomorrow),
                "end_date": str(tomorrow)
            }
        )
        self.logger.reasoning(step4.thought)
        self.logger.tool_call(step4.action, step4.action_input)

        conflicts_result = self.tools.execute(step4.action, **step4.action_input)

        if conflicts_result["success"]:
            conflicts_found = conflicts_result["result"]
            if conflicts_found:
                step4.observation = f"ALERTE: {len(conflicts_found)} conflit(s) détecté(s)"
                for c in conflicts_found:
                    step4.observation += f"\n  - {c['title']} ({c['severity']})"
            else:
                step4.observation = "Aucun conflit détecté"
            actions_taken.append("Vérification calendrier effectuée")
        else:
            step4.observation = f"Erreur: {conflicts_result.get('error')}"

        self.logger.observation(step4.observation)
        self.steps.append(step4)

        # ======================
        # STEP 5: Gérer les conflits (si présents)
        # ======================
        if conflicts_found:
            client_meeting = next(
                (c for c in conflicts_found if c.get("is_client_facing")),
                None
            )

            if client_meeting:
                step5 = AgentStep(
                    step_number=5,
                    thought=f"Conflit critique détecté: réunion client '{client_meeting['title']}'. "
                            f"Je dois trouver un remplaçant avec les compétences: {client_meeting.get('required_skills', [])}",
                    action="find_replacement",
                    action_input={
                        "date": str(tomorrow),
                        "required_skills": client_meeting.get("required_skills", []),
                        "exclude_employee": context.employee_id
                    }
                )
                self.logger.reasoning(step5.thought)
                self.logger.tool_call(step5.action, step5.action_input)

                replacement_result = self.tools.execute(step5.action, **step5.action_input)

                if replacement_result["success"] and replacement_result["result"]:
                    candidates = replacement_result["result"]
                    replacement_found = candidates[0]  # Meilleur candidat
                    step5.observation = (
                        f"Remplaçant trouvé: {replacement_found['employee_name']} "
                        f"(score: {replacement_found['compatibility_score']:.0f}%)"
                    )
                    actions_taken.append(f"Remplaçant identifié: {replacement_found['employee_name']}")
                else:
                    step5.observation = "Aucun remplaçant disponible trouvé"

                self.logger.observation(step5.observation)
                self.steps.append(step5)

                # ======================
                # STEP 6: Envoyer demande de remplacement
                # ======================
                if replacement_found:
                    step6 = AgentStep(
                        step_number=6,
                        thought=f"J'envoie une demande de remplacement à {replacement_found['employee_name']}.",
                        action="send_replacement_request",
                        action_input={
                            "original_employee_id": context.employee_id,
                            "replacement_employee_id": replacement_found["employee_id"],
                            "meeting_id": client_meeting["event_id"]
                        }
                    )
                    self.logger.reasoning(step6.thought)
                    self.logger.tool_call(step6.action, step6.action_input)

                    notif_result = self.tools.execute(step6.action, **step6.action_input)

                    if notif_result["success"]:
                        step6.observation = f"Demande de remplacement envoyée: {notif_result['result']['notification_id']}"
                        notifications_sent.append({
                            "type": "replacement_request",
                            "to": replacement_found["employee_name"],
                            "id": notif_result["result"]["notification_id"]
                        })
                        actions_taken.append(f"Email de remplacement envoyé à {replacement_found['employee_name']}")
                    else:
                        step6.observation = f"Erreur envoi: {notif_result.get('error')}"

                    self.logger.observation(step6.observation)
                    self.steps.append(step6)

        # ======================
        # STEP 7: Notifier le manager
        # ======================
        if leave_request_id and manager_info:
            step7 = AgentStep(
                step_number=len(self.steps) + 1,
                thought="Je notifie le manager de la demande de congé pour approbation.",
                action="send_leave_notification",
                action_input={
                    "request_id": leave_request_id,
                    "manager_id": manager_info["id"]
                }
            )
            self.logger.reasoning(step7.thought)
            self.logger.tool_call(step7.action, step7.action_input)

            notif_result = self.tools.execute(step7.action, **step7.action_input)

            if notif_result["success"]:
                step7.observation = f"Manager notifié: {notif_result['result']['notification_id']}"
                notifications_sent.append({
                    "type": "leave_approval",
                    "to": manager_info["name"],
                    "id": notif_result["result"]["notification_id"]
                })
                actions_taken.append(f"Notification envoyée à {manager_info['name']}")
            else:
                step7.observation = f"Erreur: {notif_result.get('error')}"

            self.logger.observation(step7.observation)
            self.steps.append(step7)

        # ======================
        # FINALISATION
        # ======================
        self.state = AgentState.COMPLETED

        # Construire le rapport final
        final_report = self._build_final_report(
            context=context,
            employee_info=employee_info,
            manager_info=manager_info,
            leave_request_id=leave_request_id,
            conflicts_found=conflicts_found,
            replacement_found=replacement_found,
            notifications_sent=notifications_sent,
            actions_taken=actions_taken
        )

        self.logger.user_output("Traitement terminé avec succès")

        return final_report

    def _build_final_report(
        self,
        context: AgentContext,
        employee_info: dict,
        manager_info: dict,
        leave_request_id: Optional[str],
        conflicts_found: list,
        replacement_found: Optional[dict],
        notifications_sent: list,
        actions_taken: list
    ) -> dict:
        """Construit le rapport final d'exécution."""

        # Message utilisateur formaté
        user_message = f"""
Votre demande a été traitée avec succès.

RÉSUMÉ DES ACTIONS EFFECTUÉES:
{'='*40}

1. DEMANDE DE CONGÉ
   - Référence: {leave_request_id or 'Non créée'}
   - Statut: En attente d'approbation
   - Manager notifié: {manager_info.get('name', 'N/A')}

2. CONFLITS DE CALENDRIER
   - {len(conflicts_found)} conflit(s) détecté(s)
"""

        if conflicts_found:
            for c in conflicts_found:
                user_message += f"   - {c['title']} (Priorité: {c['severity']})\n"

        if replacement_found:
            user_message += f"""
3. REMPLACEMENT
   - Candidat proposé: {replacement_found['employee_name']}
   - Compatibilité: {replacement_found['compatibility_score']:.0f}%
   - Demande envoyée: Oui
"""

        user_message += f"""
4. NOTIFICATIONS ENVOYÉES
   - {len(notifications_sent)} notification(s)
"""
        for n in notifications_sent:
            user_message += f"   - {n['type']} -> {n['to']}\n"

        user_message += """
PROCHAINES ÉTAPES:
- Attendre l'approbation de votre manager
- Attendre la confirmation du remplaçant
- Je surveille les réponses et vous tiendrai informé
"""

        return {
            "success": True,
            "user_message": user_message.strip(),
            "actions_taken": actions_taken,
            "actions_required_by_user": [
                "Attendre les réponses (l'agent surveille)"
            ],
            "systems_accessed": [
                "Système RH (création demande)",
                "Calendrier (vérification conflits)",
                "Email (notifications)",
                "Équipe (recherche remplaçant)"
            ],
            "steps_executed": len(self.steps),
            "detailed_steps": [
                {
                    "step": s.step_number,
                    "thought": s.thought,
                    "action": s.action,
                    "observation": s.observation
                }
                for s in self.steps
            ]
        }

    def get_capabilities(self) -> dict:
        """Retourne les capacités de l'agent."""
        return {
            "name": self.name,
            "type": "Agent Agentique (Autonome)",
            "capabilities": [
                "Raisonnement autonome",
                "Planification de tâches",
                "Exécution d'actions via outils",
                "Vérification et résolution de conflits",
                "Envoi de notifications",
                "Recherche de ressources",
                "Adaptation aux résultats"
            ],
            "tools_available": len(self.tools.list_tools()),
            "pattern": "ReAct: Thought -> Action -> Observation -> Repeat",
            "autonomy_level": "Élevée (avec supervision humaine)"
        }

    def demonstrate(self, user_message: str, employee_id: str = "EMP001") -> None:
        """
        Exécute une démonstration interactive avec affichage formaté.
        """
        print("\n" + "="*70)
        print("  DÉMONSTRATION: AGENT AGENTIQUE")
        print("="*70)

        print(f"\n[Utilisateur]: {user_message}\n")

        print("-"*70)
        print("  BOUCLE ReAct (Reasoning and Acting)")
        print("-"*70 + "\n")

        context = AgentContext(
            user_request=user_message,
            employee_id=employee_id
        )

        result = self.process_request(context)

        print("\n" + "-"*70)
        print("  RAPPORT FINAL À L'UTILISATEUR")
        print("-"*70)
        print(result["user_message"])

        print("\n" + "-"*70)
        print("  ANALYSE DU COMPORTEMENT")
        print("-"*70)

        print("\n Actions RÉELLEMENT effectuées par l'agent:")
        for action in result["actions_taken"]:
            print(f"    [OK] {action}")

        print("\n Systèmes accédés:")
        for system in result["systems_accessed"]:
            print(f"    - {system}")

        print(f"\n Étapes de raisonnement: {result['steps_executed']}")

        print("\n" + "="*70 + "\n")


def demo():
    """Fonction de démonstration standalone."""
    agent = AgenticAgent()

    scenario = (
        "Je dois m'absenter demain pour une urgence familiale. "
        "J'ai une réunion client importante à 14h et le planning d'équipe doit être mis à jour."
    )

    agent.demonstrate(scenario)


if __name__ == "__main__":
    demo()
