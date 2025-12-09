"""
Orchestrateur du système Multi-Agents.

L'orchestrateur est le cerveau du système:
- Analyse les demandes complexes
- Décompose en sous-tâches
- Distribue aux agents spécialisés
- Coordonne l'exécution (parallèle/séquentielle)
- Agrège les résultats
- Gère les erreurs et fallbacks
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, List, Dict
from enum import Enum
import uuid

from .specialized_agents import (
    SpecializedAgent, AgentTask, AgentResult, AgentStatus,
    HRAgent, CalendarAgent, EmailAgent, PlanningAgent
)
from ..common.logger import ActionLogger, setup_logger


class ExecutionMode(Enum):
    """Mode d'exécution des tâches."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass
class TaskPlan:
    """Plan d'exécution des tâches."""
    plan_id: str
    phases: list[list[AgentTask]]  # Chaque phase peut contenir plusieurs tâches parallèles
    current_phase: int = 0


@dataclass
class OrchestratorContext:
    """Contexte d'exécution de l'orchestrateur."""
    user_request: str
    employee_id: str = "EMP001"
    current_date: date = field(default_factory=date.today)


class Orchestrator:
    """
    Orchestrateur de système Multi-Agents.

    Caractéristiques clés (différences avec un agent simple):
    1. DÉCOMPOSITION: Analyse et découpe les tâches complexes
    2. SPÉCIALISATION: Route vers les agents experts
    3. PARALLÉLISME: Exécute les tâches indépendantes en parallèle
    4. COORDINATION: Gère les dépendances entre tâches
    5. RÉSILIENCE: Gère les échecs avec fallbacks

    Architecture:
    ```
    [Requête] -> [Analyse] -> [Planification] -> [Distribution] -> [Agrégation]
                                    |
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                [HR-Agent]   [Calendar-Agent]  [Planning-Agent]
                    │               │               │
                    └───────────────┴───────────────┘
                                    │
                            [Email-Agent]
    ```
    """

    def __init__(self):
        self.name = "Orchestrator"
        self.logger = ActionLogger(f"[{self.name}]", setup_logger())

        # Initialiser les agents spécialisés
        self.agents: dict[str, SpecializedAgent] = {
            "hr": HRAgent(),
            "calendar": CalendarAgent(),
            "email": EmailAgent(),
            "planning": PlanningAgent()
        }

        self.execution_history: list[dict] = []

    def process_request(self, context: OrchestratorContext) -> dict:
        """
        Traite une demande complexe via orchestration multi-agents.

        Args:
            context: Contexte de la requête

        Returns:
            Résultat agrégé de tous les agents
        """
        self.logger.reasoning(f"Nouvelle requête: {context.user_request}")

        # Phase 1: Analyse et planification
        self.logger.decision("Phase 1: Analyse de la demande")
        plan = self._create_execution_plan(context)

        # Phase 2: Exécution orchestrée
        self.logger.decision("Phase 2: Exécution du plan")
        results = self._execute_plan(plan, context)

        # Phase 3: Agrégation des résultats
        self.logger.decision("Phase 3: Agrégation des résultats")
        final_result = self._aggregate_results(results, context)

        return final_result

    def _create_execution_plan(self, context: OrchestratorContext) -> TaskPlan:
        """
        Crée un plan d'exécution avec les phases et dépendances.

        Le plan est structuré en phases:
        - Phase 1: Récupération des informations (parallèle)
        - Phase 2: Création demande + Vérification conflits (parallèle)
        - Phase 3: Recherche remplaçant (si nécessaire)
        - Phase 4: Notifications (parallèle)
        """
        tomorrow = context.current_date + timedelta(days=1)
        tomorrow_str = str(tomorrow)

        plan = TaskPlan(
            plan_id=f"PLAN-{uuid.uuid4().hex[:8]}",
            phases=[]
        )

        # PHASE 1: Récupération des informations (parallèle)
        phase1 = [
            AgentTask(
                task_id="T1-employee",
                description="Récupérer informations employé",
                parameters={
                    "action": "get_employee_info",
                    "employee_id": context.employee_id
                },
                priority=1
            ),
            AgentTask(
                task_id="T1-manager",
                description="Récupérer informations manager",
                parameters={
                    "action": "get_manager_info",
                    "employee_id": context.employee_id
                },
                priority=1
            )
        ]
        plan.phases.append(phase1)

        # PHASE 2: Actions principales (parallèle)
        phase2 = [
            AgentTask(
                task_id="T2-leave",
                description="Créer demande de congé",
                parameters={
                    "action": "create_leave_request",
                    "employee_id": context.employee_id,
                    "start_date": tomorrow_str,
                    "end_date": tomorrow_str,
                    "reason": "Urgence familiale",
                    "is_urgent": True
                },
                priority=1
            ),
            AgentTask(
                task_id="T2-conflicts",
                description="Vérifier conflits calendrier",
                parameters={
                    "action": "check_conflicts",
                    "employee_id": context.employee_id,
                    "start_date": tomorrow_str,
                    "end_date": tomorrow_str
                },
                priority=1
            )
        ]
        plan.phases.append(phase2)

        # PHASE 3: Recherche remplaçant (conditionnel, sera ajusté dynamiquement)
        phase3 = [
            AgentTask(
                task_id="T3-replacement",
                description="Trouver remplaçant disponible",
                parameters={
                    "action": "find_replacement",
                    "date": tomorrow_str,
                    "required_skills": [],  # Sera mis à jour
                    "exclude_employee": context.employee_id
                },
                priority=2
            )
        ]
        plan.phases.append(phase3)

        # PHASE 4: Notifications (sera construite dynamiquement)
        plan.phases.append([])  # Placeholder pour notifications

        self.logger.observation(f"Plan créé: {len(plan.phases)} phases")
        return plan

    def _execute_plan(
        self,
        plan: TaskPlan,
        context: OrchestratorContext
    ) -> dict[str, AgentResult]:
        """
        Exécute le plan phase par phase.

        Simule l'exécution parallèle au sein de chaque phase.
        """
        all_results: dict[str, AgentResult] = {}
        artifacts = {}

        for phase_idx, phase_tasks in enumerate(plan.phases):
            self.logger.reasoning(f"Exécution Phase {phase_idx + 1}/{len(plan.phases)}")

            # Ajustements dynamiques basés sur les résultats précédents
            if phase_idx == 2:  # Phase de recherche remplaçant
                phase_tasks = self._adjust_replacement_phase(phase_tasks, all_results, context)
            elif phase_idx == 3:  # Phase notifications
                phase_tasks = self._build_notification_phase(all_results, artifacts, context)

            if not phase_tasks:
                self.logger.observation(f"Phase {phase_idx + 1} ignorée (pas de tâches)")
                continue

            # Exécution "parallèle" des tâches de la phase
            phase_results = self._execute_phase(phase_tasks)

            # Collecter les résultats et artifacts
            for task_id, result in phase_results.items():
                all_results[task_id] = result
                if result.artifacts:
                    artifacts.update(result.artifacts)

            self.logger.observation(
                f"Phase {phase_idx + 1} terminée: "
                f"{sum(1 for r in phase_results.values() if r.status == AgentStatus.SUCCESS)}"
                f"/{len(phase_results)} succès"
            )

        return all_results

    def _execute_phase(self, tasks: list[AgentTask]) -> dict[str, AgentResult]:
        """
        Exécute toutes les tâches d'une phase.

        Dans un système réel, ceci serait parallélisé avec asyncio/threading.
        """
        results = {}

        for task in tasks:
            agent = self._route_task(task)
            if agent:
                self.logger.delegation(agent.name, task.description)
                result = agent.execute(task)
                results[task.task_id] = result

                status_icon = "[OK]" if result.status == AgentStatus.SUCCESS else "[ERR]"
                self.logger.observation(f"{status_icon} {agent.name}: {task.description}")
            else:
                results[task.task_id] = AgentResult(
                    agent_name="none",
                    task_id=task.task_id,
                    status=AgentStatus.FAILED,
                    error="Aucun agent disponible pour cette tâche"
                )

        return results

    def _route_task(self, task: AgentTask) -> Optional[SpecializedAgent]:
        """
        Route une tâche vers l'agent approprié.

        Utilise les mots-clés et le type d'action pour déterminer l'agent.
        """
        action = task.parameters.get("action", "")

        # Routage basé sur l'action
        if action in ["create_leave_request", "get_employee_info", "get_manager_info"]:
            return self.agents["hr"]
        elif action in ["check_conflicts", "get_meeting", "update_attendee"]:
            return self.agents["calendar"]
        elif action in ["send_notification", "send_replacement_request"]:
            return self.agents["email"]
        elif action in ["find_replacement", "update_schedule"]:
            return self.agents["planning"]

        # Fallback: chercher l'agent qui peut gérer la description
        for agent in self.agents.values():
            if agent.can_handle(task.description):
                return agent

        return None

    def _adjust_replacement_phase(
        self,
        tasks: list[AgentTask],
        results: dict[str, AgentResult],
        context: OrchestratorContext
    ) -> list[AgentTask]:
        """
        Ajuste la phase de recherche de remplaçant selon les conflits détectés.
        """
        conflicts_result = results.get("T2-conflicts")

        if not conflicts_result or conflicts_result.status != AgentStatus.SUCCESS:
            return []

        critical_conflicts = conflicts_result.artifacts.get("critical", [])

        if not critical_conflicts:
            self.logger.observation("Pas de conflit critique - pas de remplacement nécessaire")
            return []

        # Mettre à jour la tâche avec les compétences requises
        conflict = critical_conflicts[0]
        required_skills = conflict.get("required_skills", [])

        return [
            AgentTask(
                task_id="T3-replacement",
                description=f"Trouver remplaçant pour '{conflict['title']}'",
                parameters={
                    "action": "find_replacement",
                    "date": str(context.current_date + timedelta(days=1)),
                    "required_skills": required_skills,
                    "exclude_employee": context.employee_id
                },
                priority=1
            )
        ]

    def _build_notification_phase(
        self,
        results: dict[str, AgentResult],
        artifacts: dict,
        context: OrchestratorContext
    ) -> list[AgentTask]:
        """
        Construit dynamiquement la phase de notifications.
        """
        tasks = []

        # Notification au manager
        manager_result = results.get("T1-manager")
        leave_result = results.get("T2-leave")

        if (manager_result and manager_result.status == AgentStatus.SUCCESS
            and leave_result and leave_result.status == AgentStatus.SUCCESS):

            manager_id = manager_result.result.get("id")
            request_id = leave_result.result.get("request_id")

            tasks.append(AgentTask(
                task_id="T4-notify-manager",
                description="Notifier manager de la demande",
                parameters={
                    "action": "send_notification",
                    "recipient_id": manager_id,
                    "subject": f"[URGENT] Demande de congé - {request_id}",
                    "body": f"Une demande de congé urgente {request_id} requiert votre approbation."
                },
                priority=1
            ))

        # Notification de remplacement
        replacement_result = results.get("T3-replacement")
        conflicts_result = results.get("T2-conflicts")

        if (replacement_result and replacement_result.status == AgentStatus.SUCCESS
            and replacement_result.result.get("best_candidate")):

            candidate = replacement_result.result["best_candidate"]
            critical = conflicts_result.artifacts.get("critical", []) if conflicts_result else []

            if critical:
                tasks.append(AgentTask(
                    task_id="T4-notify-replacement",
                    description=f"Demander remplacement à {candidate['employee_name']}",
                    parameters={
                        "action": "send_replacement_request",
                        "original_id": context.employee_id,
                        "replacement_id": candidate["employee_id"],
                        "meeting_id": critical[0]["event_id"]
                    },
                    priority=1
                ))

        return tasks

    def _aggregate_results(
        self,
        results: dict[str, AgentResult],
        context: OrchestratorContext
    ) -> dict:
        """
        Agrège tous les résultats en un rapport cohérent.
        """
        # Collecter les informations
        all_actions = []
        notifications_sent = []
        errors = []

        for task_id, result in results.items():
            all_actions.extend(result.actions_performed)
            if result.status == AgentStatus.FAILED:
                errors.append(f"{result.agent_name}: {result.error}")

        # Extraire les données clés
        leave_result = results.get("T2-leave")
        conflicts_result = results.get("T2-conflicts")
        replacement_result = results.get("T3-replacement")
        manager_result = results.get("T1-manager")

        request_id = leave_result.result.get("request_id") if leave_result else None
        conflicts = conflicts_result.result.get("conflicts", []) if conflicts_result else []
        critical_count = conflicts_result.result.get("critical_conflicts", 0) if conflicts_result else 0
        replacement = replacement_result.result.get("best_candidate") if replacement_result else None
        manager_name = manager_result.result.get("name") if manager_result else "N/A"

        # Construire le message utilisateur
        user_message = self._build_user_message(
            request_id=request_id,
            manager_name=manager_name,
            conflicts=conflicts,
            critical_count=critical_count,
            replacement=replacement,
            results=results
        )

        return {
            "success": len(errors) == 0,
            "user_message": user_message,
            "actions_taken": all_actions,
            "agents_used": list(set(r.agent_name for r in results.values())),
            "tasks_executed": len(results),
            "tasks_successful": sum(1 for r in results.values() if r.status == AgentStatus.SUCCESS),
            "errors": errors,
            "execution_details": {
                task_id: {
                    "agent": result.agent_name,
                    "status": result.status.value,
                    "actions": result.actions_performed
                }
                for task_id, result in results.items()
            }
        }

    def _build_user_message(
        self,
        request_id: str,
        manager_name: str,
        conflicts: list,
        critical_count: int,
        replacement: Optional[dict],
        results: dict[str, AgentResult]
    ) -> str:
        """Construit le message final pour l'utilisateur."""

        msg = f"""
{'='*50}
 TRAITEMENT MULTI-AGENTS TERMINÉ
{'='*50}

Votre demande a été traitée par notre système multi-agents.

1. DEMANDE DE CONGÉ
   - Référence: {request_id or 'Non créée'}
   - Statut: En attente d'approbation
   - Approbateur: {manager_name}

2. ANALYSE DU CALENDRIER
   - Conflits détectés: {len(conflicts)}
   - Conflits critiques (clients): {critical_count}
"""

        if conflicts:
            msg += "\n   Détail des conflits:\n"
            for c in conflicts:
                severity = "[CRITIQUE]" if c.get("is_client_facing") else "[Standard]"
                msg += f"   - {severity} {c['title']}\n"

        if replacement:
            msg += f"""
3. REMPLACEMENT ORGANISÉ
   - Candidat sélectionné: {replacement['employee_name']}
   - Score de compatibilité: {replacement['compatibility_score']:.0f}%
   - Compétences matchées: {', '.join(replacement.get('matching_skills', []))}
   - Demande envoyée: Oui
"""
        elif critical_count > 0:
            msg += """
3. REMPLACEMENT
   - Aucun candidat disponible trouvé
   - Action requise: Contacter manuellement un collègue
"""

        # Compter les notifications
        notif_count = sum(
            1 for tid, r in results.items()
            if tid.startswith("T4") and r.status == AgentStatus.SUCCESS
        )

        msg += f"""
4. NOTIFICATIONS
   - {notif_count} notification(s) envoyée(s)
"""

        msg += """
{'='*50}
AGENTS IMPLIQUÉS:
- HR-Agent: Gestion de la demande de congé
- Calendar-Agent: Analyse des conflits
- Planning-Agent: Recherche de remplaçant
- Email-Agent: Envoi des notifications

Toutes les actions ont été exécutées automatiquement.
Je surveille les réponses et vous tiendrai informé.
{'='*50}
"""

        return msg.strip()

    def get_capabilities(self) -> dict:
        """Retourne les capacités du système multi-agents."""
        return {
            "name": "Système Multi-Agents",
            "type": "Orchestration d'agents spécialisés",
            "agents": [
                {"name": agent.name, "domain": agent.domain}
                for agent in self.agents.values()
            ],
            "capabilities": [
                "Décomposition de tâches complexes",
                "Routage intelligent vers agents spécialisés",
                "Exécution parallèle des tâches indépendantes",
                "Gestion des dépendances inter-tâches",
                "Agrégation des résultats",
                "Gestion des erreurs avec fallback",
                "Communication inter-agents"
            ],
            "pattern": "Orchestrator -> Specialized Agents -> Aggregation",
            "autonomy_level": "Très élevée (système auto-organisé)"
        }

    def demonstrate(self, user_message: str, employee_id: str = "EMP001") -> None:
        """
        Exécute une démonstration interactive avec affichage formaté.
        """
        print("\n" + "="*70)
        print("  DÉMONSTRATION: SYSTÈME MULTI-AGENTS")
        print("="*70)

        print(f"\n[Utilisateur]: {user_message}\n")

        print("-"*70)
        print("  ARCHITECTURE MULTI-AGENTS")
        print("-"*70)
        print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                    ORCHESTRATEUR                             │
    │            (Analyse, Planifie, Coordonne)                   │
    └─────────────────────┬───────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┬─────────────┐
            ▼             ▼             ▼             ▼
       ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
       │HR-Agent │  │Calendar │  │Planning │  │ Email   │
       │         │  │ Agent   │  │ Agent   │  │ Agent   │
       └─────────┘  └─────────┘  └─────────┘  └─────────┘
