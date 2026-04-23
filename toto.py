import httpx
import json

class OllamaClient:
    def __init__(self, model="llama3.2:3b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/chat"
        self.messages = []

    def chat(self, user_input):
        # Ajouter le message utilisateur à l'historique
        self.messages.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": True
        }

        full_response = ""
        
        # Appel de l'API avec streaming
        with httpx.stream("POST", self.base_url, json=payload, timeout=60.0) as response:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        content = data["message"].get("content", "")
                        print(content, end="", flush=True)
                        full_response += content
                    if data.get("done"):
                        break
        
        print("\n") # Retour à la ligne après la réponse complète
        
        # Ajouter la réponse du modèle à l'historique
        self.messages.append({"role": "assistant", "content": full_response})
        return full_response

# Exemple d'utilisation
if __name__ == "__main__":
    client = OllamaClient(model="llama3.2:3b")
    print("Atlas Chat démarré (tapez 'exit' pour quitter)")
    
    while True:
        user_text = input("Vous: ")
        if user_text.lower() == "exit":
            break
        client.chat(user_text)