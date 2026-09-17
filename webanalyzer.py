import requests
import typer

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

app = typer.Typer()
console = Console()


@app.callback()
def main():
    pass


def text_color(stat):
    if stat == 200:
        return "[green]"
    if stat == 404:
        return "[red]"
    return "[yellow]"


@app.command()
def scan(
    host: str,
    urls: str = typer.Argument(""),
    file: bool = typer.Option(False, "-f", "--file"),
):
    if not host:
        host = input("give me your host name: ")

    table = Table(title="Scan Results")

    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Size")

    console.print(
        Panel(
            f"Host: {host}\n"
            f"URLs given (file name or plain text): {urls}",
            title="Info"
        )
    )

    if file:
        with open(urls, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        with Progress() as progress:
            task = progress.add_task(
                "[green]Scanning...",
                total=len(lines)
            )

            for line in lines:
                try:
                    res = requests.get(
                        f"{host.rstrip('/')}/{line.lstrip('/')}",
                        timeout=10
                    )

                    color = text_color(res.status_code)

                    table.add_row(
                        f"{color}{host.rstrip('/')}/{line.lstrip('/')}",
                        f"{color}{res.status_code}",
                        f"{color}{len(res.content) // 1024} KB"
                    )

                except requests.RequestException:
                    table.add_row(
                        f"[red]{host.rstrip('/')}/{line.lstrip('/')}",
                        "[red]ERROR",
                        "-"
                    )

                progress.update(task, advance=1)

    else:
        try:
            res = requests.get(
                f"{host.rstrip('/')}/{urls.lstrip('/')}",
                timeout=10
            )

            color = text_color(res.status_code)

            table.add_row(
                f"{color}{host.rstrip('/')}/{urls.lstrip('/')}",
                f"{color}{res.status_code}",
                f"{color}{len(res.content) // 1024} KB"
            )

        except requests.RequestException:
            table.add_row(
                f"[red]{host.rstrip('/')}/{urls.lstrip('/')}",
                "[red]ERROR",
                "-"
            )

    console.print(table)


if __name__ == "__main__":
    app()