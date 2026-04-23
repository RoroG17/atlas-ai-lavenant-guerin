import typer
from rich.console import Console
from rich.prompt import Prompt
from atlas.llm import OllamaClient, ChatSession

app = typer.Typer()
console = Console()

@app.command()
def chat(
    model: str = typer.Option("llama3.2:3b", help="Modèle Ollama à utiliser"),
    timeout: int = typer.Option(30, help="Timeout en secondes pour les requêtes"),
    stream: bool = typer.Option(False, help="Activer le streaming des réponses")
):
    """
    Lance l'assistant IA Atlas en mode interactif.
    """
    console.print("[bold green]Bienvenue dans Atlas AI ![/bold green]")
    console.print(f"Modèle: {model}")
    console.print("Tapez 'quit' ou 'exit' pour quitter.\n")

    try:
        client = OllamaClient(timeout=timeout)
        session = ChatSession(model, client)

        while True:
            user_input = Prompt.ask("[bold blue]Vous[/bold blue]")

            if user_input.lower() in ['quit', 'exit']:
                console.print("[yellow]Au revoir ![/yellow]")
                client.close()
                break

            if not user_input.strip():
                continue

            try:
                console.print("[bold red]Atlas[/bold red]", end=": ")
                response = session.send_message(user_input, stream=stream)
                if not stream:
                    console.print(response)

            except Exception as e:
                console.print(f"[red]Erreur: {e}[/red]")

    except Exception as e:
        console.print(f"[red]Erreur d'initialisation: {e}[/red]")
        raise typer.Exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    app()