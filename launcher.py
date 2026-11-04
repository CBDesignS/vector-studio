"""Desktop entry point: prefer a stable local address for browser preferences."""
import threading
import webbrowser

from werkzeug.serving import make_server
from app import app
PREFERRED_PORT = 5179


def main():
    try:
        server = make_server('127.0.0.1', PREFERRED_PORT, app, threaded=True)
    except SystemExit as exc:
        if exc.code != 1:
            raise
        print(f'Port {PREFERRED_PORT} is unavailable; using a free local port instead.', flush=True)
        print('The browser may use a different remembered upload folder on this address.', flush=True)
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
