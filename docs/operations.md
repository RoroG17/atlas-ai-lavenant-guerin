# Guide des Opérations (Runbook)

Ce document décrit les tâches courantes pour opérer et maintenir l'assistant Atlas AI.

## Démarrer et Arrêter l'assistant

### Démarrage
Assurez-vous qu'Ollama est lancé, puis exécutez :
```powershell
python -m atlas.cli
```

### Arrêt
Tapez `au revoir`, `exit` ou utilisez `Ctrl+C` pour quitter la console interactive.

## Maintenance de la Mémoire

### Purger la mémoire vectorielle
Si l'assistant commence à avoir des comportements incohérents basés sur de vieux souvenirs, vous pouvez réinitialiser sa mémoire :
```powershell
Remove-Item -Recurse ./data/chroma/
```
*Note : Cela supprimera tous les souvenirs appris. L'assistant repartira de zéro au prochain démarrage.*

## Maintenance des Logs

### Rotation des logs
Les logs s'accumulent dans `./data/logs/interactions.jsonl`. Pour repartir sur un fichier propre sans perdre l'historique :
1.  Renommez le fichier actuel (ex: `interactions_archive_2026.jsonl`).
2.  L'application créera un nouveau fichier `interactions.jsonl` automatiquement lors du prochain appel.

## Rollback (Retour arrière)

En cas de problème après une mise à jour de configuration :
1.  Consultez les erreurs de validation au démarrage.
2.  Restaurez la version précédente de `config/atlas.yaml` à partir de votre gestionnaire de version (Git).
3.  Vérifiez que le modèle Ollama spécifié dans la config est toujours présent : `ollama list`.
