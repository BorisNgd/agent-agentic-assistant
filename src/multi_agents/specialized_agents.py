"""
Agents Spécialisés pour le système Multi-Agents.

Chaque agent a un domaine d'expertise spécifique:
- HRAgent: Gestion des ressources humaines
- CalendarAgent: Gestion des calendriers et réunions
- EmailAgent: Communications et notifications
- PlanningAgent: Gestion des plannings d'équipe
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Optional, List, Dict
from enum import Enum

from ..common.mock_services import (
    HRService, CalendarService, EmailService, TeamService
)
from ..common.models import Priority
from ..common.logger import ActionLogger, setup_logger


class AgentStatus(Enum):
    """Statut d'exécution d'un agent."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class AgentTask:
    """Tâche assignée à un agent."""
    task_id: str
    description: str
    parameters: dict = field(default_factory=dict)
    priority: int = 1  # 1 = haute, 5 = basse
    dependencies: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """Résultat d'exécution d'un agent."""
    agent_name: str
    task_id: str
    status: AgentStatus
    result: Any = None
    error: Optional[str] = None
    actions_performed: list[str] = field(default_factory=list)
    artifacts: dict = field(default_factory=dict)


class SpecializedAgent(ABC):
    """
    Classe de base pour tous les agents spécialisés.

    Chaque agent spécialisé:
    - A un domaine d'expertise défini
    - Peut exécuter des tâches de son domaine
    - Peut communiquer avec d'autres agents via l'orchestrateur
    """

    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.status = AgentStatus.IDLE
        self.logger = ActionLogger(f"[{name}]", setup_logger())

    @abstractmethod
    def execute(self, task: AgentTask) -> AgentResult:
        """Exécute une tâche spécifique au domaine de l'agent."""
        pass

    @abstractmethod
    def can_handle(self, task_description: str) -> bool:
        """Vérifie si l'agent peut gérer ce type de tâche."""
        pass

    def _success_result(
        self,
        task: AgentTask,
        result: Any,
        actions: list[str],
        artifacts: dict = None
    ) -> AgentResult:
        """Crée un résultat de succès."""
        return AgentResult(
            agent_name=self.name,
            task_id=task.task_id,
            status=AgentStatus.SUCCESS,
            result=result,
            actions_performed=actions,
            artifacts=artifacts or {}
        )

    def _failure_result(self, task: AgentTask, error: str) -> AgentResult:
        """Crée un résultat d'échec."""
        return AgentResult(
            agent_name=self.name,
            task_id=task.task_id,
            status=AgentStatus.FAILED,
            error=error
        )


