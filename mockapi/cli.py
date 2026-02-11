"""CLI."""
import click
from mockapi.server import create_app

@click.group()
def main(): pass

@main.command()
@click.argument('datafile')
@click.option('--port', default=3000)
@click.option('--host', default='127.0.0.1')
def serve(datafile, port, host):
    """Start mock API server."""
    app = create_app(datafile)
    click.echo(f"mockapi serving {datafile} on http://{host}:{port}")
    app.run(host=host, port=port)
