#!/usr/bin/env python3
"""
browser-bridge server
=====================
WebSocket server  ws://localhost:8787  — pages embedding wsb-client.js connect here
Management server    localhost:8788    — the wsb CLI talks here (JSON-line protocol)

Ports are overridable with WSB_WS_PORT / WSB_MGMT_PORT environment variables.
The client must be pointed at the matching WS port via window.WSB.url.

Client protocol (JSON text frames):
  client → server:
    {"kind": "hello", "app": "myapp", "version": "key", "href": "http://..."}
    {"kind": "log",  "run": <id|null>, "text": "..."}
    {"kind": "done", "run": <id>, "ok": true|false, "error": "..."}
  server → client:
    {"kind": "run", "id": <run_id>, "code": "<js source>"}
    {"kind": "reload"}

Non-JSON frames from the client are treated as bare console log lines.

Management protocol (newline-terminated JSON, one request per connection):
  {"cmd": "status"}
  {"cmd": "run", "code": "...", "name": "...", "wait": true, "timeout": 30,
   "connection": 2, "app": "myapp", "version": "key"}
  {"cmd": "log", "run": 3}
  {"cmd": "console", "connection": 2, "app": "myapp"}
  {"cmd": "reload", "connection": 2, "app": "myapp", "wait": true, "timeout": 15}
  {"cmd": "wait", "app": "myapp", "version": "key", "timeout": 15}
  {"cmd": "shutdown"}

status replies include "build" (the server's BUILD number) so the CLI's
`ensure` command can detect and restart an out-of-date running server.

Connection selection (run / console / reload): explicit "connection" id wins;
otherwise the most recent connection matching "app" (or the most recent overall).
If "version" is given and the selected connection reports a different version,
the command fails — this is the staleness guard.
"""

import asyncio
import json
import os
from collections import deque, OrderedDict
from datetime import datetime

import websockets
from websockets.exceptions import ConnectionClosed

# Bumped on any protocol/behaviour change; `wsb ensure` restarts a running
# server whose status reply reports a different build.
BUILD = 1

WS_HOST   = os.environ.get("WSB_WS_HOST", "localhost")
WS_PORT   = int(os.environ.get("WSB_WS_PORT", "8787"))
MGMT_HOST = "localhost"
MGMT_PORT = int(os.environ.get("WSB_MGMT_PORT", "8788"))

MAX_RUNS      = 200   # completed runs kept for `log`
CONSOLE_LINES = 500   # per-connection console ring buffer

# ── Global state ──────────────────────────────────────────────────────────────
_conn_counter = 0
_run_counter  = 0

# conn_id → {"ws", "app", "version", "href", "opened", "console": deque}
connections: dict = {}
# ordered conn_ids, oldest first (most recent = last)
conn_order: list = []
# run_id → {"conn", "name", "lines", "done": asyncio.Event, "ok", "error", "started"}
runs: OrderedDict = OrderedDict()
# waiters for hello messages: {"app", "version", "future"}
hello_waiters: list = []
# set by the "shutdown" management command; main() exits when it fires
_shutdown_event: asyncio.Event = None


def _next_conn_id() -> int:
    global _conn_counter
    _conn_counter += 1
    return _conn_counter


def _next_run_id() -> int:
    global _run_counter
    _run_counter += 1
    return _run_counter


def _stamp(text: str) -> str:
    ts = datetime.now().isoformat(timespec="milliseconds")
    return f"[{ts}] {text}"


def _conn_summary(cid: int) -> dict:
    c = connections[cid]
    return {
        "connection": cid,
        "app":        c["app"],
        "version":    c["version"],
        "href":       c["href"],
        "age":        round((datetime.now() - c["opened"]).total_seconds(), 1),
    }


def _notify_hello(cid: int):
    c = connections[cid]
    for waiter in hello_waiters[:]:
        if waiter["app"] is not None and c["app"] != waiter["app"]:
            continue
        if waiter["version"] is not None and c["version"] != waiter["version"]:
            continue
        hello_waiters.remove(waiter)
        if not waiter["future"].done():
            waiter["future"].set_result(cid)


# ── WebSocket handler ─────────────────────────────────────────────────────────

