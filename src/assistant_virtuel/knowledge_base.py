"""
Base de connaissances statique pour l'Assistant Virtuel.
Contient les réponses pré-définies aux questions fréquentes.
"""
from __future__ import annotations
from typing import Tuple, List


class KnowledgeBase:
    """
    Base de connaissances FAQ pour l'assistant virtuel.

    Cette classe représente la limitation fondamentale d'un chatbot classique:
    il ne peut que matcher des intentions et retourner des réponses pré-définies.
    """

    # Réponses pré-définies organisées par intention
    RESPONSES = {
        "leave_request": {
            "keywords": ["congé", "absence", "vacances", "jour de repos", "leave"],
            "response": """
Pour faire une demande de congé, veuillez suivre ces étapes:

1. Connectez-vous au portail RH (hr.company.com)
2. Accédez à "Mes demandes" > "Nouvelle demande de congé"
3. Remplissez le formulaire HR-001 avec:
   - Date de début et fin
   - Motif de l'absence
   - Type de congé (payé, sans solde, etc.)
4. Soumettez la demande pour validation
5. Votre manager recevra une notification par email

Note: Les demandes urgentes (moins de 48h) nécessitent le formulaire HR-001-URG
et une validation téléphonique de votre manager.

Avez-vous d'autres questions sur les congés?
            """.strip()
        },

        "urgent_leave": {
            "keywords": ["urgent", "urgence", "demain", "immédiat", "emergency"],
            "response": """
Pour une demande de congé URGENTE (moins de 48h):

1. Contactez immédiatement votre manager par téléphone
2. Envoyez un email de confirmation à votre manager ET aux RH
3. Remplissez le formulaire HR-001-URG
4. Indiquez clairement le motif d'urgence

Documents à fournir:
- Justificatif si nécessaire (certificat médical, etc.)

Important: Les congés urgents doivent être exceptionnels et justifiés.
Le délai standard de demande est de 5 jours ouvrés.

Puis-je vous aider avec autre chose?
            """.strip()
        },

        "meeting_reschedule": {
            "keywords": ["réunion", "meeting", "reporter", "annuler", "remplacer"],
            "response": """
Pour modifier ou annuler une réunion:

1. Ouvrez votre calendrier Outlook/Google Calendar
2. Localisez la réunion concernée
3. Options disponibles:
   - Modifier: Changez la date/heure et envoyez la mise à jour
   - Annuler: Cliquez sur "Annuler" et notifiez les participants
   - Déléguer: Transférez l'invitation à un collègue

Pour les réunions clients:
- Prévenez votre manager avant toute modification
- Assurez-vous d'avoir un remplaçant qualifié
- Mettez à jour le CRM si nécessaire

Avez-vous besoin d'aide supplémentaire?
            """.strip()
        },

        "find_replacement": {
            "keywords": ["remplaçant", "remplacement", "collègue disponible", "backup"],
            "response": """
Pour trouver un remplaçant:

1. Consultez le planning d'équipe dans Teams/SharePoint
2. Vérifiez les disponibilités de vos collègues
3. Identifiez les personnes avec les compétences requises
4. Contactez-les directement pour demander leur disponibilité
5. Une fois confirmé, mettez à jour l'invitation de réunion

Conseil: Prévenez votre manager de l'arrangement.

Outils utiles:
- Teams: Voir le statut de présence
- Outlook: Vérifier les calendriers partagés
- SharePoint: Planning d'équipe

Autre question?
            """.strip()
        },

        "team_schedule": {
            "keywords": ["planning", "équipe", "schedule", "disponibilité"],
            "response": """
Pour consulter ou modifier le planning d'équipe:

1. Accédez à Teams > Votre équipe > Planning
2. Ou consultez SharePoint: sites/equipe-it/planning

Pour les modifications:
- Contactez votre manager pour toute modification
- Les changements de dernière minute nécessitent une approbation
- Mettez à jour le planning APRÈS validation

Rappel: Tout changement doit être communiqué à l'équipe.

Besoin d'autres informations?
            """.strip()
        },

        "default": {
            "keywords": [],
            "response": """
Je suis l'assistant RH virtuel. Je peux vous aider avec:

- Demandes de congé et absences
- Gestion des réunions
- Planning d'équipe
- Procédures RH générales

Comment puis-je vous aider aujourd'hui?
            """.strip()
        }
    }

    @classmethod
    def find_best_response(cls, user_input: str) -> tuple[str, str]:
        """
        Trouve la meilleure réponse basée sur les mots-clés.

        Args:
            user_input: Message de l'utilisateur

        Returns:
            Tuple (intention_détectée, réponse)
        """
        user_input_lower = user_input.lower()

        # Score chaque intention basé sur les mots-clés trouvés
        best_intent = "default"
        best_score = 0

        for intent, data in cls.RESPONSES.items():
            if intent == "default":
                continue

            score = sum(
                1 for keyword in data["keywords"]
                if keyword in user_input_lower
            )

            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent, cls.RESPONSES[best_intent]["response"]

    @classmethod
    def get_faq_list(cls) -> list[str]:
        """Retourne la liste des sujets couverts."""
        return [
            intent for intent in cls.RESPONSES.keys()
            if intent != "default"
        ]
