"""
Utilitaires communs pour le projet de démonstration.
"""
from .models import Employee, LeaveRequest, Meeting, CalendarEvent
from .mock_services import HRService, CalendarService, EmailService, TeamService
from .logger import setup_logger, log_action

__all__ = [
    "Employee",
    "LeaveRequest",
    "Meeting",
    "CalendarEvent",
    "HRService",
    "CalendarService",
    "EmailService",
    "TeamService",
    "setup_logger",
    "log_action",
]