def _handle_client_msg(conn_id: int, info: dict, raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    try:
        msg = json.loads(raw)
        if not isinstance(msg, dict):
            raise ValueError
    except (ValueError, json.JSONDecodeError):
        info["console"].append(_stamp(raw))
        return

    kind = msg.get("kind")

    if kind == "hello":
        info["app"]     = str(msg.get("app") or "")
        info["version"] = str(msg.get("version") or "")
        info["href"]    = str(msg.get("href") or "")
        print(f"[=] conn {conn_id} hello  app={info['app']}  "
              f"version={info['version']}  {info['href']}")
        _notify_hello(conn_id)

    elif kind == "log":
        run = runs.get(msg.get("run"))
        text = str(msg.get("text", ""))
        if run is not None and run["conn"] == conn_id:
            run["lines"].append(_stamp(text))
        else:
            info["console"].append(_stamp(text))

    elif kind == "done":
        run = runs.get(msg.get("run"))
        if run is not None and run["conn"] == conn_id and not run["done"].is_set():
            run["ok"]    = bool(msg.get("ok"))
            err          = msg.get("error")
            run["error"] = str(err) if err else None
            run["done"].set()


async def ws_handler(websocket):
    conn_id = _next_conn_id()
    info = {
        "ws":      websocket,
        "app":     None,
        "version": None,
        "href":    None,
        "opened":  datetime.now(),
        "console": deque(maxlen=CONSOLE_LINES),
    }
    connections[conn_id] = info
    conn_order.append(conn_id)
    print(f"[+] conn {conn_id} opened  ({len(connections)} open)")

    try:
        async for raw in websocket:
            _handle_client_msg(conn_id, info, raw)
    except ConnectionClosed:
        pass
    finally:
        connections.pop(conn_id, None)
        try:
            conn_order.remove(conn_id)
        except ValueError:
            pass
        # Fail any still-pending runs on this connection
        for run in runs.values():
            if run["conn"] == conn_id and not run["done"].is_set():
                run["ok"]    = False
                run["error"] = "connection closed before run completed"
                run["done"].set()
        print(f"[-] conn {conn_id} closed  ({len(connections)} open)")


# ── Management handler ────────────────────────────────────────────────────────

def _select_conn(req: dict):
    """Return (conn_id, error). Applies the version staleness guard."""
    if req.get("connection") is not None:
        cid = int(req["connection"])
        if cid not in connections:
            return None, f"connection {cid} not found"
    else:
        app = req.get("app")
        candidates = [c for c in conn_order
                      if app is None or connections[c]["app"] == app]
        if not candidates:
            if app is not None:
                return None, f"no connection with app '{app}'"
            return None, "no connections available"
        cid = candidates[-1]

    want = req.get("version")
    if want is not None:
        have = connections[cid]["version"]
        if have != want:
            return None, (f"connection {cid} (app '{connections[cid]['app']}') "
                          f"reports version '{have}', expected '{want}' — "
                          f"the page is stale; reload it (wsb reload --wait)")
    return cid, None


def _run_snapshot(run_id: int, run: dict) -> dict:
    return {
        "run_id":     run_id,
        "name":       run["name"],
        "connection": run["conn"],
        "done":       run["done"].is_set(),
        "ok":         run["ok"],
        "error":      run["error"],
        "lines":      run["lines"][:],
    }


async def _handle_mgmt_request(req: dict) -> dict:
    cmd = req.get("cmd", "")

    if cmd == "status":
        return {"build": BUILD,
                "connections": [_conn_summary(c) for c in conn_order]}

    if cmd == "shutdown":
        return {"stopping": True, "_shutdown": True}

    if cmd == "run":
        code = req.get("code")
        if not isinstance(code, str) or not code.strip():
            return {"error": "run requires non-empty 'code'"}
        cid, err = _select_conn(req)
        if err:
            return {"error": err}

        run_id = _next_run_id()
        run = {
            "conn":    cid,
            "name":    str(req.get("name") or f"run_{run_id}"),
            "lines":   [],
            "done":    asyncio.Event(),
            "ok":      None,
            "error":   None,
            "started": datetime.now(),
        }
        runs[run_id] = run
        while len(runs) > MAX_RUNS:
            runs.popitem(last=False)

        await connections[cid]["ws"].send(
            json.dumps({"kind": "run", "id": run_id, "code": code}))

        if not req.get("wait"):
            return {"run_id": run_id, "connection": cid}

        timeout = float(req.get("timeout") or 30)
        try:
            await asyncio.wait_for(run["done"].wait(), timeout)
        except asyncio.TimeoutError:
            pass
        return _run_snapshot(run_id, run)

    if cmd == "log":
        run_id = req.get("run")
        try:
            run_id = int(run_id)
        except (TypeError, ValueError):
            return {"error": "log requires a numeric 'run' id"}
        run = runs.get(run_id)
        if run is None:
            return {"error": f"run {run_id} not found (server keeps the last {MAX_RUNS})"}
        return _run_snapshot(run_id, run)

    if cmd == "console":
        cid, err = _select_conn(req)
        if err:
            return {"error": err}
        return {"connection": cid, "lines": list(connections[cid]["console"])}

    if cmd == "reload":
        cid, err = _select_conn(req)
        if err:
            return {"error": err}
        app = connections[cid]["app"] or None
        await connections[cid]["ws"].send(json.dumps({"kind": "reload"}))
        if not req.get("wait"):
            return {"reloaded": True, "connection": cid}

        timeout = float(req.get("timeout") or 15)
        fut = asyncio.get_event_loop().create_future()
        waiter = {"app": app, "version": req.get("new_version"), "future": fut}
        hello_waiters.append(waiter)
        try:
            new_cid = await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            if waiter in hello_waiters:
                hello_waiters.remove(waiter)
            return {"error": f"reload sent, but no matching hello within {timeout}s"}
        result = _conn_summary(new_cid)
        result["reloaded"] = True
        return result

    if cmd == "wait":
        app     = req.get("app")
        version = req.get("version")
        timeout = float(req.get("timeout") or 15)

        for cid in reversed(conn_order):
            c = connections[cid]
            if c["app"] is None:
                continue  # not hello'd yet
            if app is not None and c["app"] != app:
                continue
            if version is not None and c["version"] != version:
                continue
            return _conn_summary(cid)

        fut = asyncio.get_event_loop().create_future()
        waiter = {"app": app, "version": version, "future": fut}
        hello_waiters.append(waiter)
        try:
            cid = await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            if waiter in hello_waiters:
                hello_waiters.remove(waiter)
            want = " ".join(filter(None, [
                f"app '{app}'" if app else None,
                f"version '{version}'" if version else None])) or "any connection"
            return {"error": f"no hello for {want} within {timeout}s"}
        return _conn_summary(cid)

    return {"error": f"unknown command: {cmd}"}


async def mgmt_handler(reader, writer):
    try:
        raw = await asyncio.wait_for(reader.readline(), timeout=10.0)
    except asyncio.TimeoutError:
        writer.close()
        return

    try:
        req = json.loads(raw.decode("utf-8").strip())
        if not isinstance(req, dict):
            raise ValueError
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        result = {"error": "invalid JSON"}
    else:
        try:
            result = await _handle_mgmt_request(req)
        except Exception as e:  # noqa: BLE001 — surface anything to the CLI
            result = {"error": f"server exception: {e!r}"}

    shutdown = result.pop("_shutdown", False)

    writer.write((json.dumps(result) + "\n").encode("utf-8"))
    try:
        await writer.drain()
    except ConnectionResetError:
        pass
    writer.close()

    if shutdown:
        print("shutdown requested via management socket")
        _shutdown_event.set()


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    global _shutdown_event
    _shutdown_event = asyncio.Event()

    ws_server   = await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    mgmt_server = await asyncio.start_server(mgmt_handler, MGMT_HOST, MGMT_PORT)

    print(f"browser-bridge server ready (build {BUILD})")
    print(f"  WebSocket:  ws://{WS_HOST}:{WS_PORT}")
    print(f"  Management: {MGMT_HOST}:{MGMT_PORT}")
    print()

    async with ws_server, mgmt_server:
        await _shutdown_event.wait()
    print("server stopped")


if __name__ == "__main__":
    asyncio.run(main())
