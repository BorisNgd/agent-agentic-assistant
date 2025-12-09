"""
Assistant Virtuel - Chatbot Classique

Ce module implémente un assistant virtuel traditionnel qui:
- Répond aux questions de manière réactive
- Ne prend pas d'actions autonomes
- Fournit des informations et instructions
- Ne possède pas de mémoire contextuelle entre les interactions
"""
from .assistant import VirtualAssistant
from .knowledge_base import KnowledgeBase

__all__ = ["VirtualAssistant", "KnowledgeBase"]
