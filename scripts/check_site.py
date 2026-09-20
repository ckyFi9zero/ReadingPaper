#!/usr/bin/env python3
"""Check library navigation, fragments, assets, and declared reading stages offline."""
import json
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links, self.ids, self.cards = [], set(), []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ["href", "src"]:
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get('poster'):
            self.links.append(attrs['poster'])
        if attrs.get('srcset') and not attrs['srcset'].startswith('data:'):
            self.links.extend(item.strip().split()[0] for item in attrs['srcset'].split(',') if item.strip())
        if "paper-card" in attrs.get("class", "").split():
            self.cards.append(attrs)


def check(root=ROOT, papers=None):
    root = Path(root).resolve()
    if papers is None:
        manifest = root / 'site-manifest.json'
        papers = json.loads(manifest.read_text())['papers'] if manifest.exists() else json.loads((root / 'papers.json').read_text())
    paths = [root / "index.html", root / "overview.html"]
    for paper in papers:
        paths += [root / "papers" / paper["slug"] / f"{stage}.html" for stage in ["index", "first-pass", "deep-read", "code"]]
    pages, errors, links = {}, [], 0
    for path in paths:
        if not path.is_file():
            errors.append(f"Missing page: {path}")
        else:
            pages[path.resolve()] = Page(path)
    for path, page in pages.items():
        for value in page.links:
            url = urlsplit(value)
            if url.scheme in ('file', 'javascript', 'vbscript'):
                errors.append(f"{path.relative_to(root)}: unsafe or machine-local URL {value[:120]}")
                continue
            if url.scheme or url.netloc:
                continue
            if url.path.startswith('/'):
                errors.append(f"{path.relative_to(root)}: root-absolute link breaks project-site prefixes: {value}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            links += 1
            if not target.is_relative_to(root) or not target.is_file():
                errors.append(f"{path.relative_to(root)}: broken/outside link {value}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{path.relative_to(root)}: missing anchor {value}")
    for path in root.glob('assets/**/*.css'):
        for value in re.findall(r'url\(\s*[\"\x27]?([^\)\"\x27]+)', path.read_text()):
            url = urlsplit(value.strip())
            if url.scheme or url.netloc: continue
            target = (path.parent / unquote(url.path)).resolve()
            if url.path.startswith('/') or not target.is_relative_to(root) or not target.is_file():
                errors.append(f'{path.relative_to(root)}: missing/outside CSS resource {value}')
    home = pages.get(root / "index.html")
    if home:
        if len(home.cards) != len(papers):
            errors.append("Homepage paper count differs from manifest")
        by_slug = {card.get("data-slug"): card for card in home.cards}
        for paper in papers:
            expected = set(paper.get("stages", {})) | ({"deep-read"} if paper.get("card") else set())
            card = by_slug.get(paper['slug'])
            if card is None or set(card["data-stages"].split()) != expected:
                errors.append(f"Wrong reading status: {paper['slug']}")
            if card is None or card.get('data-category') != paper.get('category', 'uncategorized'):
                errors.append(f"Wrong paper category: {paper['slug']}")
            if card is None or card.get('data-venue') != paper.get('venue', '').strip():
                errors.append(f"Wrong publication venue: {paper['slug']}")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"PASS: {len(pages)} HTML pages, {links} local links/assets/fragments, {len(papers)} paper statuses.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    check(args.root)
