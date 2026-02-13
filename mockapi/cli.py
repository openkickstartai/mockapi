"""CLI interface for mockapi.

Provides the `mockapi serve` command that boots a REST API
from a JSON file with optional hot-reload on file changes.
"""

import json
import os
import sys
import threading
import time

import click


def _file_size_human(path):
    """Return human-readable file size."""
    size = os.path.getsize(path)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _profile_data(data, db_path):
    """Print a quick data profile on startup — sizes, record counts."""
    click.echo(f"  source : {db_path} ({_file_size_human(db_path)})")
    click.echo(f"  collections: {len(data)}")
    total_records = 0
    for name, records in data.items():
        if isinstance(records, list):
            n = len(records)
            total_records += n
            click.echo(f"    /{name:<20s}  {n:>6,} record(s)")
        else:
            click.echo(f"    /{name:<20s}  (scalar value)")
    click.echo(f"  total records: {total_records:,}")


def _start_watcher(db_path, app, interval=1.0):
    """Poll-based file watcher that reloads data into the app on change.

    Uses mtime polling (1 s default) — no extra deps like watchdog.
    Tolerates partial writes by catching JSON decode errors.
    """

    def _watch():
        last_mtime = os.path.getmtime(db_path)
        while True:
            time.sleep(interval)
            try:
                mtime = os.path.getmtime(db_path)
                if mtime != last_mtime:
                    last_mtime = mtime
                    t0 = time.monotonic()
                    with open(db_path, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    elapsed_ms = (time.monotonic() - t0) * 1000
                    app.config["DB_DATA"] = data
                    total = sum(
                        len(v) for v in data.values() if isinstance(v, list)
                    )
                    click.echo(
                        f"[hot-reload] {db_path} reloaded in {elapsed_ms:.1f} ms "
                        f"({total:,} records across {len(data)} collections)"
                    )
            except json.JSONDecodeError:
                pass  # file is mid-write, retry next tick
            except Exception as exc:  # noqa: BLE001
                click.echo(f"[hot-reload] watch error: {exc}", err=True)

    t = threading.Thread(target=_watch, daemon=True)
    t.start()


@click.group()
@click.version_option(package_name="mockapi")
def main():
    """mockapi — Instant REST API from a JSON file."""


@main.command()
@click.argument("db_path", type=click.Path(exists=True))
@click.option("--host", "-h", default="0.0.0.0", show_default=True, help="Bind host.")
@click.option("--port", "-p", default=3000, show_default=True, type=int, help="Bind port.")
@click.option(
    "--reload/--no-reload",
    default=True,
    show_default=True,
    help="Watch JSON file and hot-reload on change.",
)
def serve(db_path, host, port, reload):
    """Start the mock API server from DB_PATH (a JSON file)."""
    from mockapi.server import create_app  # lazy import to keep CLI snappy

    db_path = os.path.abspath(db_path)

    # ---------- validate & profile ----------
    t0 = time.monotonic()
    try:
        with open(db_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON in {db_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise click.ClickException(
            f"Top-level value must be a JSON object, got {type(data).__name__}"
        )

    load_ms = (time.monotonic() - t0) * 1000
    click.echo(f"mockapi — loaded in {load_ms:.1f} ms")
    _profile_data(data, db_path)

    # ---------- create app ----------
    app = create_app(db_path)

    if reload:
        _start_watcher(db_path, app)
        click.echo("  hot-reload: enabled (polling 1 s)")

    click.echo(f"\n  Listening on http://{host}:{port}\n")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