""")

        print("-"*70)
        print("  EXÉCUTION ORCHESTRÉE")
        print("-"*70 + "\n")

        context = OrchestratorContext(
            user_request=user_message,
            employee_id=employee_id
        )

        result = self.process_request(context)

        print("\n" + "-"*70)
        print("  RAPPORT CONSOLIDÉ")
        print("-"*70)
        print(result["user_message"])

        print("\n" + "-"*70)
        print("  ANALYSE DU COMPORTEMENT MULTI-AGENTS")
        print("-"*70)

        print(f"\n Tâches exécutées: {result['tasks_executed']}")
        print(f" Tâches réussies: {result['tasks_successful']}")
        print(f"\n Agents utilisés:")
        for agent in result["agents_used"]:
            print(f"    - {agent}")

        print("\n Actions par agent:")
        for task_id, details in result["execution_details"].items():
            status = "[OK]" if details["status"] == "success" else "[ERR]"
            print(f"    {status} {details['agent']}: {', '.join(details['actions']) or 'N/A'}")

        if result["errors"]:
            print("\n Erreurs rencontrées:")
            for error in result["errors"]:
                print(f"    - {error}")

        print("\n" + "="*70 + "\n")


def demo():
    """Fonction de démonstration standalone."""
    orchestrator = Orchestrator()

    scenario = (
        "Je dois m'absenter demain pour une urgence familiale. "
        "J'ai une réunion client importante à 14h et le planning d'équipe doit être mis à jour."
    )

    orchestrator.demonstrate(scenario)


if __name__ == "__main__":
    demo()
