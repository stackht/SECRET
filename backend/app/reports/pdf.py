"""Minimal stdlib PDF writer (Phase 9).

Produces a small, structurally-valid PDF from plain text lines using only the
Python standard library. Sufficient for a PDF "preview" artifact without
introducing heavy dependencies. Not a full layout engine — intentionally simple.
"""
from __future__ import annotations

import base64
import io
import zlib


def _escape(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace("(", r"\(")
        .replace(")", r"\)")
    )


def render_pdf_text(lines: list[str], title: str = "SECRET Report") -> bytes:
    """Return PDF bytes for the given text lines."""
    objects: list[bytes] = []
    pages: list[bytes] = []

    # Content stream (a single page is enough for previews).
    content_parts = [f"BT /F1 11 Tf 36 780 Td 14 TL"]
    content_parts.append(f"({_escape('SECRET — ' + title)}) Tj")
    content_parts.append("T*")
    line_count = 0
    for line in lines:
        content_parts.append(f"({_escape(line[:120])}) Tj")
        content_parts.append("T*")
        line_count += 1
        if line_count >= 52:
            break
    content_parts.append("ET")
    content_stream = ("\n".join(content_parts)).encode("latin-1", "replace")
    compressed = zlib.compress(content_stream)

    # Object 1: catalog, 2: pages, 3: page, 4: font, 5: content stream.
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj"
    )
    objects.append(
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj"
    )
    objects.append(
        b"5 0 obj\n<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(compressed)
        + compressed
        + b"\nendstream\nendobj"
    )

    body = b"".join(o + b"\n" for o in objects)
    xref_offset = 0
    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(buf.tell())
        buf.write(obj + b"\n")
    xref_start = buf.tell()
    buf.write(b"xref\n0 %d\n" % (len(objects) + 1))
    buf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buf.write(b"%010d 00000 n \n" % off)
    buf.write(b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1))
    buf.write(b"startxref\n%d\n%%%%EOF\n" % xref_start)
    return buf.getvalue()


def encode_pdf_artifact(lines: list[str], title: str) -> str:
    """Return base64-encoded PDF artifact for API responses."""
    pdf_bytes = render_pdf_text(lines, title)
    return base64.b64encode(pdf_bytes).decode("ascii")
