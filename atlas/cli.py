import typer
from rich.console import Console
from rich.prompt import Prompt
from atlas.llm import OllamaClient, ChatSession
from atlas.memory import VectorMemory          # import corrigé

app = typer.Typer()
console = Console()


def handle_command(command: str, session: ChatSession, memory: VectorMemory):
    parts = command.split()
    cmd = parts[0].lower()

    if cmd == "/memory":
        if len(parts) < 2:
            console.print("[cyan]Sous-commandes :[/cyan]")
            console.print("  /memory stats              - Stats de mémoire")
            console.print("  /memory clear              - Efface la mémoire")
            console.print("  /memory search <query>     - Cherche un souvenir")

        elif parts[1] == "stats":
            stats = memory.get_collection_stats()
            console.print(f"[cyan]Mémoire :[/cyan] {stats['total_memories']} souvenir(s)") # ← total_memories
            console.print(f"  Chemin : {stats['memory_path']}")

        elif parts[1] == "clear":
            memory.clear_all()
            console.print("[green]✓ Mémoire effacée[/green]")

        elif parts[1] == "search" and len(parts) > 2:
            query = " ".join(parts[2:])
            result = memory.retrieve_best_memory(query)   # ← nouvelle API
            if result:
                console.print(f"[cyan]Meilleur souvenir pour '{query}' :[/cyan]")
                console.print(result)
            else:
                console.print("[yellow]Aucun souvenir trouvé[/yellow]")
    else:
        console.print(f"[red]Commande inconnue : {cmd}[/red]")


@app.command()
def chat(
    model: str = typer.Option("llama3.2:3b", help="Modèle Ollama à utiliser"),
    timeout: int = typer.Option(30, help="Timeout en secondes"),
    stream: bool = typer.Option(False, help="Activer le streaming"),
):
    """Lance l'assistant IA Atlas en mode interactif."""
    console.print("[bold green]Bienvenue dans Atlas AI ![/bold green]")
    console.print(f"Modèle : {model} | Mémoire : activée\n")

    client = OllamaClient(timeout=timeout)
    session = ChatSession(model, client)
    memory = VectorMemory()                        # ← instancié séparément

    while True:
        try:
            user_input = Prompt.ask("[bold blue]Vous[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Au revoir ![/yellow]")
            break

        if user_input.lower() in ("quit", "exit"):
            console.print("[yellow]Au revoir ![/yellow]")
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            handle_command(user_input, session, memory)
            continue

        # ── Injection mémoire dans le prompt système ──────────────────────
        souvenir = memory.retrieve_best_memory(user_input)
        system = None
        if souvenir:
            system = f"Contexte issu de tes souvenirs :\n{souvenir}"
            console.print(f"[dim]Souvenir injecté[/dim]")

        # ── Appel LLM ─────────────────────────────────────────────────────
        try:
            console.print("[bold red]Atlas[/bold red]", end=" : ")
            session.history.append({"role": "user", "content": user_input})
            response = session.client.chat(
                session.model, session.history, stream=stream, system=system
            )
            session.history.append({"role": "assistant", "content": response})

            if not stream:
                console.print(response)

            # ── Stockage en mémoire ───────────────────────────────────────
            memory.store_exchange(user_input, response)

        except Exception as e:
            console.print(f"[red]Erreur : {e}[/red]")
            session.history.pop()           # retire le message user non traité

    client.close()


if __name__ == "__main__":
    app()