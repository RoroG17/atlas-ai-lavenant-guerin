# Module de gestion de la mémoire vectorielle
import chromadb
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import re


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

    def retrieve_best_memory(self, question: str) -> Optional[str]:
        """
        Cherche dans la mémoire le souvenir le plus pertinent pour la question.
        La recherche porte sur les MOTS-CLÉS, pas sur la question brute.

        Returns:
            Le résumé formaté (str) à injecter dans le prompt, ou None.
        """
        if self.collection.count() == 0:
            return None

        keywords = extract_keywords(question)
        if not keywords:
            return None

        query_text = " ".join(keywords)

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=1,          # ← on n'injecte qu'UN seul souvenir
            )
        except Exception as e:
            print(f"[VectorMemory] Erreur recherche : {e}")
            return None

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        if not docs or not metas:
            return None

        meta = metas[0]
        summary = meta.get("summary", "")
        kw = meta.get("keywords", "")
        ts = meta.get("timestamp", "")[:10]   # date seule

        return (
            f"Souvenir pertinent ({ts}) — mots-clés : {kw}\n"
            f"{summary}"
        )

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
