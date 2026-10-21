#!/usr/bin/env python3
"""Inline the local scripts, stylesheets and images of a built HTML page.

Usage: inline_html.py <dist/index.html>   (writes the inlined page to stdout)

Handles <script src>, <link rel=stylesheet href>, <img src> and CSS url(),
resolving paths against the HTML file's directory. Attribute values may be
quoted or unquoted (Parcel's minifier drops quotes). Remote and data: URLs
are left as they are.
"""
import base64, html, mimetypes, pathlib, re, sys, urllib.parse

page = pathlib.Path(sys.argv[1])
root = page.parent
mimetypes.add_type("image/webp", ".webp")
ATTR = re.compile(r"""([^\s=/>]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?""")


def attrs(text):
    """Parse a tag's attribute text into an ordered {name: value-or-None} dict."""
    out = {}
    for name, value in ATTR.findall(text):
        out[name.lower()] = html.unescape(value.strip("\"'")) if value else None
    return out


def render(a):
    return "".join(f" {k}" if v is None else f' {k}="{html.escape(v)}"' for k, v in a.items())


def local(ref):
    ref = urllib.parse.unquote((ref or "").split("?")[0].split("#")[0])
    if not ref or re.match(r"^([a-z]+:|//)", ref, re.I):
        return None
    path = (root / ref.lstrip("/")).resolve()
    return path if path.is_file() else None


def data_url(path):
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def css_urls(css):
    def repl(m):
        path = local(m.group(2))
        return f"url({data_url(path)})" if path else m.group(0)
    return re.sub(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""", repl, css)


def script(m):
    a = attrs(m.group(1))
    path = local(a.pop("src", None))
    if not path:
        return m.group(0)
    code = path.read_text(encoding="utf-8").replace("</script", "<\\/script")
    return f"<script{render(a)}>{code}</script>"


def link(m):
    a = attrs(m.group(1))
    path = local(a.get("href")) if (a.get("rel") or "").lower() == "stylesheet" else None
    if not path:
        return m.group(0)
    return f"<style>{css_urls(path.read_text(encoding='utf-8'))}</style>"


def img(m):
    a = attrs(m.group(1))
    path = local(a.get("src"))
    if not path:
        return m.group(0)
    a["src"] = data_url(path)
    return f"<img{render(a)}>"


doc = page.read_text(encoding="utf-8")
doc = re.sub(r"<script\b([^>]*)>\s*</script>", script, doc, flags=re.I)
doc = re.sub(r"<link\b([^>]*)>", link, doc, flags=re.I)
doc = re.sub(r"<img\b([^>]*?)/?>", img, doc, flags=re.I)
doc = re.sub(r"(<style\b[^>]*>)(.*?)(</style>)",
             lambda m: m.group(1) + css_urls(m.group(2)) + m.group(3), doc, flags=re.S | re.I)
sys.stdout.write(doc)
