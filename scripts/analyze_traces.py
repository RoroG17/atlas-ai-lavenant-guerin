import pandas as pd
import json
import os
from pathlib import Path

def analyze_traces(log_path: str = "./data/logs/interactions.jsonl"):
    """
    Analyse les logs d'interaction (Voie A) et génère des métriques agrégées.
    """
    path = Path(log_path)
    if not path.exists():
        print(f"Le fichier {log_path} n'existe pas. Aucune trace à analyser.")
        return

    # Chargement du JSONL
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                    
    if not data:
        print("Aucune donnée valide trouvée dans les logs.")
        return

    df = pd.DataFrame(data)

    print("\n" + "="*50)
    print("📊 RAPPORT D'ANALYSE DES TRACES (Voie A)")
    print("="*50)

    # 1. Nombre total d'interactions
    total_interactions = len(df)
    print(f"\n1. Total des interactions : {total_interactions}")

    # 2. Latence moyenne
    if 'latency_ms' in df.columns:
        avg_latency = df['latency_ms'].mean()
        print(f"2. Latence moyenne : {avg_latency:.2f} ms")
    else:
        print("2. Latence moyenne : N/A")

    # 3. Consommation totale de tokens
    if 'prompt_tokens' in df.columns and 'completion_tokens' in df.columns:
        total_tokens = df['prompt_tokens'].sum() + df['completion_tokens'].sum()
        print(f"3. Consommation totale de tokens : {total_tokens}")
    else:
        print("3. Consommation totale de tokens : N/A")

    # 4. Statistiques sur la mémoire (Memory Hits)
    if 'memory_hits' in df.columns:
        total_hits = df['memory_hits'].sum()
        avg_hits = df['memory_hits'].mean()
        print(f"4. Memory Hits : Total={total_hits}, Moyenne={avg_hits:.2f} par requête")

    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    analyze_traces()
