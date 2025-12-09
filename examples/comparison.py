"""
Comparaison côte à côte des trois approches.

Ce script exécute le même scénario avec:
1. Assistant Virtuel (Chatbot)
2. Agent Agentique
3. Système Multi-Agents

Et affiche les différences de comportement.
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assistant_virtuel.assistant import VirtualAssistant
from src.agent_agentique.agent import AgenticAgent, AgentContext
from src.multi_agents.orchestrator import Orchestrator, OrchestratorContext


def print_header(title: str, char: str = "=") -> None:
    """Affiche un en-tête formaté."""
    width = 70
    print("\n" + char * width)
    print(f" {title}".center(width))
    print(char * width + "\n")


def print_section(title: str) -> None:
    """Affiche une section."""
    print(f"\n--- {title} ---\n")


def compare_capabilities() -> None:
    """Compare les capacités des trois approches."""
    print_header("COMPARAISON DES CAPACITÉS", "=")

    assistant = VirtualAssistant()
    agent = AgenticAgent()
    orchestrator = Orchestrator()

    caps = [
        assistant.get_capabilities(),
        agent.get_capabilities(),
        orchestrator.get_capabilities()
    ]

    # Affichage en tableau
    headers = ["Critère", "Assistant Virtuel", "Agent Agentique", "Multi-Agents"]
    rows = [
        ["Type", caps[0]["type"], caps[1]["type"], caps[2]["type"]],
        ["Pattern", caps[0]["pattern"], caps[1]["pattern"], caps[2]["pattern"]],
        ["Autonomie", caps[0]["autonomy_level"], caps[1]["autonomy_level"], caps[2]["autonomy_level"]],
    ]

    # Afficher le tableau
    col_widths = [15, 20, 20, 20]
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    print(separator)
    print("|" + "|".join(f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)) + "|")
    print(separator)

    for row in rows:
        print("|" + "|".join(f" {str(c)[:col_widths[i]]:<{col_widths[i]}} " for i, c in enumerate(row)) + "|")
    print(separator)

    print_section("Capacités de l'Assistant Virtuel")
    for cap in caps[0]["capabilities"]:
        print(f"  + {cap}")
    print("\n  Limitations:")
    for lim in caps[0]["limitations"]:
        print(f"  - {lim}")

    print_section("Capacités de l'Agent Agentique")
    for cap in caps[1]["capabilities"]:
        print(f"  + {cap}")

    print_section("Capacités du Système Multi-Agents")
    for cap in caps[2]["capabilities"]:
        print(f"  + {cap}")
    print("\n  Agents spécialisés:")
    for agent_info in caps[2]["agents"]:
        print(f"  - {agent_info['name']}: {agent_info['domain']}")


def run_scenario_comparison() -> None:
    """Execute le même scénario avec les trois approches."""

    scenario = (
        "Je dois m'absenter demain pour une urgence familiale. "
        "J'ai une réunion client importante à 14h et le planning d'équipe doit être mis à jour."
    )

    print_header("SCÉNARIO DE TEST", "=")
    print(f"Demande utilisateur:\n\"{scenario}\"")

    # ==========================================
    # APPROCHE 1: ASSISTANT VIRTUEL
    # ==========================================
    print_header("APPROCHE 1: ASSISTANT VIRTUEL (CHATBOT)", "#")

    assistant = VirtualAssistant()
    result_assistant = assistant.process_complex_scenario(scenario)

    print("RÉPONSE DE L'ASSISTANT:")
    print("-" * 50)
    print(result_assistant["response"][:500] + "...")  # Tronquer pour lisibilité

    print("\n ANALYSE:")
    print(f"  - Actions réelles effectuées: {len(result_assistant['actions_taken'])}")
    print(f"  - Systèmes accédés: {len(result_assistant['systems_accessed'])}")
    print(f"  - Actions requises par l'utilisateur: {len(result_assistant['actions_required_by_user'])}")

    print("\n L'utilisateur doit MANUELLEMENT:")
    for action in result_assistant["actions_required_by_user"][:5]:
        print(f"    [ ] {action}")

    # ==========================================
    # APPROCHE 2: AGENT AGENTIQUE
    # ==========================================
    print_header("APPROCHE 2: AGENT AGENTIQUE", "#")

    agent = AgenticAgent()
    context_agent = AgentContext(user_request=scenario, employee_id="EMP001")

    print("EXÉCUTION DE L'AGENT (boucle ReAct)...")
    print("-" * 50)
    result_agent = agent.process_request(context_agent)

    print("\n RAPPORT:")
    # Afficher un extrait du message
    lines = result_agent["user_message"].split("\n")[:15]
    for line in lines:
        print(line)
    print("...")

    print("\n ANALYSE:")
    print(f"  - Étapes de raisonnement: {result_agent['steps_executed']}")
    print(f"  - Actions réelles effectuées: {len(result_agent['actions_taken'])}")
    print(f"  - Systèmes accédés: {len(result_agent['systems_accessed'])}")

    print("\n Actions AUTOMATISÉES par l'agent:")
    for action in result_agent["actions_taken"]:
        print(f"    [✓] {action}")

    # ==========================================
    # APPROCHE 3: SYSTÈME MULTI-AGENTS
    # ==========================================
    print_header("APPROCHE 3: SYSTÈME MULTI-AGENTS", "#")

    orchestrator = Orchestrator()
    context_multi = OrchestratorContext(user_request=scenario, employee_id="EMP001")

    print("ORCHESTRATION MULTI-AGENTS...")
    print("-" * 50)
    result_multi = orchestrator.process_request(context_multi)

    print("\n RAPPORT CONSOLIDÉ:")
    # Afficher un extrait
    lines = result_multi["user_message"].split("\n")[:20]
    for line in lines:
        print(line)
    print("...")

    print("\n ANALYSE:")
    print(f"  - Tâches distribuées: {result_multi['tasks_executed']}")
    print(f"  - Tâches réussies: {result_multi['tasks_successful']}")
    print(f"  - Agents mobilisés: {len(result_multi['agents_used'])}")

    print("\n Agents utilisés:")
    for agent_name in result_multi["agents_used"]:
        print(f"    - {agent_name}")

    print("\n Exécution détaillée:")
    for task_id, details in list(result_multi["execution_details"].items())[:6]:
        status = "OK" if details["status"] == "success" else "ERR"
        print(f"    [{status}] {details['agent']}: {task_id}")


def print_summary() -> None:
    """Affiche un résumé des différences."""
    print_header("RÉSUMÉ COMPARATIF", "=")

    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                    ASSISTANT VIRTUEL (CHATBOT)                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Pattern:      Question → Réponse (réactif)                               ║
║ Autonomie:    AUCUNE                                                     ║
║ Actions:      AUCUNE (instructions manuelles uniquement)                 ║
║ Idéal pour:   FAQ, Support niveau 1, Information                         ║
╚══════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════╗
║                       AGENT AGENTIQUE                                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Pattern:      Thought → Action → Observation → Repeat (ReAct)            ║
║ Autonomie:    ÉLEVÉE avec supervision                                    ║
║ Actions:      Exécute via outils (APIs, DBs, etc.)                       ║
║ Idéal pour:   Automatisation, Tâches multi-étapes, Workflows             ║
╚══════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════╗
║                      SYSTÈME MULTI-AGENTS                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Pattern:      Orchestration → Distribution → Parallélisation → Agrégation║
║ Autonomie:    TRÈS ÉLEVÉE (système auto-organisé)                        ║
║ Actions:      Multiples agents spécialisés en parallèle                  ║
║ Idéal pour:   Processus complexes, Domaines multiples, Scale             ║
╚══════════════════════════════════════════════════════════════════════════╝
""")


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 70)
    print(" DÉMONSTRATION: ASSISTANT vs AGENT vs MULTI-AGENTS ".center(70))
    print("=" * 70)

    print("\nCe programme démontre les différences fondamentales entre:")
    print("  1. Assistant Virtuel (Chatbot classique)")
    print("  2. Agent Agentique (IA autonome avec outils)")
    print("  3. Système Multi-Agents (Orchestration d'agents spécialisés)")

    input("\nAppuyez sur Entrée pour commencer la comparaison...")

    compare_capabilities()
    input("\nAppuyez sur Entrée pour voir l'exécution du scénario...")

    run_scenario_comparison()
    input("\nAppuyez sur Entrée pour voir le résumé final...")

    print_summary()

    print("\n" + "=" * 70)
    print(" FIN DE LA DÉMONSTRATION ".center(70))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
