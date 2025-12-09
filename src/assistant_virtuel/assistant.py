"""
Assistant Virtuel - Implémentation du chatbot classique.

Cet assistant illustre les LIMITATIONS d'un chatbot traditionnel:
- Réactif uniquement (pas d'actions proactives)
- Matching de mots-clés simple
- Réponses pré-définies
- Pas de capacité d'exécution
- Pas de contexte persistant
"""
from __future__ import annotations
from typing import Optional, List, Dict
from ..common.logger import ActionLogger, setup_logger
from .knowledge_base import KnowledgeBase


class VirtualAssistant:
    """
    Assistant Virtuel classique basé sur FAQ et matching de mots-clés.

    Caractéristiques:
    - Pattern: Question -> Réponse
    - Pas d'actions réelles sur les systèmes
    - Fournit des instructions que l'utilisateur doit suivre manuellement
    - Chaque interaction est indépendante (pas de mémoire)
    """

    def __init__(self, name: str = "Assistant RH"):
        self.name = name
        self.knowledge_base = KnowledgeBase()
        self.logger = ActionLogger(f"[{name}]", setup_logger())
        self.interaction_count = 0

    def greet(self) -> str:
        """Message d'accueil de l'assistant."""
        return f"""
Bonjour! Je suis {self.name}, votre assistant virtuel.

Je peux vous fournir des informations sur:
 - Les demandes de congé
 - La gestion des réunions
 - Le planning d'équipe
 - Les procédures RH

Comment puis-je vous aider?
        """.strip()

    def process_message(self, user_message: str) -> str:
        """
        Traite un message utilisateur et retourne une réponse.

        C'est ici que se manifeste la LIMITATION principale:
        L'assistant ne fait QUE répondre avec des informations.
        Il ne peut pas:
        - Créer une demande de congé
        - Envoyer des emails
        - Vérifier le calendrier
        - Trouver des remplaçants

        Args:
            user_message: Message de l'utilisateur

        Returns:
            Réponse textuelle de l'assistant
        """
        self.interaction_count += 1

        # Log le message reçu
        self.logger.observation(f"Message reçu: '{user_message}'")

        # Matching simple d'intention
        intent, response = self.knowledge_base.find_best_response(user_message)

        self.logger.reasoning(f"Intention détectée: {intent}")
        self.logger.user_output(f"Réponse fournie (intention: {intent})")

        return response

    def process_complex_scenario(self, scenario: str) -> dict:
        """
        Traite un scénario complexe pour démonstration.

        Cette méthode montre comment l'assistant gère une demande complexe:
        il décompose verbalement les étapes mais NE FAIT RIEN CONCRÈTEMENT.

        Args:
            scenario: Description du scénario complexe

        Returns:
            Dictionnaire avec la réponse et métadonnées
        """
        self.logger.observation(f"Scénario complexe reçu: '{scenario}'")
        self.logger.reasoning("Analyse du scénario pour identifier les besoins")

        # L'assistant ne peut que décrire ce que l'utilisateur DOIT faire
        response = self._generate_manual_instructions(scenario)

        return {
            "response": response,
            "actions_taken": [],  # AUCUNE action réelle!
            "actions_required_by_user": [
                "Remplir le formulaire HR-001-URG",
                "Contacter le manager par téléphone",
                "Envoyer un email de confirmation",
                "Vérifier le calendrier manuellement",
                "Contacter les collègues pour remplacement",
                "Mettre à jour le planning"
            ],
            "systems_accessed": [],  # L'assistant n'accède à RIEN
            "limitations": [
                "Ne peut pas créer la demande automatiquement",
                "Ne peut pas vérifier les conflits de calendrier",
                "Ne peut pas envoyer de notifications",
                "Ne peut pas rechercher des remplaçants",
                "L'utilisateur doit tout faire manuellement"
            ]
        }

    def _generate_manual_instructions(self, scenario: str) -> str:
        """Génère des instructions manuelles pour un scénario complexe."""
        return """
Je comprends que vous avez une situation complexe. Voici les étapes à suivre:

DEMANDE DE CONGÉ URGENT:
------------------------
1. Appelez votre manager immédiatement au poste XXX
2. Envoyez un email à votre manager ET hr@company.com
3. Remplissez le formulaire HR-001-URG sur le portail RH
4. Joignez tout justificatif nécessaire

GESTION DE VOS RÉUNIONS:
------------------------
1. Ouvrez votre calendrier Outlook
2. Identifiez les réunions du jour de votre absence
3. Pour chaque réunion critique:
   - Vérifiez qui peut vous remplacer
   - Contactez cette personne
   - Mettez à jour l'invitation si confirmé

MISE À JOUR DU PLANNING:
------------------------
1. Accédez au SharePoint de l'équipe
2. Mettez à jour votre statut
3. Informez vos collègues par Teams

IMPORTANT: Toutes ces actions doivent être effectuées PAR VOUS-MÊME.
Je ne peux que vous guider avec des informations.

Avez-vous d'autres questions sur ces procédures?
        """.strip()

    def get_capabilities(self) -> dict:
        """Retourne les capacités (limitées) de l'assistant."""
        return {
            "name": self.name,
            "type": "Assistant Virtuel (Chatbot)",
            "capabilities": [
                "Répondre aux questions fréquentes",
                "Fournir des informations sur les procédures",
                "Guider avec des instructions étape par étape",
                "Rediriger vers les bonnes ressources"
            ],
            "limitations": [
                "Ne peut PAS exécuter d'actions",
                "Ne peut PAS accéder aux systèmes",
                "Ne peut PAS créer de demandes",
                "Ne peut PAS envoyer d'emails",
                "Ne peut PAS vérifier les calendriers",
                "Pas de mémoire entre les sessions"
            ],
            "pattern": "Question -> Réponse (Réactif)",
            "autonomy_level": "Aucune"
        }

    def demonstrate(self, user_message: str) -> None:
        """
        Exécute une démonstration interactive avec affichage formaté.

        Args:
            user_message: Message de démonstration
        """
        print("\n" + "="*70)
        print("  DÉMONSTRATION: ASSISTANT VIRTUEL (CHATBOT)")
        print("="*70)

        print(f"\n[Utilisateur]: {user_message}\n")

        print("-"*70)
        print("  TRAITEMENT PAR L'ASSISTANT")
        print("-"*70)

        result = self.process_complex_scenario(user_message)

        print("\n[Assistant]:")
        print(result["response"])

        print("\n" + "-"*70)
        print("  ANALYSE DU COMPORTEMENT")
        print("-"*70)

        print("\n Actions RÉELLEMENT effectuées par l'assistant:")
        if result["actions_taken"]:
            for action in result["actions_taken"]:
                print(f"    - {action}")
        else:
            print("    (AUCUNE - l'assistant ne fait que répondre)")

        print("\n Actions que l'UTILISATEUR doit faire MANUELLEMENT:")
        for action in result["actions_required_by_user"]:
            print(f"    - {action}")

        print("\n Limitations:")
        for limitation in result["limitations"]:
            print(f"    - {limitation}")

        print("\n" + "="*70 + "\n")


def demo():
    """Fonction de démonstration standalone."""
    assistant = VirtualAssistant()

    # Scénario de test
    scenario = (
        "Je dois m'absenter demain pour une urgence familiale. "
        "J'ai une réunion client importante à 14h et le planning d'équipe doit être mis à jour."
    )

    assistant.demonstrate(scenario)


if __name__ == "__main__":
    demo()
