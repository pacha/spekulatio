from werkzeug.utils import redirect
from werkzeug.utils import send_file
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response


def create_file_serving_app(directory):
    """Create WSGI app to serve the files of a directory.

    * Redirects requests to directories without trailing slash to the version with trailing slash
    * Redirects requests to files with trailing slash to the version without trailing slash
    * Serves html files even if the extension is not provided
    * Uses Etags to cache resources in the client

    Intended only for development purposes, not to be used in production.
    """

    def get_response(request):
        filepath = directory / request.path[1:]
        trailing_slash = request.path.endswith("/")

        if filepath.is_file():
            if trailing_slash:
                new_path = (
                    request.path[:-6]
                    if request.path.endswith(".html/")
                    else request.path[:-1]
                )
                return redirect(new_path, 302)
            else:
                return send_file(filepath, request.environ)

        if filepath.is_dir():
            if not trailing_slash:
                return redirect(f"{request.path}/", 302)
            else:
                index_path = filepath / "index.html"
                if index_path.is_file():
                    return send_file(index_path, request.environ)

        if trailing_slash:
            slashless_filepath = directory / request.path[1:-1]
            html_filepath = slashless_filepath.with_name(
                f"{slashless_filepath.name}.html"
            )
            if slashless_filepath.is_file() or html_filepath.is_file():
                return redirect(request.path[:-1], 302)
        else:
            html_filepath = filepath.with_name(f"{filepath.name}.html")
            if html_filepath.is_file():
                return send_file(html_filepath, request.environ)

        return Response("Not Found", status=404)

    def application(environ, start_response):
        request = Request(environ)
        response = get_response(request)

        # use only etag for catching
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response(environ, start_response)

    return application
