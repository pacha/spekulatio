from pathlib import Path

import click
from werkzeug.serving import run_simple

from spekulatio.lib.wsgi import create_file_serving_app


@click.command()
@click.option(
    "-d",
    "--directory",
    "directory",
    required=True,
    default=".",
    help="Directory to serve.",
)
@click.option(
    "-p",
    "--port",
    "port",
    required=True,
    default=5000,
    help="Port to be used by the HTTP server.",
)
def serve(directory, port):
    """Run a HTTP server to serve a directory."""

    directory_path = Path(directory)
    app = create_file_serving_app(directory_path)
    run_simple("localhost", port, app, threaded=True)
