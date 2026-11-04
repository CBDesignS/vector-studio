"""Desktop entry point: bind a free local port, then open the browser."""
import threading
import webbrowser

from werkzeug.serving import make_server
from app import app


def main():
    # Port 0 asks Windows for a free port, avoiding conflicts with other apps.
    server = make_server('127.0.0.1', 0, app, threaded=True)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Vector Studio is running at {url}', flush=True)
    print('Keep this window open. Close it or press Ctrl+C to stop the app.', flush=True)
    print('If the browser does not open, copy the address above into your browser.', flush=True)
    opener = threading.Timer(0.5, webbrowser.open, args=(url,))
    opener.daemon = True
    opener.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        opener.cancel()
        server.server_close()


if __name__ == '__main__':
    main()
