"""
Services simulés représentant les APIs d'entreprise.
Ces services imitent le comportement réel des systèmes RH, Calendrier, Email, etc.
"""
from __future__ import annotations
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from .models import (
    Employee, LeaveRequest, Meeting, CalendarEvent,
    Notification, TeamSchedule, LeaveStatus, Priority
)


# Base de données simulée
class MockDatabase:
    """Simule une base de données en mémoire."""

    employees: dict[str, Employee] = {
        "EMP001": Employee(
            id="EMP001",
            name="Thomas Bernard",
            email="thomas.bernard@company.com",
            department="IT",
            manager_id="MGR001",
            skills=["python", "cloud", "devops"]
        ),
        "EMP002": Employee(
            id="EMP002",
            name="Marie Dupont",
            email="marie.dupont@company.com",
            department="IT",
            manager_id="MGR001",
            skills=["python", "data", "client-facing"]
        ),
        "EMP003": Employee(
            id="EMP003",
            name="Pierre Martin",
            email="pierre.martin@company.com",
            department="IT",
            manager_id="MGR001",
            skills=["java", "cloud"]
        ),
        "MGR001": Employee(
            id="MGR001",
            name="Jean Martin",
            email="jean.martin@company.com",
            department="IT",
            manager_id=None,
            skills=["management", "architecture"]
        ),
    }

    leave_requests: dict[str, LeaveRequest] = {}
    meetings: dict[str, Meeting] = {}
    calendar_events: dict[str, list[CalendarEvent]] = {}
    notifications: list[Notification] = []


class HRService:
    """
    Service de gestion des Ressources Humaines.
    Gère les demandes de congé, les approbations, etc.
    """

    def __init__(self):
        self.db = MockDatabase

    def create_leave_request(
        self,
        employee_id: str,
        start_date: date,
        end_date: date,
        reason: str,
        priority: Priority = Priority.MEDIUM
    ) -> LeaveRequest:
        """
        Crée une nouvelle demande de congé.

        Args:
            employee_id: ID de l'employé
            start_date: Date de début du congé
            end_date: Date de fin du congé
            reason: Motif du congé
            priority: Priorité de la demande

        Returns:
            LeaveRequest: La demande créée
        """
        request_id = f"LR-{uuid.uuid4().hex[:8].upper()}"

        request = LeaveRequest(
            id=request_id,
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=LeaveStatus.PENDING,
            priority=priority
        )

        self.db.leave_requests[request_id] = request
        return request

    def get_leave_request(self, request_id: str) -> Optional[LeaveRequest]:
        """Récupère une demande de congé par son ID."""
        return self.db.leave_requests.get(request_id)

    def approve_leave(self, request_id: str, approver_role: str) -> bool:
        """
        Approuve une demande de congé.

        Args:
            request_id: ID de la demande
            approver_role: "manager" ou "hr"

        Returns:
            bool: True si l'approbation est réussie
        """
        request = self.get_leave_request(request_id)
        if not request:
            return False

        if approver_role == "manager":
            request.manager_approval = True
        elif approver_role == "hr":
            request.hr_approval = True

        if request.manager_approval:  # Simplified: manager approval enough
            request.status = LeaveStatus.APPROVED

        return True

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Récupère les informations d'un employé."""
        return self.db.employees.get(employee_id)

    def get_manager(self, employee_id: str) -> Optional[Employee]:
        """Récupère le manager d'un employé."""
        employee = self.get_employee(employee_id)
        if employee and employee.manager_id:
            return self.get_employee(employee.manager_id)
        return None

    def get_leave_policy_info(self) -> dict:
        """Retourne les informations sur la politique de congés."""
        return {
            "urgent_notice_days": 2,
            "standard_notice_days": 5,
            "max_consecutive_days": 20,
            "requires_manager_approval": True,
            "requires_hr_approval": False,
            "forms": {
                "standard": "HR-001",
                "urgent": "HR-001-URG"
            }
        }


