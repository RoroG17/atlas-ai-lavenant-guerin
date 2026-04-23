from atlas.llm import OllamaClient, ChatSession
import time


def run_dialogue(turns: int = 50, model: str = "llama3.2:3b", timeout: int = 30) -> None:
    client = OllamaClient(base_url="http://localhost:11434", timeout=timeout)
    # Désactiver la mémoire pour ce test (mesure pure de la fenêtre de contexte)
    session = ChatSession(model, client, enable_memory=False)

    print(f"Lancement d'un dialogue de {turns} tours avec le modèle {model}...\n")
    print("Tour | Prompt tokens | Completion tokens | Latency (ms)")
    print("-----|----------------|------------------|--------------")

    for turn in range(turns):
        user_message = f"Tour {turn + 1}: Rappelle-moi le tour précédent et compte jusqu'à {turn + 1}."
        session.history.append({"role": "user", "content": user_message})

        prompt_tokens = sum(len(msg["content"].split()) for msg in session.history) * 1.3

        start = time.time()
        response = session.client.chat(session.model, session.history, stream=False)
        latency = (time.time() - start) * 1000

        completion_tokens = len(response.split()) * 1.3
        session.history.append({"role": "assistant", "content": response})

        print(f"{turn + 1:>4} | {prompt_tokens:>13.0f} | {completion_tokens:>16.0f} | {latency:>12.0f}")

    client.close()


if __name__ == "__main__":
    run_dialogue()