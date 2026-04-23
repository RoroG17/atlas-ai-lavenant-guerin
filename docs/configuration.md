# Guide de Configuration

La configuration de l'assistant Atlas AI centralise tous les paramètres dans le fichier `config/atlas.yaml`.

## Structure du fichier `atlas.yaml`

Le fichier est découpé en 4 sections principales.

### 1. `model` (Paramètres LLM)
- `name` : Nom du modèle Ollama à utiliser (ex: `llama3.2:3b`).
- `temperature` : Degré de créativité (0.0 à 2.0). Recommandé : `0.3`.
- `top_p` : Filtrage nucléaire. Recommandé : `0.9`.
- `num_ctx` : Taille de la fenêtre de contexte (ex: `4096`).

### 2. `persona` (Identité de l'IA)
- `name` : Nom affiché dans la console (ex: `Atlas`).
- `system_prompt` : Les instructions fondamentales qui dictent le comportement et le ton de l'assistant.

### 3. `memory` (RAG)
- `top_k` : Nombre de souvenirs pertinents à injecter dans le prompt.
- `min_similarity` : Seuil de similarité minimale pour qu'un souvenir soit retenu (0.0 à 1.0).

### 4. `guardrails` (Sécurité)
- `enabled` : Active ou désactive globalement les filtres.
- `blocked_topics` : Liste de mots-clés ou sujets interdits (ex: `["politique", "religion"]`).
- `max_words` : Limite de mots par message utilisateur.
- `pii_masking` : Active le masquage des données sensibles (ex: Cartes Bancaires).
- `prompt_injection_blocking` : Détecte les tentatives de détournement d'instructions.

## Validation technique

Toute modification du fichier YAML est validée au démarrage de l'application via des modèles **Pydantic** (`atlas/config.py`). Si une valeur est hors limite ou de mauvais type, l'application refusera de démarrer en affichant une erreur explicite.
