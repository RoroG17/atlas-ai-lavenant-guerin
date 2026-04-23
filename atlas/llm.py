import httpx
import json
import time
from typing import List, Dict, Optional, Iterator, Union, Tuple
from atlas.memory import VectorMemory
from atlas.monitoring import traced

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
        Envoie une requête de chat à Ollama (ancien format).
        Retourne seulement le contenu (pour compatibilité).

        Args:
            model: Nom du modèle
            messages: Liste des messages [{"role": "user", "content": "..."}]
            stream: Si True, retourne un itérateur pour le streaming
            **kwargs: Paramètres supplémentaires (temperature, system, etc.)

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

    @traced(log_path="./data/logs/interactions.jsonl")
    def chat_with_metrics(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Tuple[str, int, int]:
        """
        Envoie une requête de chat à Ollama et retourne les véritables métriques.
        
        Returns:
            Tuple (response, prompt_eval_count, eval_count) depuis Ollama
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
                raise NotImplementedError("chat_with_metrics n'est pas compatible avec stream=True")
            else:
                response = self._client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extraire les tokens réels depuis Ollama
                prompt_tokens = result.get("prompt_eval_count", 0)
                completion_tokens = result.get("eval_count", 0)
                content = result["message"]["content"]
                
                return content, prompt_tokens, completion_tokens

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
    def __init__(self, model: str, client: OllamaClient, enable_memory: bool = True):
        self.model = model
        self.client = client
        self.history: List[Dict[str, str]] = []
        
        # Initialiser la mémoire vectorielle
        self.enable_memory = enable_memory
        if enable_memory:
            self.memory = VectorMemory()
        else:
            self.memory = None

    def send_message(self, message: str, stream: bool = False) -> str:
        """Envoie un message et met à jour l'historique."""
        self.history.append({"role": "user", "content": message})

        # Préparer les messages à envoyer au modèle
        messages_to_send = self.history.copy()
        
        # Injecter les souvenirs pertinents dans le contexte
        if self.memory:
            memories = self.memory.get_memories_as_text(message, n_results=3)
            
            # Ajouter les souvenirs au contexte système si pertinents
            if memories:
                # Insérer les souvenirs après le premier message ou en système
                messages_to_send.insert(0, {
                    "role": "system",
                    "content": memories
                })

        # Envoyer la requête
        if stream:
            response_parts = []
            for part in self.client.chat(self.model, messages_to_send, stream=True):
                response_parts.append(part)
                print(part, end="", flush=True)
            response = "".join(response_parts)
            print()  # Nouvelle ligne après streaming
        else:
            response, prompt_tokens, completion_tokens = self.client.chat_with_metrics(self.model, messages_to_send, stream=False)

        # Stocker le message de l'utilisateur et la réponse en mémoire
        if self.memory:
            self.memory.store_message("user", message)
            self.memory.store_message("assistant", response)

        self.history.append({"role": "assistant", "content": response})
        return response

    def get_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique des messages."""
        return self.history.copy()