# Runtime requirements

Read this reference only when setting up or troubleshooting Browser Bridge.

## Python dependency

The server requires Python 3 and the `websockets` package. By default, `wsb`
uses its own active Python interpreter. Check that environment:

```bash
python3 -c "import websockets; print(websockets.__version__)"
```

If the import fails, ask before installing into the user's selected Python
environment. Alternatively, point Browser Bridge at an existing compatible
interpreter:

```bash
WSB_PYTHON=/path/to/python3 <skill-dir>/wsb ensure
```

`wsb ensure` and `wsb serve` verify the dependency before starting the
server and report how to select another interpreter. Do not create or replace
an environment without approval.

## Local services

Browser Bridge uses loopback services only:

- WebSocket clients connect to `localhost:8787`.
- The CLI connects to the management service on `localhost:8788`.
- Override the ports with `WSB_WS_PORT` and `WSB_MGMT_PORT`.
- When overriding the WebSocket port, set `window.WSB.url` to match.

`wsb ensure` starts `server.py` as a detached process. The default log is
`browser-bridge-server.log` in the operating system's temporary directory.
Set `WSB_LOG_PATH` to select another writable location.

Some sandboxes require approval to bind or connect to loopback ports, start a
detached process, open a browser, or write instrumentation into the project.
Follow the host agent's normal approval mechanism and request the narrowest
capability needed. Do not alter permission configuration automatically.
