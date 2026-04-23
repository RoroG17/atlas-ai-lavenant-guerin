# Module de gestion de la mémoire vectorielle
import chromadb
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import re
from atlas.config import CONFIG


# Mots vides à exclure de l'extraction de mots-clés
_STOPWORDS = {
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "en",
    "à", "au", "aux", "ce", "je", "tu", "il", "elle", "nous", "vous",
    "ils", "elles", "que", "qui", "quoi", "comment", "est", "sont",
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses",
    "sur", "sous", "dans", "par", "pour", "avec", "sans", "ou", "si",
    "me", "te", "se", "ne", "pas", "plus", "très", "bien", "tout",
    "this", "the", "is", "are", "a", "an", "of", "in", "on", "at",
}


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extrait les mots-clés significatifs d'un texte.
    Filtre les stopwords et les mots trop courts.
    """
    words = re.findall(r'\b[a-zA-ZÀ-ÿ]{' + str(min_length) + r',}\b', text.lower())
    return [w for w in words if w not in _STOPWORDS]


def summarize_response(response: str, max_length: int = 200) -> str:
    """
    Résume une réponse en tronquant à la première phrase complète
    qui ne dépasse pas max_length caractères.
    """
    if len(response) <= max_length:
        return response

    # Cherche la première coupure propre (fin de phrase)
    for sep in (". ", ".\n", "! ", "? "):
        idx = response.find(sep, max_length // 2)
        if 0 < idx <= max_length:
            return response[: idx + 1].strip()

    return response[:max_length].rstrip() + "…"


class VectorMemory:
    """
    Gère la mémoire vectorielle persistante avec ChromaDB.

    Stratégie :
    - On stocke un RÉSUMÉ des réponses associé aux MOTS-CLÉS de la question.
    - On recherche uniquement sur les mots-clés (pas le texte complet).
    - On n'injecte qu'UN SEUL souvenir dans le prompt (le plus proche).
    - Les doublons (même ensemble de mots-clés) sont dédupliqués ;
      en cas de contradiction, la réponse la plus récente écrase l'ancienne.
    """

    def __init__(self, memory_path: str = "./data/memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.memory_path))
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Résumés de réponses indexés par mots-clés"},
        )

    # ── API principale ────────────────────────────────────────────────────────

    def store_exchange(self, question: str, response: str) -> Optional[str]:
        """
        Stocke le résumé d'une réponse, indexé par les mots-clés de la question.

        - Calcule un ID déterministe à partir des mots-clés → gère les doublons
          (upsert : la nouvelle réponse écrase l'ancienne si même sujet).
        - Ne stocke rien si aucun mot-clé n'est extrait.

        Returns:
            ID du document stocké, ou None si pas de mots-clés.
        """
        keywords = extract_keywords(question)
        if not keywords:
            return None

        summary = summarize_response(response)

        # ID déterministe basé sur les mots-clés triés → même sujet = même ID
        keyword_key = "_".join(sorted(set(keywords)))
        doc_id = f"kw_{hash(keyword_key) & 0xFFFFFFFF:08x}"

        # Le document ChromaDB = les mots-clés (c'est sur eux qu'on cherche)
        keyword_document = " ".join(sorted(set(keywords)))

        metadata = {
            "summary": summary,
            "keywords": ", ".join(sorted(set(keywords))),
            "timestamp": datetime.now().isoformat(),
        }

        # upsert : crée ou écrase silencieusement le souvenir existant
        try:
            self.collection.upsert(
                ids=[doc_id],
                documents=[keyword_document],
                metadatas=[metadata],
            )
        except Exception as e:
            print(f"[VectorMemory] Erreur stockage : {e}")
            return None

        return doc_id

    def get_memories_as_text(self, question: str, n_results: Optional[int] = None) -> Optional[str]:
        """
        Récupère plusieurs souvenirs et les formate en un seul bloc de texte.
        Filtre par min_similarity défini dans la config.
        """
        if self.collection.count() == 0:
            return None

        keywords = extract_keywords(question)
        if not keywords:
            return None

        query_text = " ".join(keywords)
        
        # Paramètres depuis la config
        if n_results is None:
            n_results = CONFIG["memory"].get("top_k", 5)
        
        min_similarity = CONFIG["memory"].get("min_similarity", 0.7)

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
            )
        except Exception as e:
            print(f"[VectorMemory] Erreur recherche : {e}")
            return None

        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not metas:
            return None

        formatted_memories = []
        for meta, dist in zip(metas, distances):
            # ChromaDB utilise souvent la distance L2 par défaut.
            # On simule une similarité simple pour le filtrage (1 - dist/2 ou autre selon l'espace)
            # Ici on fait une vérification basique.
            similarity = 1.0 - (dist / 2.0) if dist < 2.0 else 0
            
            if similarity < min_similarity:
                continue
                
            summary = meta.get("summary", "")
            kw = meta.get("keywords", "")
            ts = meta.get("timestamp", "")[:10]
            
            formatted_memories.append(
                f"- Souvenir ({ts}) [mots-clés: {kw}] : {summary}"
            )

        if not formatted_memories:
            return None

        return "\n".join(formatted_memories)

    def retrieve_best_memory(self, question: str) -> Optional[str]:
        """
        Cherche dans la mémoire le souvenir le plus pertinent pour la question.
        Utilise get_memories_as_text avec n_results=1.
        """
        return self.get_memories_as_text(question, n_results=1)

    # ── utilitaires ───────────────────────────────────────────────────────────

    def clear_all(self) -> None:
        """Efface tous les souvenirs."""
        self.client.delete_collection(name="conversations")
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Résumés de réponses indexés par mots-clés"},
        )

    def get_collection_stats(self) -> Dict:
        """Statistiques de la collection."""
        return {
            "total_memories": self.collection.count(),
            "memory_path": str(self.memory_path),
        }
