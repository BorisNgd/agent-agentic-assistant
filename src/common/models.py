"""
Modèles de données pour le système de gestion des demandes.
Ces modèles représentent les entités métier du scénario.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict


class LeaveStatus(Enum):
    """Statuts possibles d'une demande de congé."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Niveaux de priorité."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Employee:
    """Représente un employé dans le système."""
    id: str
    name: str
    email: str
    department: str
    manager_id: Optional[str] = None
    skills: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({self.department})"


@dataclass
class LeaveRequest:
    """Demande de congé d'un employé."""
    id: str
    employee_id: str
    start_date: date
    end_date: date
    reason: str
    status: LeaveStatus = LeaveStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    manager_approval: Optional[bool] = None
    hr_approval: Optional[bool] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_urgent(self) -> bool:
        """Vérifie si la demande est urgente (moins de 48h)."""
        days_until = (self.start_date - date.today()).days
        return days_until <= 2

    def approve(self, by_manager: bool = False, by_hr: bool = False) -> None:
        """Approuve la demande."""
        if by_manager:
            self.manager_approval = True
        if by_hr:
            self.hr_approval = True
        if self.manager_approval and self.hr_approval:
            self.status = LeaveStatus.APPROVED


@dataclass
class Meeting:
    """Représente une réunion."""
    id: str
    title: str
    organizer_id: str
    attendees: list[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_client_facing: bool = False
    required_skills: list[str] = field(default_factory=list)

    @property
    def duration_minutes(self) -> int:
        """Durée de la réunion en minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


@dataclass
class CalendarEvent:
    """Événement générique du calendrier."""
    id: str
    employee_id: str
    title: str
    start_time: datetime
    end_time: datetime
    event_type: str  # "meeting", "leave", "training", etc.
    details: dict = field(default_factory=dict)


@dataclass
class Notification:
    """Notification envoyée aux utilisateurs."""
    id: str
    recipient_id: str
    subject: str
    body: str
    sent_at: Optional[datetime] = None
    read: bool = False
    notification_type: str = "email"  # "email", "sms", "push"

    def mark_as_sent(self) -> None:
        """Marque la notification comme envoyée."""
        self.sent_at = datetime.now()


@dataclass
class TeamSchedule:
    """Planning d'équipe."""
    team_id: str
    date: date
    assignments: dict[str, str] = field(default_factory=dict)  # employee_id -> task

    def assign(self, employee_id: str, task: str) -> None:
        """Assigne une tâche à un employé."""
        self.assignments[employee_id] = task

    def get_available(self, exclude: list[str] = None) -> list[str]:
        """Retourne les employés non assignés."""
        exclude = exclude or []
        return [
            emp_id for emp_id in self.assignments.keys()
            if emp_id not in exclude and not self.assignments.get(emp_id)
        ]
