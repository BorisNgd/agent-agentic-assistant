"""
Système de logging pour traçabilité des actions.
Permet de visualiser le comportement des différentes approches.
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from functools import wraps


class ActionType(Enum):
    """Types d'actions loggées."""
    REASONING = "reasoning"      # Raisonnement interne
    TOOL_CALL = "tool_call"     # Appel d'outil/API
    OBSERVATION = "observation"  # Observation du résultat
    DECISION = "decision"        # Décision prise
    USER_OUTPUT = "user_output"  # Message à l'utilisateur
    ERROR = "error"              # Erreur rencontrée
    DELEGATION = "delegation"    # Délégation à un autre agent


class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour le terminal."""

    COLORS = {
        "reasoning": "\033[94m",     # Bleu
        "tool_call": "\033[92m",     # Vert
        "observation": "\033[93m",   # Jaune
        "decision": "\033[95m",      # Magenta
        "user_output": "\033[96m",   # Cyan
        "error": "\033[91m",         # Rouge
        "delegation": "\033[97m",    # Blanc
        "reset": "\033[0m"           # Reset
    }

    ICONS = {
        "reasoning": "",
        "tool_call": "",
        "observation": "",
        "decision": "",
        "user_output": "",
        "error": "",
        "delegation": ""
    }

    def format(self, record: logging.LogRecord) -> str:
        action_type = getattr(record, 'action_type', 'reasoning')
        color = self.COLORS.get(action_type, "")
        reset = self.COLORS["reset"]
        icon = self.ICONS.get(action_type, "")

        formatted_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        source = getattr(record, 'source', 'System')

        return f"{color}[{formatted_time}] {icon} [{source}] {record.getMessage()}{reset}"


def setup_logger(name: str = "AgentDemo", level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger avec formatage coloré.

    Args:
        name: Nom du logger
        level: Niveau de logging

    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Éviter les handlers dupliqués
    if logger.handlers:
        logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())
    logger.addHandler(handler)

    return logger


def log_action(
    logger: logging.Logger,
    action_type: ActionType,
    message: str,
    source: str = "Agent"
) -> None:
    """
    Log une action avec métadonnées.

    Args:
        logger: Logger à utiliser
        action_type: Type d'action
        message: Message à logger
        source: Source de l'action
    """
    extra = {
        "action_type": action_type.value,
        "source": source
    }
    logger.info(message, extra=extra)


def trace_action(action_type: ActionType, source: str = "Agent"):
    """
    Décorateur pour tracer automatiquement les appels de fonction.

    Args:
        action_type: Type d'action
        source: Source de l'action
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("AgentDemo")
            log_action(
                logger,
                ActionType.TOOL_CALL,
                f"Calling {func.__name__}({args[1:] if args else ''}, {kwargs})",
                source
            )
            try:
                result = func(*args, **kwargs)
                log_action(
                    logger,
                    ActionType.OBSERVATION,
                    f"{func.__name__} returned: {result}",
                    source
                )
                return result
            except Exception as e:
                log_action(
                    logger,
                    ActionType.ERROR,
                    f"{func.__name__} failed: {e}",
                    source
                )
                raise
        return wrapper
    return decorator


class ActionLogger:
    """Classe utilitaire pour logging structuré dans les démonstrations."""

    def __init__(self, source: str, logger: Optional[logging.Logger] = None):
        self.source = source
        self.logger = logger or setup_logger()
        self.action_history: list[dict] = []

    def reasoning(self, message: str) -> None:
        """Log un raisonnement."""
        self._log(ActionType.REASONING, message)

    def tool_call(self, tool_name: str, params: dict) -> None:
        """Log un appel d'outil."""
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        self._log(ActionType.TOOL_CALL, f"{tool_name}({param_str})")

    def observation(self, message: str) -> None:
        """Log une observation."""
        self._log(ActionType.OBSERVATION, message)

    def decision(self, message: str) -> None:
        """Log une décision."""
        self._log(ActionType.DECISION, message)

    def user_output(self, message: str) -> None:
        """Log un message pour l'utilisateur."""
        self._log(ActionType.USER_OUTPUT, message)

    def error(self, message: str) -> None:
        """Log une erreur."""
        self._log(ActionType.ERROR, message)

    def delegation(self, target: str, task: str) -> None:
        """Log une délégation à un autre agent."""
        self._log(ActionType.DELEGATION, f"-> {target}: {task}")

    def _log(self, action_type: ActionType, message: str) -> None:
        """Log interne avec enregistrement dans l'historique."""
        log_action(self.logger, action_type, message, self.source)
        self.action_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": action_type.value,
            "source": self.source,
            "message": message
        })

    def get_history(self) -> list[dict]:
        """Retourne l'historique des actions."""
        return self.action_history.copy()

    def print_summary(self) -> None:
        """Affiche un résumé des actions effectuées."""
        print(f"\n{'='*60}")
        print(f"Résumé des actions - {self.source}")
        print(f"{'='*60}")

        type_counts = {}
        for action in self.action_history:
            t = action["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        for action_type, count in type_counts.items():
            print(f"  {action_type}: {count}")

        print(f"{'='*60}\n")
