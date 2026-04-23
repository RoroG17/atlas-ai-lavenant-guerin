# Modèle de Menaces et Sécurité

Ce document répertorie les risques identifiés pour Atlas AI et les mesures de mitigation mises en place.

## Matrice des Risques

| Menace | Impact | Mitigation |
| :--- | :--- | :--- |
| **Fuite de données (PII)** | Élevé | Masquage automatique via Guardrails + Hachage dans les logs. |
| **Prompt Injection** | Moyen | Détection de patterns suspects avant l'envoi au LLM. |
| **Sortie toxique/biaisée** | Moyen | System prompt restrictif + Paramètre de température bas (0.3). |
| **Déni de service (DoS)** | Faible | Limitation de la longueur des requêtes (max 100 mots). |
| **Exfiltration Cloud** | Élevé | Architecture 100% locale (Ollama + ChromaDB). |

## Mesures de Protection

### 1. Sécurité au repos
- Les données de la mémoire vectorielle (`./data/chroma`) et les logs (`./data/logs`) sont stockés sur le système de fichiers local. L'accès à ces dossiers doit être restreint via les permissions du système d'exploitation.

### 2. Sécurité en transit
- Les communications entre l'application Python et l'API Ollama s'effectuent via `localhost` (port 11434). Il est déconseillé d'exposer l'API Ollama sur une interface réseau publique sans authentification.

### 3. Contrôle du Persona
Le `system_prompt` définit des barrières strictes : l'assistant a pour consigne explicite de refuser toute requête hors du périmètre professionnel d'ATLAS Consulting.
