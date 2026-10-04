#!/usr/bin/env python3
"""Render evidence-link blocks into authored stage HTML marked with sentinels."""

import argparse
import re
from pathlib import Path

from evidence import END_MARKER, EVIDENCE_STYLE, START_MARKER, load_map, render_panel


def render_text(text, data, slug, current_stage):
    """Replace exactly one marked block while preserving all authored bytes around it."""
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start < 0 or end < 0 or end < start:
        raise ValueError(f"Authored HTML is missing a valid evidence marker block: {slug}/{current_stage}.html")
    end += len(END_MARKER)
    block = EVIDENCE_STYLE + render_panel(data, slug, current_stage=current_stage)
    return text[:start] + START_MARKER + "\n" + block + "\n" + END_MARKER + text[end:]


def render_file(root, slug, stage, *, write=True):
    root = Path(root).resolve()
    path = root / "papers" / slug / f"{stage}.html"
    if not path.is_file():
        raise ValueError(f"Missing authored stage HTML: {path}")
    data = load_map(root, slug)
    if data is None:
        raise ValueError(f"Missing evidence map: {slug}")
    rendered = render_text(path.read_text(encoding="utf-8"), data, slug, stage)
    if write:
        path.write_text(rendered, encoding="utf-8")
    return rendered


def render_all(root, slug, stages=None, *, write=True, strict=False):
    stages = stages or ["first-pass", "deep-read", "code"]
    outputs = {}
    for stage in stages:
        path = Path(root) / "papers" / slug / f"{stage}.html"
        if not path.is_file():
            if strict:
                raise ValueError(f"Missing authored stage HTML: {path}")
            continue
        if START_MARKER not in path.read_text(encoding="utf-8"):
            if strict:
                raise ValueError(f"Authored HTML is missing a valid evidence marker block: {path}")
            continue
        outputs[stage] = render_file(root, slug, stage, write=write)
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--stage", action="append", choices=["first-pass", "deep-read", "code"])
    args = parser.parse_args()
    selected = args.stage or ["first-pass", "code"]
    rendered = render_all(args.root, args.slug, selected, write=True, strict=True)
    if not rendered:
        raise SystemExit("No marked authored stage pages were rendered")
    print(f"Rendered evidence links: {args.slug}/{', '.join(rendered)}")