class CalendarService:
    """
    Service de gestion du calendrier.
    Gère les événements, réunions et conflits.
    """

    def __init__(self):
        self.db = MockDatabase
        self._setup_mock_meetings()

    def _setup_mock_meetings(self):
        """Configure des réunions de test."""
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)

        client_meeting = Meeting(
            id="MTG001",
            title="Réunion Client - Projet Alpha",
            organizer_id="EMP001",
            attendees=["EMP001", "MGR001"],
            start_time=tomorrow.replace(hour=14, minute=0),
            end_time=tomorrow.replace(hour=15, minute=30),
            location="Salle A",
            is_client_facing=True,
            required_skills=["python", "client-facing"]
        )
        self.db.meetings["MTG001"] = client_meeting

        team_meeting = Meeting(
            id="MTG002",
            title="Stand-up Équipe",
            organizer_id="MGR001",
            attendees=["EMP001", "EMP002", "EMP003", "MGR001"],
            start_time=tomorrow.replace(hour=9, minute=30),
            end_time=tomorrow.replace(hour=10, minute=0),
            location="Teams",
            is_client_facing=False
        )
        self.db.meetings["MTG002"] = team_meeting

    def get_events_for_date(
        self,
        employee_id: str,
        target_date: date
    ) -> list[CalendarEvent]:
        """
        Récupère tous les événements d'un employé pour une date donnée.
        """
        events = []
        for meeting in self.db.meetings.values():
            if employee_id in meeting.attendees:
                if meeting.start_time.date() == target_date:
                    events.append(CalendarEvent(
                        id=meeting.id,
                        employee_id=employee_id,
                        title=meeting.title,
                        start_time=meeting.start_time,
                        end_time=meeting.end_time,
                        event_type="meeting",
                        details={
                            "is_client_facing": meeting.is_client_facing,
                            "required_skills": meeting.required_skills
                        }
                    ))
        return events

    def check_conflicts(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> list[dict]:
        """
        Vérifie les conflits de calendrier pour une période donnée.

        Returns:
            Liste des conflits détectés avec leurs détails
        """
        conflicts = []
        current = start_date

        while current <= end_date:
            events = self.get_events_for_date(employee_id, current)
            for event in events:
                conflicts.append({
                    "event_id": event.id,
                    "title": event.title,
                    "date": current,
                    "start_time": event.start_time,
                    "end_time": event.end_time,
                    "is_client_facing": event.details.get("is_client_facing", False),
                    "required_skills": event.details.get("required_skills", []),
                    "severity": "high" if event.details.get("is_client_facing") else "medium"
                })
            current += timedelta(days=1)

        return conflicts

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Récupère une réunion par son ID."""
        return self.db.meetings.get(meeting_id)

    def update_meeting_attendee(
        self,
        meeting_id: str,
        old_attendee: str,
        new_attendee: str
    ) -> bool:
        """Remplace un participant dans une réunion."""
        meeting = self.get_meeting(meeting_id)
        if meeting and old_attendee in meeting.attendees:
            meeting.attendees.remove(old_attendee)
            meeting.attendees.append(new_attendee)
            return True
        return False


class EmailService:
    """
    Service d'envoi de notifications.
    Gère l'envoi d'emails et autres notifications.
    """

    def __init__(self):
        self.db = MockDatabase
        self.sent_emails: list[dict] = []

    def send_notification(
        self,
        recipient_id: str,
        subject: str,
        body: str,
        notification_type: str = "email"
    ) -> Notification:
        """
        Envoie une notification à un utilisateur.

        Args:
            recipient_id: ID du destinataire
            subject: Sujet de la notification
            body: Corps du message
            notification_type: Type de notification (email, sms, push)

        Returns:
            Notification: La notification envoyée
        """
        notification = Notification(
            id=f"NOTIF-{uuid.uuid4().hex[:8].upper()}",
            recipient_id=recipient_id,
            subject=subject,
            body=body,
            notification_type=notification_type
        )
        notification.mark_as_sent()

        self.db.notifications.append(notification)
        self.sent_emails.append({
            "id": notification.id,
            "to": recipient_id,
            "subject": subject,
            "body": body,
            "sent_at": notification.sent_at
        })

        return notification

    def send_leave_request_notification(
        self,
        request: LeaveRequest,
        recipient_id: str
    ) -> Notification:
        """Envoie une notification pour une demande de congé."""
        employee = MockDatabase.employees.get(request.employee_id)
        emp_name = employee.name if employee else request.employee_id

        subject = f"[{request.priority.value.upper()}] Demande de congé - {emp_name}"
        body = f"""
Nouvelle demande de congé à approuver:

Employé: {emp_name}
Période: {request.start_date} - {request.end_date}
Motif: {request.reason}
Priorité: {request.priority.value}

Veuillez approuver ou rejeter cette demande.
        """.strip()

        return self.send_notification(recipient_id, subject, body)

    def send_replacement_request(
        self,
        original_employee_id: str,
        replacement_employee_id: str,
        meeting: Meeting
    ) -> Notification:
        """Envoie une demande de remplacement pour une réunion."""
        original = MockDatabase.employees.get(original_employee_id)
        replacement = MockDatabase.employees.get(replacement_employee_id)

        subject = f"Demande de remplacement - {meeting.title}"
        body = f"""
{original.name if original else original_employee_id} a besoin d'un remplacement pour:

Réunion: {meeting.title}
Date: {meeting.start_time.strftime("%d/%m/%Y")}
Heure: {meeting.start_time.strftime("%H:%M")} - {meeting.end_time.strftime("%H:%M")}
Lieu: {meeting.location or "Non spécifié"}

Pouvez-vous assurer ce remplacement?
        """.strip()

        return self.send_notification(replacement_employee_id, subject, body)

    def get_sent_notifications(self) -> list[dict]:
        """Retourne la liste des notifications envoyées."""
        return self.sent_emails.copy()


class TeamService:
    """
    Service de gestion d'équipe.
    Gère les disponibilités, compétences et planning.
    """

    def __init__(self):
        self.db = MockDatabase
        self.calendar_service = CalendarService()

    def find_available_replacement(
        self,
        target_date: date,
        required_skills: list[str] = None,
        exclude_employee: str = None
    ) -> list[dict]:
        """
        Trouve des remplaçants disponibles avec les compétences requises.

        Args:
            target_date: Date pour laquelle chercher un remplacement
            required_skills: Compétences nécessaires
            exclude_employee: Employé à exclure de la recherche

        Returns:
            Liste des candidats avec leur score de compatibilité
        """
        required_skills = required_skills or []
        candidates = []

        for emp_id, employee in self.db.employees.items():
            # Exclure l'employé demandeur et les managers
            if emp_id == exclude_employee or employee.manager_id is None:
                continue

            # Vérifier disponibilité (pas de conflits sur la date)
            conflicts = self.calendar_service.check_conflicts(
                emp_id, target_date, target_date
            )
            if conflicts:
                continue

            # Calculer le score de compétences
            if required_skills:
                matching_skills = set(employee.skills) & set(required_skills)
                skill_score = len(matching_skills) / len(required_skills) * 100
            else:
                skill_score = 100

            candidates.append({
                "employee_id": emp_id,
                "employee_name": employee.name,
                "email": employee.email,
                "skills": employee.skills,
                "matching_skills": list(set(employee.skills) & set(required_skills)),
                "compatibility_score": skill_score,
                "available": True
            })

        # Trier par score de compatibilité décroissant
        candidates.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return candidates

    def get_team_members(self, manager_id: str) -> list[Employee]:
        """Récupère tous les membres d'une équipe."""
        return [
            emp for emp in self.db.employees.values()
            if emp.manager_id == manager_id
        ]

    def update_team_schedule(
        self,
        date: date,
        changes: dict[str, str]
    ) -> TeamSchedule:
        """
        Met à jour le planning d'équipe.

        Args:
            date: Date du planning
            changes: Dictionnaire {employee_id: nouvelle_assignation}

        Returns:
            TeamSchedule: Le planning mis à jour
        """
        schedule = TeamSchedule(
            team_id="TEAM-IT",
            date=date
        )

        for emp_id, task in changes.items():
            schedule.assign(emp_id, task)

        return schedule
