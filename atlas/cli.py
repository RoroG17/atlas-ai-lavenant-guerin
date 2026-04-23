import typer
from rich.console import Console
from rich.prompt import Prompt
from atlas.llm import OllamaClient, ChatSession
from atlas.memory import VectorMemory

app = typer.Typer()
console = Console()

def handle_command(command: str, session: ChatSession):
    """Traite les commandes spéciales (commençant par /)"""
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == "/memory":
        if len(parts) < 2:
            console.print("[cyan]Sous-commandes:/[/cyan]")
            console.print("  /memory stats     - Affiche les stats de mémoire")
            console.print("  /memory clear     - Efface toute la mémoire")
            console.print("  /memory search <query> - Cherche dans la mémoire")
        elif parts[1] == "stats":
            if session.memory:
                stats = session.memory.get_collection_stats()
                console.print(f"[cyan]📊 Statistiques mémoire:[/cyan]")
                console.print(f"  Total messages: {stats['total_messages']}")
                console.print(f"  Chemin: {stats['memory_path']}")
            else:
                console.print("[red]Mémoire désactivée[/red]")
        elif parts[1] == "clear":
            if session.memory:
                session.memory.clear_all()
                console.print("[green]✅ Mémoire effacée[/green]")
            else:
                console.print("[red]Mémoire désactivée[/red]")
        elif parts[1] == "search" and len(parts) > 2:
            query = " ".join(parts[2:])
            if session.memory:
                memories = session.memory.retrieve_memories(query, n_results=3)
                if memories:
                    console.print(f"[cyan]🔍 Résultats pour: '{query}'[/cyan]")
                    for i, mem in enumerate(memories, 1):
                        console.print(f"\n{i}. [{mem['metadata'].get('role', 'unknown').upper()}]")
                        console.print(f"   {mem['content'][:150]}...")
                        console.print(f"   Timestamp: {mem['metadata'].get('timestamp', 'N/A')}")
                else:
                    console.print("[yellow]Aucun souvenir trouvé[/yellow]")
    else:
        console.print(f"[red]Commande inconnue: {cmd}[/red]")
        console.print("[cyan]Tapez / pour voir les commandes disponibles[/cyan]")

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
        session = ChatSession(model, client, enable_memory=True)

        while True:
            user_input = Prompt.ask("[bold blue]Vous[/bold blue]")

            if user_input.lower() in ['quit', 'exit']:
                console.print("[yellow]Au revoir ![/yellow]")
                client.close()
                break

            if not user_input.strip():
                continue

            # Commandes spéciales
            if user_input.lower().startswith("/"):
                handle_command(user_input, session)
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