import requests
import typer
import json
import re


from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

app = typer.Typer(pretty_exceptions_enable=True,rich_markup_mode="rich",no_args_is_help=True,context_settings={"help_option_names": ["-h", "--help"]},add_completion=False)
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


def format_size(size):
    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"

    return f"{size / (1024 ** 2):.2f} MB"


@app.command()
def scan(
    host: str = typer.Argument(..., help="Target website"),
    urls: str = typer.Argument("", help="URL or file containing URLs"),
    file: bool = typer.Option(
        False,
        "-f",
        "--file",
        help="Treat the URLs argument as a file.",
    ),
    size: bool = typer.Option(
        False,
        "-s",
        "--size",
        help="Show response size.",
    ),
):
    """
    [bold cyan]Scan a website for URLs.[/bold cyan]

    Send HTTP requests to the specified URLs and display
    their status codes.

    [bold yellow]Examples:[/bold yellow]

        [green]webanalyzer scan https://example.com admin[/green]

        [green]webanalyzer scan -f https://example.com urls.txt[/green]

        [green]webanalyzer scan -s https://example.com admin[/green]
    """
    
    if not host:
        host = input("give me your host name: ")

    table = Table(title="Scan Results")

    table.add_column("URL")
    table.add_column("Status")
    if size:
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

                    display_url = f"{color}{host.rstrip('/')}/{line.lstrip('/')}"
                    stat = f"{color}{res.status_code}"


                    if size:
                        table.add_row(
                            display_url,
                            stat,
                            f"{color}{format_size(len(res.content))}",
                        )
                    else:
                        table.add_row(
                            display_url,
                            stat,
                        )

                except requests.RequestException:
                    table.add_row(
                        f"[red]{display_url.rstrip('/')}/{line.lstrip('/')}",
                        f"[red]ERROR",
                    )

                progress.update(task, advance=1)

    else:
        try:
            res = requests.get(
                f"{host.rstrip('/')}/{urls.lstrip('/')}",
                timeout=10
            )

            color = text_color(res.status_code)

            display_url = f"{color}{host.rstrip('/')}/{urls.lstrip('/')}"
            stat = f"{color}{res.status_code}"


            if size:
                table.add_row(
                    display_url,
                    stat,
                    f"{color}{format_size(len(res.content))}",
                )
            else:
                table.add_row(
                    display_url,
                    stat,
                )
        except requests.RequestException:
            table.add_row(
                f"[red]{host.rstrip('/')}/{urls.lstrip('/')}",
                "[red]ERROR",
            )

    console.print(table)




if __name__ == "__main__":
    app()