# Atlas AI — Projet local d'assistant IA

## Objectif du projet
Ce projet vise à livrer un prototype d'assistant IA 100 % on-premise pour ATLAS Consulting. Il doit permettre aux consultants de poser des questions techniques, de conserver un historique de conversation, d'utiliser une mémoire persistante et de respecter des règles de gouvernance métier.

## Comment lancer

### Installation
1. Créez un environnement Python :
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e .
   ```

2. Installez Ollama et démarrez le service local :
   ```powershell
   ollama serve
   ```

3. Téléchargez un modèle compatible (ex. `ollama pull llama3.2:3b`) :
   ```powershell
   ollama pull llama3.2:3b
   ```

### Lancement
4. Lancez l'assistant :
   ```powershell
   atlas-chat --model llama3.2:3b
   ```
   
   **Options disponibles :**
   - `--model` : Spécifier le modèle Ollama (défaut: llama3.2:3b)
   - `--timeout` : Timeout en secondes (défaut: 30)
   - `--stream` : Activer le streaming des réponses

5. Posez vos questions et la mémoire persistera même après fermeture !

### Commandes spéciales en chat
- `/memory stats` : Affiche le nombre de souvenirs stockés
- `/memory search <query>` : Cherche dans la mémoire persistante
- `/memory clear` : Efface toute la mémoire (irreversible)

## Sprint 2 : Mémoire Persistante

### Fonctionnalités implémentées
- **Mémoire vectorielle** avec ChromaDB
- **Persistance** entre sessions (SQLite)
- **Recherche sémantique** automatique
- **Injection intelligente** de souvenirs pertinents

### Stratégie de mémorisation

**Qu'est-ce qu'on stocke ?**  
Chaque message (user et assistant) dans sa totalité, avec métadonnées (role, timestamp).

**Quand on cherche en mémoire ?**  
À chaque tour, avant de générer la réponse. Les 3-5 souvenirs les plus pertinents sont injectés dans le contexte.

**Combien de souvenirs on injecte ?**  
3-5 souvenirs par défaut, combinés avec l'historique court-terme de la session actuelle.

**Comment on gère les doublons / infos contradictoires ?**  
Via la **distance sémantique** : ChromaDB retrouve naturellement les messages similaires sans déduplication explicite. Le modèle voit les contextes et gère les potentielles contradictions.

### Architecture mémoire
```
Double-mémoire hybride:
├─ Court terme  → ChatSession.history (session actuelle)
└─ Long terme   → VectorMemory (persistant, SQLite + ChromaDB)
```

### Tests de la mémoire
```powershell
# Démo interactive (5 secondes)
python demo_acceptance_s2.py

# Suite complète (10 secondes)
python test_memory.py
```

**Critère d'acceptation validé :**
1. Session A : "Je m'appelle Dupont et je travaille sur le projet Luna pour le client Atos"
2. [Fermeture/réouverture CLI]
3. Session B : "Sur quel projet je bosse ?"

---

## Sprint 1 : Limite de la fenêtre de contexte

### Tester sans mémoire long-terme
Pour mesurer la limite de contexte pure (sans mémoire vectorielle), lancez :

```powershell
python scripts/dialog_50_tours.py
```

Ce script envoie 50 tours successifs à Ollama et affiche pour chaque tour :
- le nombre approximatif de tokens envoyés (`len(text.split()) * 1.3`)
- le nombre approximatif de tokens de complétion
- la latence de la requête

**Observation attendue :**
- Au début, le modèle conserve bien le contexte
- Au-delà d'un certain nombre de tours, la taille du prompt augmente significativement
- Les tokens envoyés augmentent à chaque tour, ce qui démontre pourquoi une **mémoire persistante est nécessaire**

---

## Structure du projet

```
atlas-ai/
├── atlas/
│   ├── __init__.py
│   ├── cli.py              # Interface CLI (atlas-chat)
│   ├── llm.py              # Client Ollama + ChatSession
│   ├── memory.py           # VectorMemory (ChromaDB)
│   ├── guardrails.py       # Règles de gouvernance (future)
│   └── monitoring.py       # Logs et monitoring (future)
├── scripts/
│   └── dialog_50_tours.py  # Test fenêtre de contexte
├── data/
│   └── memory/             # Base SQLite persistante (créée auto)
├── pyproject.toml          # Config du projet
├── README.md               # Ce fichier
├── MEMORY_STRATEGY.md      # Détails stratégie mémoire
├── SPRINT2_IMPLEMENTATION.md
├── MEMORY_QUICK_START.md
└── test_memory.py          # Tests unitaires
```

---

## Architecture

### Client Ollama
- Requêtes HTTP vers Ollama (localhost:11434)
- Support streaming
- Configurable (model, timeout)

### ChatSession
- Historique court-terme (session actuelle)
- Double-mémoire (court + long terme)
- Injection automatique de souvenirs pertinents

### VectorMemory
- Stockage ChromaDB + SQLite
- Embedding automatique (`all-MiniLM-L6-v2`)
- Recherche sémantique avec distance cosinus
- Persistance entre sessions

---

## Performance

| Aspect | Valeur |
|--------|--------|
| **Embedding dim** | 384D |
| **Latence recherche** | ~10-50ms / 100 messages |
| **Espace disque** | ~2KB / message |
| **Max souvenirs** | Illimité (SQLite) |

---

## Documentation supplémentaire

- [Stratégie de mémorisation](MEMORY_STRATEGY.md)
- [Implémentation Sprint 2](SPRINT2_IMPLEMENTATION.md)
- [Quick start mémoire](MEMORY_QUICK_START.md)
- [Checklist tâche 2](TASK2_CHECKLIST.md)

---

## Prochaines étapes

- [ ] Sprint 3 : Guardrails métier (règles d'accès)
- [ ] Résumé automatique tous les N tours
- [ ] Tags métier (client, projet, topic)
- [ ] `/forget` sélectif
- [ ] Export/Import de mémoire
- [ ] Interface web (bonus)