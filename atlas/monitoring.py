# Module de monitoring et télémétrie
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from functools import wraps
import hashlib
import os

def traced(log_path: str):
    """
    Décorateur pour tracer les appels LLM et écrire un log structuré en JSONL.
    """
    # Un ID de session unique par instance de décorateur
    session_id = str(uuid.uuid4())

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            
            # Appeler la fonction cible
            result = func(*args, **kwargs)
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            # Extraction des arguments de la fonction pour construire la trace
            # args[0] est self (OllamaClient), args[1] est model, args[2] est messages
            model = kwargs.get('model') if 'model' in kwargs else (args[1] if len(args) > 1 else 'unknown')
            messages = kwargs.get('messages') if 'messages' in kwargs else (args[2] if len(args) > 2 else [])
            
            # Le message utilisateur est le dernier avec le rôle "user"
            user_message = ""
            for m in reversed(messages):
                if m.get('role') == 'user':
                    user_message = m.get('content', '')
                    break
            
            # Hachage du message pour le RGPD
            user_msg_hash = hashlib.sha256(user_message.encode('utf-8')).hexdigest()[:8]
            
            # Décompte des "memory_hits"
            memory_hits = 1 if kwargs.get('system') else 0
            if memory_hits == 0:
                for m in messages:
                    if m.get('role') == 'system':
                        memory_hits += 1
            
            # Extraction des retours. On s'attend à (content, prompt_tokens, completion_tokens)
            if isinstance(result, tuple) and len(result) >= 3:
                content = result[0]
                prompt_tokens = result[1]
                completion_tokens = result[2]
            else:
                content = str(result)
                prompt_tokens = 0
                completion_tokens = 0
            
            # Construire la trace au format attendu
            trace = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency_ms": round(latency_ms, 2),
                "user_message": f"[HASH:{user_msg_hash}]",
                "assistant_message": content,
                "memory_hits": memory_hits
            }
            
            # Écrire la ligne en JSONL
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace, ensure_ascii=False) + "\n")
                
            return result
        return wrapper
    return decorator