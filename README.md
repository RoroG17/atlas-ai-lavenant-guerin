# Atlas AI — Projet local d'assistant IA

## Objectif du projet
Ce projet vise à livrer un prototype d'assistant IA 100 % on-premise pour ATLAS Consulting. Il doit permettre aux consultants de poser des questions techniques, de conserver un historique de conversation, d'utiliser une mémoire persistante et de respecter des règles de gouvernance métier.

## Comment lancer
1. Créez un environnement Python :
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e .
   ```
2. Installez Ollama et démarrez le service local.
3. Téléchargez un modèle compatible avec votre machine (ex. `ollama pull llama3.2:3b`).
4. Lancez l'assistant :
   ```powershell
   atlas-chat --model llama3.2:3b
   ```
   Options disponibles :
   - `--model` : Spécifier le modèle Ollama
   - `--timeout` : Timeout en secondes (défaut: 30)
   - `--stream` : Activer le streaming des réponses (bonus)
5. Posez vos questions dans la boucle interactive.

## Tester la limite de la fenêtre de contexte
Pour mesurer la limite de contexte, lancez un dialogue de 50 tours avec le script suivant :

```powershell
python scripts/dialog_50_tours.py
```
Voici les résultats de la mesure des tokens 
Tour | Prompt tokens | Completion tokens | Latency (ms)
-----|----------------|------------------|--------------
   1 |            13  |               96 |        14864
   2 |           122  |               75 |         7677
   3 |           211  |              127 |        12631
   4 |           351  |              144 |        14423
   5 |           508  |              179 |        19481
   6 |           701  |              194 |        26982

Ce script envoie 50 tours successifs à Ollama et affiche pour chaque tour :
- le nombre approximatif de tokens envoyés (`len(text.split()) * 1.3`)
- le nombre approximatif de tokens de complétion
- la latence de la requête

### Observation attendue
- au début, le modèle conserve bien le contexte et répond de façon cohérente
- au-delà d'un certain nombre de tours, la taille du prompt augmente et la cohérence peut diminuer
- les tokens envoyés augmentent à chaque tour, ce qui montre pourquoi une mémoire longue est nécessaire pour maintenir une qualité stable

### Statégie de mémorisation

Qu'est-ce qu'on stocke ? 
On a décidé de stocker des résumers des réponses associées à des mots clés qui sont dans la question

Quand on cherche en mémoire ? 
Seulements sur les mots clés de la question

Combien de souvenir on injecte dans le prompt ?
1

Comment on gère les doublons / infos contradictoires ?
On supprime les doublons et pour les contradictions, on garde la dernière réponse.