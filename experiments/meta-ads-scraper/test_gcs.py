"""Quick test to verify GCS connection."""
from src import storage
from rich.console import Console

console = Console()

def test_connection():
    try:
        console.print("[blue]Testing GCS connection...[/blue]")
        blobs = storage.list_videos()
        console.print(f"[green]✓ Connection successful! Found {len(blobs)} videos in bucket.[/green]")
    except Exception as e:
        console.print(f"[red]✗ Connection failed: {e}[/red]")

if __name__ == "__main__":
    test_connection()
