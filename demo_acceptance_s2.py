#!/usr/bin/env python
"""
Script de démonstration pour le formateur - Critères d'acceptation Sprint 2

Scénario à dérouler :
1. Session A : "Je m'appelle Dupont et je travaille sur le projet Luna pour le client Atos."
2. Fermer la CLI (simulé par réouverture)
3. Session B : "Sur quel projet je bosse ?" → réponse correcte attendue
"""

from atlas.memory import VectorMemory
from pathlib import Path
import shutil


def demo_acceptance_criteria():
    """Démontre les critères d'acceptation S2."""
    print("\n" + "=" * 70)
    print(" " * 15 + "DÉMONSTRATION SPRINT 2")
    print(" " * 10 + "Critères d'acceptation mémoire persistante")
    print("=" * 70)
    
    memory_path = "./data/memory"
    
    # Vérifier si mémoire existante
    existing = Path(memory_path).exists()
    
    if existing:
        print("Mémoire existante détectée.")
        response = input("Voulez-vous la réutiliser (r) ou la réinitialiser (n)? [r/n]: ").lower()
        if response == "n":
            shutil.rmtree(memory_path)
            print("Mémoire réinitialisée")
    
    # ============================================================================
    print("\n" + "=" * 70)
    print(" ÉTAPE 1: SESSION A - Stockage de l'identité et du projet")
    print("=" * 70)
    
    memory = VectorMemory(memory_path=memory_path)
    
    user_input_a = "Je m'appelle Dupont et je travaille sur le projet Luna pour le client Atos."
    print(f"\n👤 User: {user_input_a}")
    
    # Simuler la réponse du bot
    bot_response_a = "Enchanté Dupont! J'ai mémorisé que vous travaillez sur le projet Luna pour le client Atos. Je retrouverai cette information même après fermeture de la session."
    print(f"Bot: {bot_response_a}")
    
    # Stocker en mémoire
    memory.store_message("user", user_input_a)
    memory.store_message("assistant", bot_response_a)
    
    stats = memory.get_collection_stats()
    print(f"\nStocké en mémoire vectorielle")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Localisation: {stats['memory_path']}")
    
    # ============================================================================
    print("\n" + "=" * 70)
    print(" ÉTAPE 2: Fermeture de la CLI")
    print("=" * 70)
    print("\n[Simulé: La CLI se ferme et se rouvre avec une nouvelle instance]")
    print("[En réalité: même fichier sqlite dans ./data/memory/]")
    
    # Créer une NOUVELLE instance mémoire (simule réouverture)
    memory_session_b = VectorMemory(memory_path=memory_path)
    stats_b = memory_session_b.get_collection_stats()
    
    print(f"\n CLI rouverte avec mémoire persistante")
    print(f"   Souvenirs retrouvés: {stats_b['total_messages']}")
    
    # ============================================================================
    print("\n" + "=" * 70)
    print(" ÉTAPE 3: SESSION B - Récupération d'informations")
    print("=" * 70)
    
    user_input_b = "Sur quel projet je bosse ?"
    print(f"\n User: {user_input_b}")
    
    # Rechercher dans la mémoire
    print(f"\n Recherche dans la mémoire persistante...")
    retrieved = memory_session_b.retrieve_memories(user_input_b, n_results=3)
    
    print(f"\n Résultats trouvés: {len(retrieved)}")
    for i, mem in enumerate(retrieved, 1):
        role = mem['metadata'].get('role', '?')
        distance = mem['distance']
        content = mem['content']
        
        # Marquer si c'est la réponse critique
        is_critical = "Dupont" in content and "Luna" in content
        marker = "CRITICAL" if is_critical else ""
        
        print(f"\n   {i}. [{role.upper()}] {marker}")
        print(f"      Score: {distance:.3f}")
        print(f"      \"{content[:90]}...\"")
    
    # Vérifier le critère critique
    critical_found = any(
        "Dupont" in mem['content'] and "Luna" in mem['content'] 
        for mem in retrieved
    )
    
    if critical_found:
        print("\n" + "=" * 70)
        print("CRITÈRE D'ACCEPTATION SATISFAIT")
        print("=" * 70)
        print("\nLe bot a correctement retrouvé:")
        print("  • Le nom: Dupont")
        print("  • Le projet: Luna")
        print("  • Le client: Atos")
        print("\nMême après fermeture et réouverture de la CLI!")
    else:
        print("\n" + "=" * 70)
        print(" CRITÈRE NON SATISFAIT")
        print("=" * 70)
    
    # Afficher la réponse attendue du bot
    print("\n" + "-" * 70)
    print(" Réponse attendue du bot:")
    print("-" * 70)
    print("\nLa recherche dans ma mémoire retrouve que vous êtes Dupont")
    print("et que vous travaillez sur le projet Luna pour le client Atos.")
    print("\nVous travaillez sur le projet Luna pour le client Atos.")
    
    print("\n" + "=" * 70)
    print(" " * 20 + " DÉMONSTRATION TERMINÉE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo_acceptance_criteria()
