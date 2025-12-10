#!/usr/bin/env python3
"""
Point d'entrée principal du projet de démonstration.

Usage:
    python main.py                  # Menu interactif
    python main.py --assistant      # Demo Assistant Virtuel
    python main.py --agent          # Demo Agent Agentique
    python main.py --multi          # Demo Multi-Agents
    python main.py --compare        # Comparaison complète
"""
import sys
import argparse

from src.assistant_virtuel.assistant import VirtualAssistant
from src.agent_agentique.agent import AgenticAgent, AgentContext
from src.multi_agents.orchestrator import Orchestrator, OrchestratorContext

# Scénario de démonstration par défaut
DEFAULT_SCENARIO = (
    "Je dois m'absenter demain pour une urgence familiale. "
    "J'ai une réunion client importante à 14h et le planning d'équipe doit être mis à jour."
)


def demo_assistant():
    """Démonstration de l'Assistant Virtuel."""
    print("\n" + "=" * 70)
    print(" DÉMONSTRATION: ASSISTANT VIRTUEL (CHATBOT) ".center(70))
    print("=" * 70)

    assistant = VirtualAssistant()
    assistant.demonstrate(DEFAULT_SCENARIO)


def demo_agent():
    """Démonstration de l'Agent Agentique."""
    print("\n" + "=" * 70)
    print(" DÉMONSTRATION: AGENT AGENTIQUE ".center(70))
    print("=" * 70)

    agent = AgenticAgent()
    agent.demonstrate(DEFAULT_SCENARIO)


def demo_multi_agents():
    """Démonstration du Système Multi-Agents."""
    print("\n" + "=" * 70)
    print(" DÉMONSTRATION: SYSTÈME MULTI-AGENTS ".center(70))
    print("=" * 70)

    orchestrator = Orchestrator()
    orchestrator.demonstrate(DEFAULT_SCENARIO)


def run_comparison():
    """Exécute la comparaison complète."""
    from examples.comparison import main as compare_main
    compare_main()


def interactive_menu():
    """Menu interactif principal."""
    while True:
        print("\n" + "=" * 60)
        print(" AGENT AGENTIQUE vs ASSISTANT VIRTUEL ".center(60))
        print(" Projet de Démonstration ".center(60))
        print("=" * 60)

        print("""
Choisissez une option:

  1. Assistant Virtuel (Chatbot)
     → Voir comment un chatbot classique répond

  2. Agent Agentique
     → Voir comment un agent autonome agit

  3. Système Multi-Agents
     → Voir l'orchestration d'agents spécialisés

  4. Comparaison Complète
     → Exécuter les 3 approches côte à côte

  5. Afficher le Scénario de Test

  0. Quitter
""")

        try:
            choice = input("Votre choix [0-5]: ").strip()

            if choice == "1":
                demo_assistant()
                input("\nAppuyez sur Entrée pour continuer...")

            elif choice == "2":
                demo_agent()
                input("\nAppuyez sur Entrée pour continuer...")

            elif choice == "3":
                demo_multi_agents()
                input("\nAppuyez sur Entrée pour continuer...")

            elif choice == "4":
                run_comparison()

            elif choice == "5":
                print("\n" + "-" * 60)
                print("SCÉNARIO DE TEST:")
                print("-" * 60)
                print(f"\n{DEFAULT_SCENARIO}\n")
                print("-" * 60)
                print("""
Ce scénario est complexe car il implique:
  • Une demande de congé urgente (RH)
  • Une vérification de calendrier (conflit de réunion)
  • Une recherche de remplaçant (planning d'équipe)
  • Des notifications multiples (email)

C'est un excellent test pour montrer les différences
entre les trois approches.
""")
                input("Appuyez sur Entrée pour continuer...")

            elif choice == "0":
                print("\nMerci d'avoir utilisé cette démonstration!")
                print("À bientôt.\n")
                sys.exit(0)

            else:
                print("\nOption non reconnue. Veuillez choisir entre 0 et 5.")

        except KeyboardInterrupt:
            print("\n\nInterruption détectée. Au revoir!")
            sys.exit(0)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Démonstration: Agent Agentique vs Assistant Virtuel"
    )
    parser.add_argument(
        "--assistant", "-a",
        action="store_true",
        help="Exécuter la démo de l'Assistant Virtuel"
    )
    parser.add_argument(
        "--agent", "-g",
        action="store_true",
        help="Exécuter la démo de l'Agent Agentique"
    )
    parser.add_argument(
        "--multi", "-m",
        action="store_true",
        help="Exécuter la démo du Système Multi-Agents"
    )
    parser.add_argument(
        "--compare", "-c",
        action="store_true",
        help="Exécuter la comparaison complète"
    )

    args = parser.parse_args()

    # Si aucun argument, lancer le menu interactif
    if not any([args.assistant, args.agent, args.multi, args.compare]):
        interactive_menu()
    else:
        if args.assistant:
            demo_assistant()
        if args.agent:
            demo_agent()
        if args.multi:
            demo_multi_agents()
        if args.compare:
            run_comparison()


if __name__ == "__main__":
    main()
