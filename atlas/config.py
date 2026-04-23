import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

class ModelConfig(BaseModel):
    name: str = "llama3.2:3b"
    temperature: float = Field(0.3, ge=0, le=2)
    top_p: float = Field(0.9, ge=0, le=1)
    num_ctx: int = Field(4096, gt=0)

class PersonaConfig(BaseModel):
    name: str = "Atlas"
    system_prompt: str = "Tu es Atlas, assistant IA."

class MemoryConfig(BaseModel):
    top_k: int = Field(5, gt=0)
    min_similarity: float = Field(0.7, ge=0, le=1)

class GuardrailsConfig(BaseModel):
    enabled: bool = True
    blocked_topics: List[str] = []

class AtlasConfig(BaseModel):
    model: ModelConfig = ModelConfig()
    persona: PersonaConfig = PersonaConfig()
    memory: MemoryConfig = MemoryConfig()
    guardrails: GuardrailsConfig = GuardrailsConfig()

def load_config(config_path: str = "config/atlas.yaml") -> AtlasConfig:
    """Charge et valide la configuration depuis un fichier YAML."""
    path = Path(config_path)
    
    if not path.exists():
        print(f"[Config] Fichier {config_path} introuvable. Utilisation des valeurs par défaut.")
        return AtlasConfig()
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f) or {}
            return AtlasConfig(**raw_config)
    except ValidationError as e:
        print(f"\n[ERREUR] Configuration invalide dans {config_path} :")
        for error in e.errors():
            loc = " -> ".join(str(l) for l in error['loc'])
            print(f"  - {loc} : {error['msg']}")
        print("\nVeuillez corriger le fichier config/atlas.yaml.\n")
        raise SystemExit(1)
    except Exception as e:
        print(f"[Config] Erreur inattendue lors du chargement : {e}")
        return AtlasConfig()

# Instance globale de configuration
_config_obj = load_config()

# Pour garder la compatibilité avec le reste du code qui utilise CONFIG["key"]
# On convertit le modèle en dictionnaire
CONFIG = _config_obj.model_dump()