class HRAgent(SpecializedAgent):
    """
    Agent spécialisé dans les Ressources Humaines.

    Responsabilités:
    - Création et gestion des demandes de congé
    - Récupération des informations employés
    - Application des politiques RH
    """

    def __init__(self):
        super().__init__("HR-Agent", "Ressources Humaines")
        self.hr_service = HRService()

    def can_handle(self, task_description: str) -> bool:
        keywords = ["congé", "leave", "absence", "employé", "rh", "manager", "policy"]
        return any(kw in task_description.lower() for kw in keywords)

    def execute(self, task: AgentTask) -> AgentResult:
        self.status = AgentStatus.RUNNING
        self.logger.reasoning(f"Traitement tâche: {task.description}")

        try:
            action_type = task.parameters.get("action", "unknown")

            if action_type == "create_leave_request":
                return self._handle_leave_request(task)
            elif action_type == "get_employee_info":
                return self._handle_get_employee(task)
            elif action_type == "get_manager_info":
                return self._handle_get_manager(task)
            else:
                return self._failure_result(task, f"Action non supportée: {action_type}")

        except Exception as e:
            self.logger.error(f"Erreur: {e}")
            return self._failure_result(task, str(e))
        finally:
            self.status = AgentStatus.IDLE

    def _handle_leave_request(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("create_leave_request", params)

        request = self.hr_service.create_leave_request(
            employee_id=params["employee_id"],
            start_date=date.fromisoformat(params["start_date"]),
            end_date=date.fromisoformat(params["end_date"]),
            reason=params.get("reason", "Non spécifié"),
            priority=Priority.URGENT if params.get("is_urgent") else Priority.MEDIUM
        )

        self.logger.observation(f"Demande créée: {request.id}")

        return self._success_result(
            task,
            result={"request_id": request.id, "status": request.status.value},
            actions=["Demande de congé créée dans le système RH"],
            artifacts={"leave_request": request}
        )

    def _handle_get_employee(self, task: AgentTask) -> AgentResult:
        emp_id = task.parameters["employee_id"]
        self.logger.tool_call("get_employee", {"employee_id": emp_id})

        employee = self.hr_service.get_employee(emp_id)

        if employee:
            return self._success_result(
                task,
                result={"id": employee.id, "name": employee.name, "email": employee.email},
                actions=["Informations employé récupérées"]
            )
        return self._failure_result(task, f"Employé {emp_id} non trouvé")

    def _handle_get_manager(self, task: AgentTask) -> AgentResult:
        emp_id = task.parameters["employee_id"]
        self.logger.tool_call("get_manager", {"employee_id": emp_id})

        manager = self.hr_service.get_manager(emp_id)

        if manager:
            return self._success_result(
                task,
                result={"id": manager.id, "name": manager.name, "email": manager.email},
                actions=["Informations manager récupérées"]
            )
        return self._failure_result(task, f"Manager non trouvé pour {emp_id}")


class CalendarAgent(SpecializedAgent):
    """
    Agent spécialisé dans la gestion des calendriers.

    Responsabilités:
    - Vérification des conflits
    - Gestion des réunions
    - Analyse des disponibilités
    """

    def __init__(self):
        super().__init__("Calendar-Agent", "Calendrier")
        self.calendar_service = CalendarService()

    def can_handle(self, task_description: str) -> bool:
        keywords = ["calendrier", "réunion", "meeting", "conflit", "disponibilité"]
        return any(kw in task_description.lower() for kw in keywords)

    def execute(self, task: AgentTask) -> AgentResult:
        self.status = AgentStatus.RUNNING
        self.logger.reasoning(f"Traitement tâche: {task.description}")

        try:
            action_type = task.parameters.get("action", "unknown")

            if action_type == "check_conflicts":
                return self._handle_check_conflicts(task)
            elif action_type == "get_meeting":
                return self._handle_get_meeting(task)
            elif action_type == "update_attendee":
                return self._handle_update_attendee(task)
            else:
                return self._failure_result(task, f"Action non supportée: {action_type}")

        except Exception as e:
            self.logger.error(f"Erreur: {e}")
            return self._failure_result(task, str(e))
        finally:
            self.status = AgentStatus.IDLE

    def _handle_check_conflicts(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("check_conflicts", params)

        conflicts = self.calendar_service.check_conflicts(
            employee_id=params["employee_id"],
            start_date=date.fromisoformat(params["start_date"]),
            end_date=date.fromisoformat(params["end_date"])
        )

        self.logger.observation(f"{len(conflicts)} conflit(s) trouvé(s)")

        # Analyser les conflits critiques
        critical_conflicts = [c for c in conflicts if c.get("is_client_facing")]

        return self._success_result(
            task,
            result={
                "total_conflicts": len(conflicts),
                "critical_conflicts": len(critical_conflicts),
                "conflicts": conflicts
            },
            actions=["Calendrier analysé", f"{len(conflicts)} conflit(s) identifié(s)"],
            artifacts={"conflicts": conflicts, "critical": critical_conflicts}
        )

    def _handle_get_meeting(self, task: AgentTask) -> AgentResult:
        meeting_id = task.parameters["meeting_id"]
        self.logger.tool_call("get_meeting", {"meeting_id": meeting_id})

        meeting = self.calendar_service.get_meeting(meeting_id)

        if meeting:
            return self._success_result(
                task,
                result={
                    "id": meeting.id,
                    "title": meeting.title,
                    "is_client_facing": meeting.is_client_facing,
                    "required_skills": meeting.required_skills
                },
                actions=["Détails réunion récupérés"]
            )
        return self._failure_result(task, f"Réunion {meeting_id} non trouvée")

    def _handle_update_attendee(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("update_attendee", params)

        success = self.calendar_service.update_meeting_attendee(
            meeting_id=params["meeting_id"],
            old_attendee=params["old_attendee"],
            new_attendee=params["new_attendee"]
        )

        if success:
            return self._success_result(
                task,
                result={"updated": True},
                actions=[f"Participant mis à jour dans la réunion {params['meeting_id']}"]
            )
        return self._failure_result(task, "Échec mise à jour participant")


class EmailAgent(SpecializedAgent):
    """
    Agent spécialisé dans les communications.

    Responsabilités:
    - Envoi de notifications
    - Demandes d'approbation
    - Communications d'équipe
    """

    def __init__(self):
        super().__init__("Email-Agent", "Communications")
        self.email_service = EmailService()

    def can_handle(self, task_description: str) -> bool:
        keywords = ["email", "notification", "envoyer", "communiquer", "notifier"]
        return any(kw in task_description.lower() for kw in keywords)

    def execute(self, task: AgentTask) -> AgentResult:
        self.status = AgentStatus.RUNNING
        self.logger.reasoning(f"Traitement tâche: {task.description}")

        try:
            action_type = task.parameters.get("action", "unknown")

            if action_type == "send_notification":
                return self._handle_send_notification(task)
            elif action_type == "send_replacement_request":
                return self._handle_replacement_request(task)
            else:
                return self._failure_result(task, f"Action non supportée: {action_type}")

        except Exception as e:
            self.logger.error(f"Erreur: {e}")
            return self._failure_result(task, str(e))
        finally:
            self.status = AgentStatus.IDLE

    def _handle_send_notification(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("send_notification", params)

        notif = self.email_service.send_notification(
            recipient_id=params["recipient_id"],
            subject=params["subject"],
            body=params["body"]
        )

        self.logger.observation(f"Notification envoyée: {notif.id}")

        return self._success_result(
            task,
            result={"notification_id": notif.id, "sent_at": str(notif.sent_at)},
            actions=[f"Email envoyé à {params['recipient_id']}"]
        )

    def _handle_replacement_request(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("send_replacement_request", params)

        # Récupérer la réunion
        calendar = CalendarService()
        meeting = calendar.get_meeting(params["meeting_id"])

        if not meeting:
            return self._failure_result(task, "Réunion non trouvée")

        notif = self.email_service.send_replacement_request(
            original_employee_id=params["original_id"],
            replacement_employee_id=params["replacement_id"],
            meeting=meeting
        )

        return self._success_result(
            task,
            result={"notification_id": notif.id},
            actions=[f"Demande de remplacement envoyée pour {meeting.title}"]
        )


class PlanningAgent(SpecializedAgent):
    """
    Agent spécialisé dans la planification d'équipe.

    Responsabilités:
    - Recherche de remplaçants
    - Mise à jour des plannings
    - Analyse des compétences
    """

    def __init__(self):
        super().__init__("Planning-Agent", "Planning")
        self.team_service = TeamService()

    def can_handle(self, task_description: str) -> bool:
        keywords = ["planning", "remplaçant", "équipe", "disponible", "compétence"]
        return any(kw in task_description.lower() for kw in keywords)

    def execute(self, task: AgentTask) -> AgentResult:
        self.status = AgentStatus.RUNNING
        self.logger.reasoning(f"Traitement tâche: {task.description}")

        try:
            action_type = task.parameters.get("action", "unknown")

            if action_type == "find_replacement":
                return self._handle_find_replacement(task)
            elif action_type == "update_schedule":
                return self._handle_update_schedule(task)
            else:
                return self._failure_result(task, f"Action non supportée: {action_type}")

        except Exception as e:
            self.logger.error(f"Erreur: {e}")
            return self._failure_result(task, str(e))
        finally:
            self.status = AgentStatus.IDLE

    def _handle_find_replacement(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("find_replacement", params)

        candidates = self.team_service.find_available_replacement(
            target_date=date.fromisoformat(params["date"]),
            required_skills=params.get("required_skills", []),
            exclude_employee=params.get("exclude_employee")
        )

        self.logger.observation(f"{len(candidates)} candidat(s) trouvé(s)")

        if candidates:
            best = candidates[0]
            return self._success_result(
                task,
                result={
                    "best_candidate": best,
                    "all_candidates": candidates,
                    "total_found": len(candidates)
                },
                actions=[
                    f"Analyse des disponibilités effectuée",
                    f"Meilleur candidat: {best['employee_name']} ({best['compatibility_score']:.0f}%)"
                ],
                artifacts={"candidates": candidates}
            )

        return self._success_result(
            task,
            result={"best_candidate": None, "all_candidates": [], "total_found": 0},
            actions=["Aucun candidat disponible trouvé"]
        )

    def _handle_update_schedule(self, task: AgentTask) -> AgentResult:
        params = task.parameters
        self.logger.tool_call("update_schedule", params)

        schedule = self.team_service.update_team_schedule(
            date=date.fromisoformat(params["date"]),
            changes=params["changes"]
        )

        return self._success_result(
            task,
            result={"schedule_updated": True, "team_id": schedule.team_id},
            actions=["Planning d'équipe mis à jour"]
        )
