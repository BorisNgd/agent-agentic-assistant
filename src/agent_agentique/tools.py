"""
Système d'outils (Tools) pour l'Agent Agentique.

Les outils permettent à l'agent d'AGIR sur les systèmes:
- Créer des demandes
- Envoyer des notifications
- Vérifier des calendriers
- etc.

C'est la différence fondamentale avec un chatbot classique.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, List, Dict
from datetime import date, timedelta

from ..common.mock_services import (
    HRService, CalendarService, EmailService, TeamService
)
from ..common.models import Priority


@dataclass
class Tool:
    """
    Représente un outil utilisable par l'agent.

    Un outil encapsule une capacité d'action:
    - name: Identifiant unique
    - description: Ce que l'outil fait (pour le raisonnement de l'agent)
    - function: La fonction à exécuter
    - parameters: Description des paramètres attendus
    """
    name: str
    description: str
    function: Callable
    parameters: dict = field(default_factory=dict)

    def execute(self, **kwargs) -> Any:
        """Exécute l'outil avec les paramètres fournis."""
        return self.function(**kwargs)


class ToolRegistry:
    """
    Registre de tous les outils disponibles pour l'agent.

    Cette classe gère:
    - L'enregistrement des outils
    - La recherche d'outils par nom
    - L'exécution sécurisée des outils
    """

    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self._hr_service = HRService()
        self._calendar_service = CalendarService()
        self._email_service = EmailService()
        self._team_service = TeamService()

        self._register_default_tools()

    def _register_default_tools(self):
        """Enregistre les outils par défaut."""

        # ======================
        # OUTILS RH
        # ======================
        self.register(Tool(
            name="create_leave_request",
            description="Crée une nouvelle demande de congé dans le système RH",
            function=self._create_leave_request,
            parameters={
                "employee_id": "ID de l'employé",
                "start_date": "Date de début (YYYY-MM-DD)",
                "end_date": "Date de fin (YYYY-MM-DD)",
                "reason": "Motif du congé",
                "is_urgent": "True si demande urgente"
            }
        ))

        self.register(Tool(
            name="get_leave_policy",
            description="Récupère les informations sur la politique de congés",
            function=self._get_leave_policy,
            parameters={}
        ))

        self.register(Tool(
            name="get_employee_info",
            description="Récupère les informations d'un employé",
            function=self._get_employee_info,
            parameters={"employee_id": "ID de l'employé"}
        ))

        self.register(Tool(
            name="get_manager_info",
            description="Récupère les informations du manager d'un employé",
            function=self._get_manager_info,
            parameters={"employee_id": "ID de l'employé"}
        ))

        # ======================
        # OUTILS CALENDRIER
        # ======================
        self.register(Tool(
            name="check_calendar_conflicts",
            description="Vérifie les conflits de calendrier pour une période",
            function=self._check_calendar_conflicts,
            parameters={
                "employee_id": "ID de l'employé",
                "start_date": "Date de début",
                "end_date": "Date de fin"
            }
        ))

        self.register(Tool(
            name="get_meeting_details",
            description="Récupère les détails d'une réunion",
            function=self._get_meeting_details,
            parameters={"meeting_id": "ID de la réunion"}
        ))

        self.register(Tool(
            name="update_meeting_attendee",
            description="Remplace un participant dans une réunion",
            function=self._update_meeting_attendee,
            parameters={
                "meeting_id": "ID de la réunion",
                "old_attendee": "ID du participant à remplacer",
                "new_attendee": "ID du nouveau participant"
            }
        ))

        # ======================
        # OUTILS EMAIL
        # ======================
        self.register(Tool(
            name="send_notification",
            description="Envoie une notification par email",
            function=self._send_notification,
            parameters={
                "recipient_id": "ID du destinataire",
                "subject": "Sujet du message",
                "body": "Corps du message"
            }
        ))

        self.register(Tool(
            name="send_leave_notification",
            description="Envoie une notification de demande de congé au manager",
            function=self._send_leave_notification,
            parameters={
                "request_id": "ID de la demande de congé",
                "manager_id": "ID du manager"
            }
        ))

        self.register(Tool(
            name="send_replacement_request",
            description="Envoie une demande de remplacement pour une réunion",
            function=self._send_replacement_request,
            parameters={
                "original_employee_id": "ID de l'employé absent",
                "replacement_employee_id": "ID du remplaçant proposé",
                "meeting_id": "ID de la réunion"
            }
        ))

        # ======================
        # OUTILS ÉQUIPE
        # ======================
        self.register(Tool(
            name="find_replacement",
            description="Trouve des remplaçants disponibles avec les compétences requises",
            function=self._find_replacement,
            parameters={
                "date": "Date pour le remplacement",
                "required_skills": "Liste des compétences requises",
                "exclude_employee": "ID de l'employé à exclure"
            }
        ))

        self.register(Tool(
            name="update_team_schedule",
            description="Met à jour le planning d'équipe",
            function=self._update_team_schedule,
            parameters={
                "date": "Date du planning",
                "changes": "Dictionnaire des changements"
            }
        ))

    def register(self, tool: Tool) -> None:
        """Enregistre un nouvel outil."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Récupère un outil par son nom."""
        return self.tools.get(name)

    def list_tools(self) -> list[dict]:
        """Liste tous les outils disponibles avec leurs descriptions."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]

    def execute(self, tool_name: str, **kwargs) -> dict:
        """
        Exécute un outil de manière sécurisée.

        Returns:
            Dictionnaire avec le résultat ou l'erreur
        """
        tool = self.get(tool_name)
        if not tool:
            return {"success": False, "error": f"Outil '{tool_name}' non trouvé"}

        try:
            result = tool.execute(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ======================
    # IMPLÉMENTATIONS DES OUTILS
    # ======================

    def _create_leave_request(
        self,
        employee_id: str,
        start_date: str,
        end_date: str,
        reason: str,
        is_urgent: bool = False
    ) -> dict:
        """Crée une demande de congé."""
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        priority = Priority.URGENT if is_urgent else Priority.MEDIUM

        request = self._hr_service.create_leave_request(
            employee_id=employee_id,
            start_date=start,
            end_date=end,
            reason=reason,
            priority=priority
        )

        return {
            "request_id": request.id,
            "status": request.status.value,
            "employee_id": request.employee_id,
            "period": f"{start_date} - {end_date}",
            "priority": priority.value
        }

    def _get_leave_policy(self) -> dict:
        """Récupère la politique de congés."""
        return self._hr_service.get_leave_policy_info()

    def _get_employee_info(self, employee_id: str) -> Optional[dict]:
        """Récupère les infos d'un employé."""
        emp = self._hr_service.get_employee(employee_id)
        if emp:
            return {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "department": emp.department,
                "skills": emp.skills
            }
        return None

    def _get_manager_info(self, employee_id: str) -> Optional[dict]:
        """Récupère les infos du manager."""
        manager = self._hr_service.get_manager(employee_id)
        if manager:
            return {
                "id": manager.id,
                "name": manager.name,
                "email": manager.email
            }
        return None

    def _check_calendar_conflicts(
        self,
        employee_id: str,
        start_date: str,
        end_date: str
    ) -> list[dict]:
        """Vérifie les conflits de calendrier."""
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        return self._calendar_service.check_conflicts(employee_id, start, end)

    def _get_meeting_details(self, meeting_id: str) -> Optional[dict]:
        """Récupère les détails d'une réunion."""
        meeting = self._calendar_service.get_meeting(meeting_id)
        if meeting:
            return {
                "id": meeting.id,
                "title": meeting.title,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat(),
                "location": meeting.location,
                "is_client_facing": meeting.is_client_facing,
                "required_skills": meeting.required_skills,
                "attendees": meeting.attendees
            }
        return None

    def _update_meeting_attendee(
        self,
        meeting_id: str,
        old_attendee: str,
        new_attendee: str
    ) -> bool:
        """Met à jour un participant de réunion."""
        return self._calendar_service.update_meeting_attendee(
            meeting_id, old_attendee, new_attendee
        )

    def _send_notification(
        self,
        recipient_id: str,
        subject: str,
        body: str
    ) -> dict:
        """Envoie une notification."""
        notif = self._email_service.send_notification(
            recipient_id, subject, body
        )
        return {
            "notification_id": notif.id,
            "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
            "recipient": recipient_id
        }

    def _send_leave_notification(
        self,
        request_id: str,
        manager_id: str
    ) -> dict:
        """Envoie une notification de congé."""
        request = self._hr_service.get_leave_request(request_id)
        if not request:
            raise ValueError(f"Demande {request_id} non trouvée")

        notif = self._email_service.send_leave_request_notification(
            request, manager_id
        )
        return {
            "notification_id": notif.id,
            "sent_at": notif.sent_at.isoformat() if notif.sent_at else None
        }

    def _send_replacement_request(
        self,
        original_employee_id: str,
        replacement_employee_id: str,
        meeting_id: str
    ) -> dict:
        """Envoie une demande de remplacement."""
        meeting = self._calendar_service.get_meeting(meeting_id)
        if not meeting:
            raise ValueError(f"Réunion {meeting_id} non trouvée")

        notif = self._email_service.send_replacement_request(
            original_employee_id, replacement_employee_id, meeting
        )
        return {
            "notification_id": notif.id,
            "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
            "replacement_candidate": replacement_employee_id
        }

    def _find_replacement(
        self,
        date: str,
        required_skills: list[str] = None,
        exclude_employee: str = None
    ) -> list[dict]:
        """Trouve des remplaçants disponibles."""
        target_date = date.fromisoformat(date) if isinstance(date, str) else date
        return self._team_service.find_available_replacement(
            target_date, required_skills, exclude_employee
        )

    def _update_team_schedule(
        self,
        date: str,
        changes: dict[str, str]
    ) -> dict:
        """Met à jour le planning d'équipe."""
        target_date = date.fromisoformat(date) if isinstance(date, str) else date
        schedule = self._team_service.update_team_schedule(target_date, changes)
        return {
            "team_id": schedule.team_id,
            "date": str(schedule.date),
            "assignments": schedule.assignments
        }
