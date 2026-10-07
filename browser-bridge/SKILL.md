---
name: browser-bridge
description: Drive and test a live browser page from the command line. Use when building or debugging a locally served web app, executing JavaScript in a real page, reading browser errors and application output, reloading a page, checking DOM behavior, or verifying that the browser is running the latest build.
---

# Browser Bridge

A page that embeds `wsb-client.js` connects (on localhost only) to a local
WebSocket server and identifies itself with an **app name** and a **version
key**. The `wsb` CLI then lets you execute arbitrary JavaScript inside that
real, live page and read back the output — no headless browser, no test
framework, works with whatever tab the user already has open.

```
your test JS ──wsb CLI──▶ mgmt socket :8788 ──▶ server ──ws :8787──▶ live page
   output   ◀───────────────────────────────────────────────────────  wslog()
```

Resolve `<skill-dir>` as the directory containing this `SKILL.md`. Do not
assume a particular home directory, skill root, current working directory, or
that `wsb` is on `PATH`. Every `wsb` command below means:

```bash
<skill-dir>/wsb <command> [arguments]
```

Invoke the executable directly; do not prefix it with `python3`. If the host
requires approval for local sockets, detached processes, browser control, or
project-file writes, request only the permission needed for the next action.
Do not edit an agent's permission settings or allowlists. Read
[runtime.md](references/runtime.md) when setup, dependencies, ports, or
sandbox behavior need attention.

## 1. Instrument the app (once per app)

Copy `<skill-dir>/wsb-client.js` into the app's static files and include it
with a config that must be set **before** the script loads:

```html
<script>window.WSB = { app: 'myapp', version: '2026-07-16-1' };</script>
<script src="wsb-client.js"></script>
```

- `app` — a stable identifier for this application (used to pick the right
  connection when several apps/tabs are open).
- `version` — **bump this every time you change the app's code.** Any unique
  string works; `YYYY-MM-DD-N` is a good convention. This is what lets you
  prove the browser is running the code you just wrote, not a cached page.

The snippet is safe to leave in production builds: off localhost it does
nothing except define a console-logging `wslog()`. Optional config:
`url` (default `ws://localhost:8787`), `hosts` (allowed hostnames),
`force: true` (connect regardless of host), `hookErrors: false` (don't
forward window errors).

## 2. Start the server (once per machine)

```bash
wsb ensure
```

This is idempotent — run it at the start of any browser-testing work. It
starts the server **detached** (it keeps running after your session ends, so
pages stay connected and their console buffers survive between sessions), is
a no-op if the server is already up, and transparently restarts a running
server that predates the current skill code (build-number check). One server
serves every app, project, and session on the machine. `wsb stop` shuts it
down. Detached-server output goes to the operating system's temporary
directory by default; set `WSB_LOG_PATH` to override it.

Then have the page open/reload — ask the user to open the URL if you can't
reload an existing connection — and confirm:

```bash
wsb wait --app myapp --timeout 20        # blocks until the page connects
```

## 3. The edit → reload → verify loop

After every change to app code:

1. Bump the `version` string in the app's WSB config (part of your edit).
2. `wsb reload --app myapp --wait` — reloads the page, waits for it to
   reconnect, prints the new connection's app/version/href.
3. Pass `--version <new-key>` on subsequent commands — they **fail loudly if
   the page is stale**, which protects you from testing old code:

```bash
wsb eval 'document.title' --app myapp --version 2026-07-16-2
```

## 4. Running browser-side tests

`wsb eval '<expr>'` — evaluate one JS expression, print its value (JSON):

```bash
wsb eval 'document.querySelectorAll(".item").length'
wsb eval 'getComputedStyle(document.querySelector("#hdr")).backgroundColor'
```

`wsb run <file.js> --wait` — run a JS file in the page and print everything it
logged. Test code rules:

- The code runs inside `async () => { ... }` in the page's global scope: use
  `await` freely, `return` exits early, all page globals are visible.
- `wslog(msg)` records a line (strings pass through; objects are
  JSON-stringified).
- The run **completes automatically when the async body finishes** — resolved
  → ok, threw → failed with the error. No done() call needed; just make sure
  you `await` anything asynchronous you care about.
- Exit codes: 0 ok, 1 the run threw, 2 timed out (`--timeout SECS`, default
  30; a timed-out run keeps collecting — fetch later with `wsb log <id>`).

```javascript
// click_test.js — example
const btn = document.querySelector('#add-item');
btn.click();
await new Promise(r => setTimeout(r, 100));   // let the UI settle
const items = document.querySelectorAll('.item');
wslog('items after click: ' + items.length);
if (items.length !== 1) throw new Error('expected 1 item, got ' + items.length);
```

Keep test files in the project you're working on (e.g. `tests/browser/`) —
the CLI reads the file and ships the source; the server never touches your
project's disk.

`wsb run --code '<js>'` runs inline statements; `wsb run` without `--wait`
prints a run id immediately (fetch output later with `wsb log <id>`).

## 5. Reading the page's own output

The app can call `wslog()` in its own code (it's a global once the client is
loaded), and window errors / unhandled rejections are forwarded automatically.
Everything logged outside a run lands in a per-connection buffer:

```bash
wsb console --app myapp        # startup errors, app instrumentation, etc.
```

Check this first when "nothing happens" — an exception during page load will
be sitting there.

## 6. CLI reference

| Command | Purpose |
|---------|---------|
| `wsb status` | List connections: id, app, version, URL, age |
| `wsb wait [--app A] [--version V] [--timeout S]` | Block until a matching page connects (exit 2 on timeout) |
| `wsb run <file> [--wait] [--timeout S] [--name N]` | Run a JS test file |
| `wsb run --code '<js>' --wait` | Run inline JS statements |
| `wsb eval '<expr>'` | Evaluate an expression, print the result |
| `wsb log <run_id>` | Print output collected for a run (so far) |
| `wsb console` | Print the page's console/error buffer |
| `wsb reload [--wait]` | Reload the page; `--wait` blocks until it reconnects |
| `wsb ensure` | Start the server detached if needed (idempotent; restarts on build mismatch) |
| `wsb stop` | Shut down the running server |
| `wsb serve` | Run the server in the foreground |

Target selection for run/eval/console/reload: `--connection N` (exact),
`--app NAME` (most recent for that app), default most recent overall.
`--version KEY` makes the command fail if the page reports a different
version. Ports: WS `8787`, management `8788`; override with `WSB_WS_PORT` /
`WSB_MGMT_PORT` env vars (and point `WSB.url` in the page at the new WS port).

## Troubleshooting

- **"no connections available"** — the page isn't open, the snippet isn't
  included, or `window.WSB` was set *after* the script tag. Ask the user to
  open the app URL; the client retries every 3 s, so a late-started server is
  fine.
- **Version mismatch error** — the page is stale: `wsb reload --wait`, or if
  the version is still old after reload, your edit didn't reach the served
  files (check the build/copy step, and hard-cache issues).
- **Run times out** — you probably didn't `await` something, or the page
  navigated away mid-run. `wsb console` often shows why.
- **Port already in use** — another server instance is probably running;
  `wsb ensure` handles this (uses the existing server, or restarts it if it's
  an older build).
