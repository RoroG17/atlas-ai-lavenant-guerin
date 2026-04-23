# Gouvernance et Conformité

Ce document décrit comment Atlas AI assure la sécurité des données et le respect des règles métier d'ATLAS Consulting.

## Respect du RGPD

La protection des données personnelles est intégrée dès la conception (*Privacy by Design*) :

1.  **Hachage des messages** : Dans les logs de monitoring (`interactions.jsonl`), le message original de l'utilisateur est remplacé par un hash (SHA-256) pour éviter le stockage de données sensibles en clair.
2.  **Exécution Locale** : Aucune donnée ne quitte le serveur ou le poste de l'utilisateur. Aucun appel vers des serveurs externes (OpenAI, Anthropic) n'est effectué par défaut.
3.  **Rétention** : Les fichiers de logs et la base de données vectorielle sont situés dans le dossier `./data/` et peuvent être purgés sur demande.

## Guardrails (Garde-fous)

Le module `atlas/guardrails.py` agit comme un pare-feu sémantique :

- **Masquage PII** : Détection automatique des formats sensibles (ex: Cartes Bancaires, Emails) et remplacement par un tag `[MASKED]`.
- **Filtrage de sujets** : Empêche l'IA de sortir de son cadre professionnel en refusant de répondre sur des sujets sensibles (politique, religion).
- **Prévention d'attaques** : Détection de patterns d'injection de prompt visant à outrepasser les consignes de sécurité.

## Politique de Rétention

- **Logs** : Conservés localement pour analyse technique. Il est recommandé de les purger tous les 90 jours.
- **Mémoire Vectorielle** : Stockée indéfiniment pour assurer la continuité de l'expérience utilisateur, sauf demande explicite de réinitialisation.
