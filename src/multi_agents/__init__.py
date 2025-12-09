"""
Système Multi-Agents - Orchestration d'agents spécialisés

Ce module implémente un système multi-agents qui:
- Orchestre plusieurs agents spécialisés
- Distribue les tâches selon les domaines d'expertise
- Permet l'exécution parallèle
- Gère la communication inter-agents
- Assure la résilience et les fallbacks
"""
from .orchestrator import Orchestrator
from .specialized_agents import HRAgent, CalendarAgent, EmailAgent, PlanningAgent

__all__ = [
    "Orchestrator",
    "HRAgent",
    "CalendarAgent",
    "EmailAgent",
    "PlanningAgent"
]
