"""Command-line interface for Meta Ad Library Scraper."""

import json
import csv
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import database
from .scraper import collect_ads
from .downloader import download_videos
from .config import DEFAULT_COUNTRY, MAX_WORKERS

console = Console()


@click.group()
def cli():
    """Meta Ad Library Video Scraper - Download video ads to GCS."""
    pass


@cli.command()
@click.argument("query")
@click.option("--country", "-c", default=DEFAULT_COUNTRY, help="Country code (US, IN, etc.)")
@click.option("--limit", "-l", type=int, default=None, help="Max ads to collect")
@click.option("--headless/--no-headless", default=True, help="Run browser in headless mode")
def collect(query: str, country: str, limit: int, headless: bool):
    """Search and collect video ad URLs from Meta Ad Library."""
    console.print(f"[bold blue]Meta Ad Library Scraper[/bold blue]")
    console.print()
    
    ads = collect_ads(query, country, limit, headless)
    
    console.print()
    console.print(f"[green]Collected {len(ads)} video ads[/green]")
    console.print(f"[dim]Run 'download' command to download videos[/dim]")


@cli.command()
@click.option("--workers", "-w", type=int, default=MAX_WORKERS, help="Number of parallel workers")
@click.option("--limit", "-l", type=int, default=None, help="Max videos to download")
@click.option("--headless/--no-headless", default=True, help="Run browser in headless mode")
@click.option("--resume", is_flag=True, help="Resume from last position")
def download(workers: int, limit: int, headless: bool, resume: bool):
    """Download pending videos and upload to GCS."""
    console.print(f"[bold blue]Downloading Videos to GCS[/bold blue]")
    console.print()
    
    stats = download_videos(workers=workers, limit=limit, headless=headless)
    
    console.print()
    console.print(f"[green]Success: {stats['success']}[/green] | [red]Failed: {stats['failed']}[/red]")


@cli.command()
def stats():
    """Show download statistics."""
    data = database.get_stats()
    
    table = Table(title="Download Statistics")
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right")
    
    table.add_row("Total", str(data["total"]))
    table.add_row("Pending", str(data["pending"]))
    table.add_row("Downloaded", str(data["downloaded"]), style="green")
    table.add_row("Failed", str(data["failed"]), style="red")
    
    console.print(table)


@cli.command()
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "csv"]), default="json")
@click.option("--output", "-o", type=click.Path(), default=None)
def export(fmt: str, output: str):
    """Export video metadata to JSON or CSV."""
    data = database.export_data()
    
    if not data:
        console.print("[yellow]No data to export[/yellow]")
        return
    
    output_path = Path(output) if output else Path(f"exports/videos.{fmt}")
    output_path.parent.mkdir(exist_ok=True)
    
    if fmt == "json":
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    else:
        keys = data[0].keys()
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    
    console.print(f"[green]Exported {len(data)} records to {output_path}[/green]")


@cli.command()
@click.option("--all", "reset_all", is_flag=True, help="Reset all failed (including those without video_url)")
def reset(reset_all: bool):
    """Reset failed videos to pending status.

    By default, only resets videos that have a video_url (can be downloaded).
    Use --all to reset all failed videos.
    """
    import sqlite3
    from .config import DATABASE_PATH

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    if reset_all:
        cursor.execute("UPDATE videos SET status = 'pending', error_message = NULL WHERE status = 'failed'")
    else:
        # Only reset videos that have video_url populated
        cursor.execute("""
            UPDATE videos
            SET status = 'pending', error_message = NULL
            WHERE status = 'failed' AND video_url IS NOT NULL AND video_url != ''
        """)

    count = cursor.rowcount
    conn.commit()
    conn.close()

    console.print(f"[green]Reset {count} failed videos to pending[/green]")


@cli.command()
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without deleting")
def cleanup(dry_run: bool):
    """Remove videos that cannot be downloaded (no video_url).

    These are entries where the scraper couldn't capture a video URL,
    making them impossible to download.
    """
    import sqlite3
    from .config import DATABASE_PATH

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # First count how many will be affected
    cursor.execute("""
        SELECT COUNT(*) FROM videos
        WHERE (video_url IS NULL OR video_url = '') AND status != 'downloaded'
    """)
    count = cursor.fetchone()[0]

    if count == 0:
        console.print("[green]No orphan entries found. All videos have video_url.[/green]")
        conn.close()
        return

    if dry_run:
        console.print(f"[yellow]Would delete {count} videos without video_url[/yellow]")

        # Show sample
        cursor.execute("""
            SELECT id, status, search_term FROM videos
            WHERE (video_url IS NULL OR video_url = '') AND status != 'downloaded'
            LIMIT 5
        """)
        rows = cursor.fetchall()
        console.print("\n[dim]Sample entries:[/dim]")
        for row in rows:
            console.print(f"  - {row[0]} ({row[1]}) - search: {row[2]}")
    else:
        cursor.execute("""
            DELETE FROM videos
            WHERE (video_url IS NULL OR video_url = '') AND status != 'downloaded'
        """)
        conn.commit()
        console.print(f"[green]Deleted {count} videos without video_url[/green]")

    conn.close()


if __name__ == "__main__":
    cli()
