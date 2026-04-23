# Module de gestion de la mémoire vectorielle
import chromadb
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime


class VectorMemory:
    """
    Gère la mémoire vectorielle persistante avec ChromaDB.
    Stocke les conversations et permet de retrouver des souvenirs pertinents.
    """

    def __init__(self, memory_path: str = "./data/memory"):
        """
        Initialise le client ChromaDB persistant.

        Args:
            memory_path: Chemin où stocker la mémoire vectorielle
        """
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # Client persistant
        self.client = chromadb.PersistentClient(path=str(self.memory_path))

        # Collection pour les conversations
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Mémoire des conversations avec l'utilisateur"}
        )

        # Compteur pour les IDs uniques
        self._message_counter = 0

    def store_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Stocke un message dans la mémoire vectorielle.

        Args:
            role: "user" ou "assistant"
            content: Le contenu du message
            metadata: Métadonnées additionnelles (optionnel)

        Returns:
            ID du message stocké
        """
        self._message_counter += 1
        message_id = f"msg_{self._message_counter}"

        # Métadonnées par défaut
        meta = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            meta.update(metadata)

        # Stocker dans ChromaDB (ChromaDB embarque un modèle d'embedding par défaut)
        self.collection.add(
            ids=[message_id],
            documents=[content],
            metadatas=[meta]
        )

        return message_id

    def retrieve_memories(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Récupère les souvenirs pertinents à partir d'une requête.

        Args:
            query: Requête pour chercher les souvenirs
            n_results: Nombre de résultats à retourner

        Returns:
            Liste des souvenirs pertinents avec leur contenu et métadonnées
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            # Formatter les résultats
            memories = []
            if results and results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    memory = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    }
                    memories.append(memory)

            return memories
        except Exception as e:
            print(f"Erreur lors de la récupération des souvenirs: {e}")
            return []

    def get_memories_as_text(
        self,
        query: str,
        n_results: int = 5
    ) -> str:
        """
        Récupère les souvenirs et les formate pour injection dans le prompt.

        Args:
            query: Requête de recherche
            n_results: Nombre de résultats

        Returns:
            Texte formaté des souvenirs pour le prompt
        """
        memories = self.retrieve_memories(query, n_results)

        if not memories:
            return ""

        formatted = "📚 **Souvenirs pertinents:**\n"
        for i, memory in enumerate(memories, 1):
            role = memory["metadata"].get("role", "unknown")
            timestamp = memory["metadata"].get("timestamp", "")
            formatted += f"\n{i}. [{role.upper()}] {memory['content'][:100]}..."

        return formatted

    def clear_all(self):
        """Efface tous les souvenirs (pour tester)."""
        # ChromaDB ne a pas de méthode delete_all(), donc on supprime et recrée
        self.client.delete_collection(name="conversations")
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Mémoire des conversations avec l'utilisateur"}
        )
        self._message_counter = 0

    def get_collection_stats(self) -> Dict:
        """Retourne les statistiques de la collection."""
        count = self.collection.count()
        return {
            "total_messages": count,
            "memory_path": str(self.memory_path),
        }