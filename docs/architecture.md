# Architecture & Décisions

## Décisions sur la configuration du modèle (Modelfile vs YAML)

Suite à la création du modèle dérivé `atlas` via Ollama (`Modelfile`), voici les décisions d'architecture concernant la gestion de la configuration et des prompts.

### 1. Le system prompt doit-il vivre dans le Modelfile ou dans le code applicatif ?

**Décision : Dans le code applicatif (fichier `atlas.yaml`)**
**Pourquoi ?** 
- **Flexibilité et agilité** : Mettre le system prompt dans le code applicatif ou un fichier de configuration permet de modifier la personnalité ou le comportement de l'assistant dynamiquement, sans nécessiter un rebuid du modèle avec la commande `ollama create`.
- **Injection de contexte (RAG/Mémoire)** : Notre application `atlas-ai` construit le prompt dynamiquement. Le système concatène le prompt de personnalité avec des souvenirs extraits de la mémoire vectorielle. Si le prompt était figé dans le Modelfile, nous n'aurions pas la maîtrise complète du formatage final envoyé à Ollama lors de l'injection en temps réel.
- **Séparation des préoccupations** : Le modèle LLM (Ollama) sert de moteur brut, l'application métier porte la logique de persona.

### 2. Quel impact si un utilisateur change la config YAML mais pas le Modelfile ?

**Impact : Surcharge API (Priorité à la configuration d'exécution)**
- **Les paramètres (temperature, top_p, num_ctx)** passés via l'API (grâce au YAML injecté dans le payload `options`) **surchargeront toujours** les valeurs encodées dans le Modelfile. L'utilisateur obtiendra donc bien les effets de sa configuration applicative, ce qui est l'effet voulu.
- **Le System Prompt** : Si l'utilisateur définit un system prompt dans le `Modelfile` ET dans le payload de la requête API, le comportement dépend du moteur (Ollama remplace généralement le system prompt natif par celui fourni dans la requête API, mais cela peut introduire des comportements flous ou résiduels). 
- **Risque d'incompréhension** : Le principal risque est la confusion du mainteneur (des paramètres dédoublés créent une ambiguïté sur "quelle est la source de vérité"). D'où la nécessité de choisir une seule source.

### 3. Votre CLI doit-elle pointer vers `atlas` ou vers `llama3.2:3b` + system prompt côté code ?

**Décision : Pointeur vers `llama3.2:3b` avec la configuration portée côté code**
- **Simplicité de déploiement** : Si on pointe vers `atlas`, cela impose à chaque nouveau développeur ou utilisateur de l'application de builder au préalable le Modelfile localement. En pointant vers le modèle natif `llama3.2:3b` avec le `system_prompt` côté code, on réduit drastiquement les étapes d'installation.
- **Source de Vérité unique** : Laissons la configuration YAML régir le comportement complet. Le `Modelfile` n'est utile que si l'on souhaite distribuer un LLM pré-packagé à travers un réseau sans client lourd devant, ce qui n'est pas notre architecture actuelle (nous avons une belle CLI interactive riche et connectée à une BDD vectorielle).
