import httpx
import json
from typing import List, Dict, Optional, Iterator, Union
import time

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self._client = httpx.Client(timeout=self.timeout)

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        Envoie une requête de chat à Ollama.

        Args:
            model: Nom du modèle
            messages: Liste des messages [{"role": "user", "content": "..."}]
            stream: Si True, retourne un itérateur pour le streaming
            **kwargs: Paramètres supplémentaires (temperature, etc.)

        Returns:
            Réponse complète ou itérateur pour streaming
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }

        try:
            if stream:
                with self._client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    return self._handle_stream(response)
            else:
                response = self._client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result["message"]["content"]

        except httpx.RequestError as e:
            raise Exception(f"Erreur lors de la requête Ollama: {e}")

    def _handle_stream(self, response) -> Iterator[str]:
        """Gère le streaming de la réponse."""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

    def close(self):
        """Ferme le client HTTP."""
        self._client.close()

class ChatSession:
    def __init__(self, model: str, client: OllamaClient):
        self.model = model
        self.client = client
        self.history: List[Dict[str, str]] = []

    def send_message(self, message: str, stream: bool = False) -> str:
        """Envoie un message et met à jour l'historique."""
        self.history.append({"role": "user", "content": message})

        if stream:
            response_parts = []
            for part in self.client.chat(self.model, self.history, stream=True):
                response_parts.append(part)
                print(part, end="", flush=True)
            response = "".join(response_parts)
            print()  # Nouvelle ligne après streaming
        else:
            response = self.client.chat(self.model, self.history, stream=False)

        self.history.append({"role": "assistant", "content": response})
        return response

    def get_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique des messages."""
        return self.history.copy()