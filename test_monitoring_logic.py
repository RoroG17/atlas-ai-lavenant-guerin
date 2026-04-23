import os
import json
from atlas.monitoring import traced

# 1. On définit une fonction qui simule un appel LLM
# Elle doit retourner (réponse, prompt_tokens, completion_tokens) pour matcher chat_with_metrics
@traced(log_path="./data/logs/test_interactions.jsonl")
def mock_llm_call(model, messages, system=None):
    print(f"--- Simulation d'appel LLM pour le modèle {model} ---")
    return "Ceci est une réponse simulée.", 10, 20

def test_logger():
    log_file = "./data/logs/test_interactions.jsonl"
    
    # Nettoyage si le fichier existe déjà
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # 2. On effectue des appels
    messages = [{"role": "user", "content": "Bonjour Atlas !"}]
    mock_llm_call("test-model", messages)
    
    # Appel avec un souvenir (system prompt)
    mock_llm_call("test-model", messages, system="Un souvenir injecté")

    # 3. Vérification du fichier
    if os.path.exists(log_file):
        print(f"\n[SUCCÈS] Le fichier {log_file} a été créé.")
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"Nombre d'entrées loguées : {len(lines)}")
            
            for i, line in enumerate(lines):
                data = json.loads(line)
                print(f"\n--- Log #{i+1} ---")
                print(f"Timestamp : {data['timestamp']}")
                print(f"Modèle    : {data['model']}")
                print(f"Tokens    : {data['prompt_tokens']} prompt / {data['completion_tokens']} completion")
                print(f"User Msg  : {data['user_message']} (Hashé)")
                print(f"Mem Hits  : {data['memory_hits']}")
    else:
        print("\n[ERREUR] Le fichier de log n'a pas été généré.")

if __name__ == "__main__":
    test_logger()
