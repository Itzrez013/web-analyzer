import requests
import typer
import json
import re


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


def load_fingerprints():
    with open("fingerprints.json", encoding="utf-8") as f:
        return json.load(f)


def fetch_site(url):
    return requests.get(url, timeout=10)


def match_html(fingerprint, html):
    pattern = fingerprint.get("html")

    if not pattern:
        return False

    try:
        return bool(re.search(pattern, html, re.I))
    except re.error:
        return False


def match_headers(fingerprint, headers):
    patterns = fingerprint.get("headers")

    if not patterns:
        return False

    for name, pattern in patterns.items():
        value = headers.get(name)

        if value is None:
            continue

        try:
            if re.search(pattern, value, re.I):
                return True
        except re.error:
            pass

    return False


def match_cookies(fingerprint, cookies):
    patterns = fingerprint.get("cookies")

    if not patterns:
        return False

    for cookie_name in patterns:
        if cookie_name in cookies:
            return True

    return False


def analyze_site(url):
    fingerprints = load_fingerprints()
    response = fetch_site(url)

    detected = []

    for name, fingerprint in fingerprints.items():

        if match_html(fingerprint, response.text):
            detected.append(name)
            continue

        if match_headers(fingerprint, response.headers):
            detected.append(name)
            continue

        if match_cookies(fingerprint, response.cookies):
            detected.append(name)
            continue

    return detected


@app.command()
def analyze(
    url: str,
):
    results = analyze_site(url)

    for technology in results:
        console.print(f"[green]✓[/green] {technology}")



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