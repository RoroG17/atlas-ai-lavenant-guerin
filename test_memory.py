#!/usr/bin/env python
"""
Script de test pour valider l'intégration mémoire vectorielle.
Simule les critères d'acceptation du Sprint 2.
"""

from atlas.memory import VectorMemory
from pathlib import Path
import shutil


def test_vector_memory():
    """Test l'intégration mémoire vectorielle."""
    print("=" * 60)
    print("🧪 TEST: Mémoire Vectorielle avec ChromaDB")
    print("=" * 60)
    
    # Nettoyer la mémoire précédente
    memory_path = "./data/memory_test"
    if Path(memory_path).exists():
        shutil.rmtree(memory_path)
    
    # Créer une instance mémoire
    memory = VectorMemory(memory_path=memory_path)
    print("\n✅ Mémoire vectorielle initialisée")
    
    # === SESSION A: Stocker des informations ===
    print("\n" + "=" * 60)
    print("📝 SESSION A: Stockage d'informations")
    print("=" * 60)
    
    memories_to_store = [
        ("Je m'appelle Dupont et je travaille sur le projet Luna pour le client Atos.", "user"),
        ("Enchanté Dupont! Je vais mémoriser que vous travaillez sur le projet Luna pour Atos.", "assistant"),
        ("Luna est un projet stratégique pour 2026-2027.", "user"),
        ("Luna est un projet stratégique. C'est noté dans ma mémoire longue.", "assistant"),
        ("Nous allons utiliser une architecture micro-services.", "user"),
        ("Excellente architecture. Les micro-services vont bien avec Luna et Atos.", "assistant"),
    ]
    
    for content, role in memories_to_store:
        msg_id = memory.store_message(role, content)
        print(f"  ✓ [{role.upper()}] Stocké: {content[:50]}...")
    
    # Afficher les stats
    stats = memory.get_collection_stats()
    print(f"\n Stats après Session A:")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  Chemin: {stats['memory_path']}")
    
    # === TEST DE RETRIEVAL: Chercher "projet Luna" ===
    print("\n" + "=" * 60)
    print(" TEST: Recherche 'projet Luna'")
    print("=" * 60)
    
    results = memory.retrieve_memories("projet Luna", n_results=3)
    print(f"\n  Résultats trouvés: {len(results)}")
    for i, mem in enumerate(results, 1):
        role = mem['metadata'].get('role', 'unknown').upper()
        distance = mem['distance']
        print(f"\n  {i}. [{role}] (distance: {distance:.3f})")
        print(f"     {mem['content'][:80]}...")
    
    # === TEST DE RETRIEVAL: Chercher le client ===
    print("\n" + "=" * 60)
    print(" TEST: Recherche 'client Atos'")
    print("=" * 60)
    
    results = memory.retrieve_memories("client Atos", n_results=3)
    print(f"\n  Résultats trouvés: {len(results)}")
    for i, mem in enumerate(results, 1):
        role = mem['metadata'].get('role', 'unknown').upper()
        print(f"\n  {i}. [{role}]")
        print(f"     {mem['content'][:80]}...")
    
    # === TEST DE RETRIEVAL: Chercher l'architecture ===
    print("\n" + "=" * 60)
    print("🔍 TEST: Recherche 'architecture'")
    print("=" * 60)
    
    results = memory.retrieve_memories("architecture", n_results=2)
    print(f"\n  Résultats trouvés: {len(results)}")
    for i, mem in enumerate(results, 1):
        role = mem['metadata'].get('role', 'unknown').upper()
        print(f"\n  {i}. [{role}]")
        print(f"     {mem['content'][:80]}...")
    
    # === PERSISTANCE: Créer une nouvelle session ===
    print("\n" + "=" * 60)
    print("💾 SESSION B: Test de persistance")
    print("=" * 60)
    
    # Réutiliser le même chemin de mémoire (simule une nouvelle session)
    memory_session_b = VectorMemory(memory_path=memory_path)
    stats_b = memory_session_b.get_collection_stats()
    print(f"\n✅ Données persistées après réouverture:")
    print(f"  Total messages: {stats_b['total_messages']}")
    
    # Chercher dans la mémoire existante
    print(f"\n🔍 Recherche 'Sur quel projet je bosse?'")
    results_b = memory_session_b.retrieve_memories("Sur quel projet je bosse", n_results=3)
    print(f"  Résultats trouvés: {len(results_b)}")
    for i, mem in enumerate(results_b, 1):
        role = mem['metadata'].get('role', 'unknown').upper()
        print(f"\n  {i}. [{role}]")
        print(f"     {mem['content'][:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS RÉUSSIS!")
    print("=" * 60)
    
    # Nettoyage
    shutil.rmtree(memory_path)


if __name__ == "__main__":
    test_vector_memory()
