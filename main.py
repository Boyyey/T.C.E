import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from synthetic_mind.core import SyntheticMind

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def run(prompt: Optional[str] = typer.Option(None, "--prompt", "-p"), trace: bool = typer.Option(False, "--trace")):
    mind = SyntheticMind(trace=trace)
    if prompt is None:
        console.print(Panel.fit("Enter interactive mode. Type 'exit' to quit.", title="Synthetic Mind"))
        while True:
            user = console.input("[bold cyan]You[/]: ")
            if user.strip().lower() in {"exit", "quit"}:
                break
            response = mind.step(user)
            console.print(f"[bold green]Mind[/]: {response}")
    else:
        response = mind.step(prompt)
        if trace:
            console.rule("Trace JSON")
            console.print_json(data=mind.last_trace)
        console.print(response)


if __name__ == "__main__":
    app()
