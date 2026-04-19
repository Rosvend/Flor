from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from ...infrastructure.knowledge_base.chroma_knowledge_base import ChromaKnowledgeBase
from ...infrastructure.knowledge_base.chunker import chunk_markdown
from ...infrastructure.knowledge_base.pdf_to_markdown import convert

logger = logging.getLogger("build_kb")

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INPUT = REPO_ROOT / "docs"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "knowledge_base"
DEFAULT_CHROMA = REPO_ROOT / "backend" / ".knowledge_base" / "chroma"


def _iter_pdfs(input_dir: Path, only: str | None) -> list[Path]:
    all_pdfs = sorted(p for p in input_dir.glob("*.pdf") if p.is_file())
    if only:
        match = [p for p in all_pdfs if p.name == only or p.stem == only]
        if not match:
            raise SystemExit(f"No PDF matched --only {only!r} in {input_dir}")
        return match
    return all_pdfs


def run(
    input_dir: Path = DEFAULT_INPUT,
    md_out: Path = DEFAULT_MD_OUT,
    chroma_dir: Path = DEFAULT_CHROMA,
    only: str | None = None,
    rebuild: bool = False,
    dry_run: bool = False,
    force_reconvert: bool = False,
) -> int:
    pdfs = _iter_pdfs(input_dir, only)
    if not pdfs:
        logger.warning("No PDFs found in %s", input_dir)
        return 0

    kb: ChromaKnowledgeBase | None = None
    if not dry_run:
        logger.info("Initialising Chroma at %s (first run downloads the embedding model)…", chroma_dir)
        kb = ChromaKnowledgeBase(persist_dir=chroma_dir)
        if rebuild:
            logger.info("--rebuild: dropping existing collection")
            kb.reset()

    total_chunks = 0
    for pdf in pdfs:
        started = time.perf_counter()
        md_path = convert(pdf, md_out, force=force_reconvert)
        entries = chunk_markdown(
            md_path,
            source_pdf=pdf.name,
            extra_metadata={"visibility": "public"},
        )
        headings = len({e.heading_path for e in entries if e.heading_path})
        took = time.perf_counter() - started

        if kb is not None:
            kb.upsert(entries)

        total_chunks += len(entries)
        logger.info(
            "%s → %d chunks, %d unique headings, %.1fs%s",
            pdf.name, len(entries), headings, took,
            " (dry-run, not indexed)" if dry_run else "",
        )

    logger.info("Done. Total chunks: %d across %d PDF(s).", total_chunks, len(pdfs))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert PDFs in docs/ to markdown, chunk, and index into Chroma.",
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA)
    parser.add_argument("--only", type=str, default=None,
                        help="Process only this PDF (filename or stem).")
    parser.add_argument("--rebuild", action="store_true",
                        help="Drop the Chroma collection before indexing.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Convert + chunk but skip embedding/indexing.")
    parser.add_argument("--force-reconvert", action="store_true",
                        help="Re-run PDF→MD even if the markdown is up-to-date.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    return run(
        input_dir=args.input_dir,
        md_out=args.md_out,
        chroma_dir=args.chroma_dir,
        only=args.only,
        rebuild=args.rebuild,
        dry_run=args.dry_run,
        force_reconvert=args.force_reconvert,
    )


if __name__ == "__main__":
    sys.exit(main())
