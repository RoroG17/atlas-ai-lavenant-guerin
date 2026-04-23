# Monitoring et Observabilité

L'observabilité est un pilier d'Atlas AI, permettant de suivre la performance et l'usage du système en production.

## Logs Structurés (Voie A)

Chaque interaction utilisateur est enregistrée de manière structurée dans `./data/logs/interactions.jsonl`.

### Format d'une trace
Chaque ligne contient un objet JSON avec les champs suivants :
- `timestamp` : Date ISO 8601.
- `session_id` : Identifiant unique de la session.
- `model` : Modèle utilisé.
- `prompt_tokens` / `completion_tokens` : Consommation réelle.
- `latency_ms` : Temps de réponse du LLM.
- `user_message` : Message utilisateur (haché pour la confidentialité).
- `assistant_message` : Réponse complète.
- `memory_hits` : Nombre de souvenirs injectés via le RAG.

## Analyse des performances

Un script utilitaire permet d'extraire des métriques agrégées à partir de ces traces :

```powershell
python scripts/analyze_traces.py
```

**Métriques produites :**
1.  **Latence moyenne** : Permet de détecter une dégradation des performances locales.
2.  **Consommation de tokens** : Pour estimer la charge et les futurs coûts (si passage sur API payante).
3.  **Taux de succès du RAG** : Nombre moyen de souvenirs utiles par requête.

## Observabilité avancée (Voie B)

Pour des déploiements en entreprise, le système est compatible avec **Langfuse** (via un décorateur de tracing dédié), offrant des tableaux de bord visuels et une gestion hiérarchique des traces (Traces > Spans > LLM Calls).
