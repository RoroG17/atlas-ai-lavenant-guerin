# Guide d'Installation

Ce guide vous permet de configurer l'environnement **Atlas AI** sur un poste Windows.

## Prérequis

1.  **Python 3.10+** : [Télécharger Python](https://www.python.org/downloads/).
2.  **Ollama** : [Télécharger Ollama](https://ollama.com/download).
3.  **Modèle de base** : Téléchargez le modèle `llama3.2:3b` via Ollama :
    ```powershell
    ollama pull llama3.2:3b
    ```

## Installation pas-à-pas

### 1. Cloner le projet
```powershell
git clone https://github.com/votre-repo/atlas-ai.git
cd atlas-ai
```

### 2. Créer l'environnement virtuel
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Installer les dépendances
```powershell
pip install -e .
pip install PyYAML pydantic chromadb rich typer pandas pytest
```

### 4. (Optionnel) Créer le modèle dérivé 'atlas'
Si vous souhaitez utiliser le modèle pré-configuré dans Ollama :
```powershell
ollama create atlas -f Modelfile
```

## Vérification de l'installation

Lancez l'assistant pour vérifier que tout fonctionne :
```powershell
python -m atlas.cli
```

Si vous voyez le message de bienvenue, l'installation est réussie !
