# ADR 002 : Gestion du Prompt Système et de la Configuration

*   **Status** : Accepted
*   **Date** : 2026-04-23
*   **Auteurs** : Atlas AI Team

## Contexte
L'assistant doit avoir une personnalité cohérente tout en étant capable d'intégrer des informations dynamiques issues de la mémoire vectorielle (RAG).

## Décision
Maintenir le prompt système et les paramètres du modèle dans le code applicatif (via `config/atlas.yaml`) plutôt que de les figer uniquement dans le `Modelfile` d'Ollama.

## Rationale
- **Dynamicité** : Permet d'injecter des souvenirs contextuels en temps réel dans le prompt système.
- **Agilité** : Permet de modifier la personnalité de l'assistant sans avoir à reconstruire le modèle Ollama (`ollama create`).
- **Configuration Unifiée** : Regroupe tous les paramètres (modèle, persona, mémoire, guardrails) dans un seul fichier YAML validé par Pydantic.

## Conséquences
- L'application doit gérer l'assemblage du prompt final.
- Le `Modelfile` sert de base structurelle (modèle de référence) mais n'est pas la source de vérité pour le comportement métier.
