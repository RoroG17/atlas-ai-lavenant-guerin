# ADR 001 : Choix d'Ollama comme moteur d'inférence

*   **Status** : Accepted
*   **Date** : 2026-04-23
*   **Auteurs** : Atlas AI Team

## Contexte
Le projet nécessite l'exécution locale de modèles de langage (LLM) pour des raisons de confidentialité (données d'ATLAS Consulting) et d'indépendance vis-à-vis des API tierces coûteuses.

## Décision
Utiliser **Ollama** comme moteur d'inférence principal.

## Rationale
- **Exécution Locale** : Garantit que les données ne quittent jamais l'infrastructure de l'entreprise.
- **Simplicité** : Gestion facile des modèles (pull, run, create) via une interface simple.
- **API Standard** : Offre une API HTTP compatible facilitant l'intégration avec le code Python.
- **Performance** : Optimisé pour l'exécution sur du matériel grand public (CPU/GPU).

## Conséquences
- Nécessite l'installation d'Ollama sur le poste de l'utilisateur.
- Dépendance à la disponibilité des modèles dans le registre Ollama (ou via Modelfile).
