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
   atlas-chat
   ```
5. Posez vos questions dans la boucle interactive.