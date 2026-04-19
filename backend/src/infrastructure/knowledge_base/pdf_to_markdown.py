from __future__ import annotations

import logging
import re
import shutil
import tempfile
from pathlib import Path

import ocrmypdf
import pymupdf
import pymupdf4llm

logger = logging.getLogger(__name__)

MIN_TEXT_LAYER_CHARS = 50

_NOISE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*Alcald[íi]a de Medell[íi]n\s*$", re.IGNORECASE),
    re.compile(r"^\s*C[óo]d\.\s*MA\s*SECI-\d+.*$", re.IGNORECASE),
    re.compile(r"^\s*Versi[óo]n\.?\s*\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*Manual\s*$", re.IGNORECASE),
    re.compile(r"^\s*MA-SECI Manual de Buenas Pr[áa]cticas para\s*$", re.IGNORECASE),
    re.compile(r"^\s*PQRSD\s*$", re.IGNORECASE),
    re.compile(r"^\s*Distrito de\s*$", re.IGNORECASE),
    re.compile(r"^\s*Ciencia,\s*Tecnolog[íi]a e Innova.*$", re.IGNORECASE),
    re.compile(r"^\s*\d{1,3}\s*$"),
    re.compile(r"^\s*P[áa]gina\s+\d+(\s+de\s+\d+)?\s*$", re.IGNORECASE),
    # OCR path: pymupdf4llm wraps each page in ``` fences with ----- separators.
    re.compile(r"^\s*```\s*$"),
    re.compile(r"^\s*-{3,}\s*$"),
)

# Heading recovery for OCR'd legal decrees (Decreto 883 de 2015 and similar).
# Tesseract strips font-size/bold cues, so pymupdf4llm emits 0 markdown headers —
# we recover them from unambiguous textual markers.
_ROMAN_FIX = str.maketrans({"|": "I", "l": "I"})


def _fix_roman(s: str) -> str:
    # Used only in the narrow Roman-numeral slot after TÍTULO / CAPÍTULO, where
    # "|", "Il", "Ill" are OCR corruptions of "I", "II", "III". Safe because
    # we only touch the numeral token, not body text.
    return s.translate(_ROMAN_FIX)


_HEADING_RULES: tuple[tuple[re.Pattern[str], str, bool], ...] = (
    # (pattern, markdown_prefix, fix_roman_in_group1)
    (re.compile(r"^\s*(DECRETO\s+N[ÚU]MERO\s+\d+\s+DE\s+\d{4})\s*$"), "# ", False),
    (re.compile(r"^\s*(EL\s+ALCALDE\s+DE\s+MEDELL[ÍI]N)\s*$"), "## ", False),
    (re.compile(r"^\s*(CONSIDERANDO\s+QUE)\s*$"), "## ", False),
    (re.compile(r"^\s*(DECRETA)\s*$"), "## ", False),
    (re.compile(r"^\s*(T[ÍI]TULO\s+[|IVXlL\d]+)\b.*$"), "## ", True),
    (re.compile(r"^\s*(LIBRO\s+[|IVXlL\d]+|LIBRO\s+(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO))\b.*$"), "## ", True),
    (re.compile(r"^\s*(CAP[ÍI]TULO\s+[|IVXlL\d]+)\b.*$"), "### ", True),
    (re.compile(r"^\s*(SECCI[ÓO]N\s+\S+)\b.*$"), "### ", False),
    (re.compile(r"^\s*(Art[ií]culo\s+\d+)[.°]?\b.*$"), "### ", False),
    (re.compile(r"^\s*(Par[áa]grafo(?:\s+\d+)?)\s*[.:]?\b.*$"), "#### ", False),
)


def _recover_headings_from_ocr(md: str) -> str:
    out: list[str] = []
    for line in md.splitlines():
        matched = False
        for pattern, prefix, fix_roman in _HEADING_RULES:
            m = pattern.match(line)
            if not m:
                continue
            token = m.group(1).strip()
            if fix_roman:
                # Only normalize the tail of the token (the numeral), not the word.
                parts = token.split(maxsplit=1)
                if len(parts) == 2:
                    token = f"{parts[0]} {_fix_roman(parts[1])}"
            out.append(f"{prefix}{token}")
            matched = True
            break
        if not matched:
            out.append(line)
    return "\n".join(out)


def _has_text_layer(pdf_path: Path) -> bool:
    with pymupdf.open(pdf_path) as doc:
        sample_pages = min(3, doc.page_count)
        total = sum(len(doc[i].get_text().strip()) for i in range(sample_pages))
    return total >= MIN_TEXT_LAYER_CHARS


def _ocr_to_temp(pdf_path: Path, tmp_dir: Path) -> Path:
    if shutil.which("tesseract") is None:
        raise RuntimeError(
            f"{pdf_path.name} has no text layer and requires OCR, but tesseract is not "
            "installed. Install with: sudo apt install tesseract-ocr tesseract-ocr-spa"
        )
    ocr_out = tmp_dir / f"{pdf_path.stem}.ocr.pdf"
    logger.info("Running OCR on %s (this may take a minute)…", pdf_path.name)
    ocrmypdf.ocr(
        input_file=str(pdf_path),
        output_file=str(ocr_out),
        language="spa",
        skip_text=True,
        output_type="pdf",
        progress_bar=False,
    )
    return ocr_out


def _strip_noise_lines(md: str) -> str:
    kept: list[str] = []
    for line in md.splitlines():
        if any(p.match(line) for p in _NOISE_PATTERNS):
            continue
        kept.append(line)
    out = "\n".join(kept)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def convert(pdf_path: Path, out_dir: Path, force: bool = False) -> Path:
    """Convert a PDF to Markdown. Uses OCR only for scans without a text layer."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pdf_path.stem}.md"

    if not force and out_path.exists() and out_path.stat().st_mtime >= pdf_path.stat().st_mtime:
        logger.info("Skipping %s (markdown is up-to-date)", pdf_path.name)
        return out_path

    was_ocr = not _has_text_layer(pdf_path)
    with tempfile.TemporaryDirectory() as tmp:
        source = _ocr_to_temp(pdf_path, Path(tmp)) if was_ocr else pdf_path
        logger.info("Converting %s → markdown", source.name)
        md = pymupdf4llm.to_markdown(str(source), show_progress=False)

    if was_ocr:
        md = _recover_headings_from_ocr(md)
    md = _strip_noise_lines(md)
    out_path.write_text(md, encoding="utf-8")
    return out_path
