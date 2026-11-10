#!/usr/bin/env python3
"""MCP stdio server for book-man.

Speaks newline-delimited JSON-RPC 2.0 over stdin/stdout and forwards every
tool call to one of the pipeline scripts in ``scripts/`` as a subprocess.
Standard library only: no SDK, no third-party dependency, so the server
starts in whatever interpreter the plugin is handed.

Two rules this file will not break:

* **The scripts own every result.** Nothing here reformats, summarises or
  improves output. If the verifier says a page fails, the agent sees the
  word "FAIL" and the reasons, not a cheerful summary.
* **Failures are loud.** A non-zero exit, a missing file or a bad argument
  comes back as an MCP tool error carrying the real stderr, so a failure can
  never be mistaken for an empty but successful run.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SERVER_NAME = "book-man"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18")
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PLUGIN_ROOT / "scripts"
TIMEOUT = float(os.environ.get("BOOK_MAN_TIMEOUT", "1800"))


class ToolError(Exception):
    """A tool call that failed for a reason the caller must see verbatim."""


def _script(name: str) -> Path:
    p = SCRIPTS / name
    if not p.exists():
        raise ToolError(f"missing pipeline script: {p}")
    return p


def _run(argv: list[str], cwd: str | None = None) -> str:
    """Run a pipeline script and return its combined output, or raise loudly."""
    proc = subprocess.run(
        [sys.executable, *argv],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )
    out = (proc.stdout or "") + (("\n[stderr]\n" + proc.stderr) if proc.stderr.strip() else "")
    if proc.returncode != 0:
        raise ToolError(
            f"exit {proc.returncode} from {' '.join(Path(a).name if i == 0 else a for i, a in enumerate(argv))}\n"
            f"{out.strip()[:6000] or '(no output)'}"
        )
    return out.strip() or "(completed with no output)"


# --------------------------------------------------------------------- tools
def book_info(pdf: str) -> str:
    return _run([str(_script("ocr_scanned_pdf.py")), pdf, "--info-only"])


def book_ocr(pdf: str, out: str, force_single: bool = False, dpi: int = 300) -> str:
    argv = [str(_script("ocr_scanned_pdf.py")), pdf, out, "--dpi", str(dpi)]
    if force_single:
        argv.append("--force-single")
    return _run(argv)


def book_pages(ocr_file: str, start: int, end: int) -> str:
    """Print a printed-page range from an OCR file (the page-mapping step)."""
    code = (
        "import sys, re\n"
        "path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])\n"
        "txt = open(path, encoding='utf-8', errors='replace').read()\n"
        "blocks = re.split(r'<!--\\s*PDF_PAGE\\s+(\\d+)\\s+(L|R|LEFT|RIGHT)\\s*-->', txt)\n"
        "out, cur = [], None\n"
        "for i in range(1, len(blocks) - 2, 3):\n"
        "    n, side, body = int(blocks[i]), blocks[i + 1][:1].upper(), blocks[i + 2]\n"
        "    printed = 2 * n - 22 if side == 'L' else 2 * n - 21\n"
        "    if a <= printed <= b:\n"
        "        out.append(f'===== printed page {printed}   (pdf {n}{side[0]}) =====')\n"
        "        out.append(body.strip())\n"
        "if not out:\n"
        "    print(f'no pages in range {a}-{b}; the file may use a different marker format', file=sys.stderr)\n"
        "    sys.exit(2)\n"
        "print('\\n'.join(out))\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code, ocr_file, str(start), str(end)],
        capture_output=True, text=True, timeout=TIMEOUT,
    )
    if proc.returncode != 0:
        raise ToolError(f"page extraction failed:\n{proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def book_verify(pages_dir: str, source_file: str | None = None,
                source_dir: str | None = None) -> str:
    argv = [str(_script("verify_pages.py")), pages_dir]
    if source_file:
        argv += ["--source-file", source_file]
    if source_dir:
        argv += ["--source-dir", source_dir]
    return _run(argv)


def book_assemble(wiki_dir: str) -> str:
    return _run([str(Path(wiki_dir) / "_meta" / "assemble_book.py")], cwd=wiki_dir)


def book_publish(pages_dir: str, dest: str, guide: str | None = None,
                 fonts: bool = False, dry_run: bool = False) -> str:
    argv = [str(_script("publish.py")), pages_dir, "--dest", dest]
    if guide:
        argv += ["--guide", guide]
    if fonts:
        argv.append("--fonts")
    if dry_run:
        argv.append("--dry-run")
    return _run(argv)


TOOLS = [
    {
        "name": "book_info",
        "description": "Inspect a PDF before OCR: page count, page size, and whether the scan holds one or two book pages per PDF page. Run this first — it decides whether the OCR step splits spreads.",
        "inputSchema": {
            "type": "object",
            "properties": {"pdf": {"type": "string", "description": "Absolute path to the PDF."}},
            "required": ["pdf"],
        },
    },
    {
        "name": "book_ocr",
        "description": "OCR a scanned book into page-marked markdown. Detects two-up spreads, splits them, OCRs in parallel with tesseract and writes '<!-- PDF_PAGE n LEFT -->' markers. Requires pdftoppm and tesseract.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pdf": {"type": "string"},
                "out": {"type": "string", "description": "Output markdown path, e.g. sources/raw.md"},
                "force_single": {"type": "boolean", "description": "Treat each PDF page as one book page even if it looks wide."},
                "dpi": {"type": "integer", "description": "Render resolution, default 300."},
            },
            "required": ["pdf", "out"],
        },
    },
    {
        "name": "book_pages",
        "description": "Print a range of PRINTED book pages from an OCR file, with the page number on each heading. Always cite printed pages, never PDF page numbers. Use this to read the source for one chapter before writing its page.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ocr_file": {"type": "string", "description": "Path to the OCR markdown, e.g. sources/raw.md"},
                "start": {"type": "integer", "description": "First printed page."},
                "end": {"type": "integer", "description": "Last printed page."},
            },
            "required": ["ocr_file", "start", "end"],
        },
    },
    {
        "name": "book_verify",
        "description": "Check built HTML pages: placeholders, script tags, dead anchors, missing viewport, citation density, prose length, and figures that do not appear in the source text. Pass source_file (the OCR markdown) for coverage-preserving pages — the condensed summary is the wrong yardstick.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pages_dir": {"type": "string"},
                "source_file": {"type": "string", "description": "e.g. sources/raw.md"},
                "source_dir": {"type": "string", "description": "Folder of ch-NN/summary.md, for older summary-based pages."},
            },
            "required": ["pages_dir"],
        },
    },
    {
        "name": "book_assemble",
        "description": "Merge every built chapter page into one self-contained HTML book with :target navigation, prefixed ids and prev/next links. Idempotent; re-run after each batch of chapters lands.",
        "inputSchema": {
            "type": "object",
            "properties": {"wiki_dir": {"type": "string", "description": "Book folder containing _meta/assemble_book.py and pages/."}},
            "required": ["wiki_dir"],
        },
    },
    {
        "name": "book_publish",
        "description": "Copy finished pages to the reader's machine, optionally embedding fonts, and verify every relative link resolves. Use --dry-run first.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pages_dir": {"type": "string"},
                "dest": {"type": "string", "description": "Destination folder, e.g. /mnt/c/Users/<user>/Desktop/<Book>"},
                "guide": {"type": "string", "description": "Optional guide filename to copy first."},
                "fonts": {"type": "boolean"},
                "dry_run": {"type": "boolean"},
            },
            "required": ["pages_dir", "dest"],
        },
    },
]

DISPATCH = {
    "book_info": book_info,
    "book_ocr": book_ocr,
    "book_pages": book_pages,
    "book_verify": book_verify,
    "book_assemble": book_assemble,
    "book_publish": book_publish,
}


# ----------------------------------------------------------------- transport
def reply(msg_id, result=None, error=None):
    payload = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def handle(req: dict):
    method = req.get("method")
    msg_id = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        want = params.get("protocolVersion")
        return reply(msg_id, {
            "protocolVersion": want if want in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "ping":
        return reply(msg_id, {})
    if method == "tools/list":
        return reply(msg_id, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        fn = DISPATCH.get(name)
        if fn is None:
            return reply(msg_id, error={"code": METHOD_NOT_FOUND, "message": f"unknown tool: {name}"})
        try:
            text = fn(**args)
            return reply(msg_id, {"content": [{"type": "text", "text": text}], "isError": False})
        except TypeError as exc:
            return reply(msg_id, error={"code": INVALID_PARAMS, "message": str(exc)})
        except ToolError as exc:
            return reply(msg_id, {"content": [{"type": "text", "text": str(exc)}], "isError": True})
        except subprocess.TimeoutExpired:
            return reply(msg_id, {"content": [{"type": "text", "text": f"timed out after {TIMEOUT:.0f}s"}], "isError": True})
        except Exception as exc:  # never swallow a failure into a cheerful result
            return reply(msg_id, {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True})
    if method == "shutdown":
        return reply(msg_id, {})
    if msg_id is not None:
        return reply(msg_id, error={"code": METHOD_NOT_FOUND, "message": f"unknown method: {method}"})
    return None


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            reply(None, error={"code": PARSE_ERROR, "message": str(exc)})
            continue
        try:
            handle(req)
        except Exception as exc:
            safe_id = req.get("id") if isinstance(req, dict) else None
            reply(safe_id, error={"code": -32603, "message": f"{type(exc).__name__}: {exc}"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
