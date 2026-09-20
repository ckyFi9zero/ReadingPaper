#!/usr/bin/env python3
"""Export an isolated local or explicitly selected public static site."""
import argparse
import base64
import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import build_site
from check_site import Page, check

ROOT = build_site.ROOT
ASSETS = ['assets/style.css', 'assets/app.js', 'assets/reader-nav.js', 'assets/favicon.svg']
PROTECTED = {'paper-cards', 'notes', 'skills', 'tmp', 'scripts', 'ai-context', '.git', '.github'}


def source_path(relative):
    if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError(f'Expected a repository-relative path: {relative}')
    candidate = ROOT / relative
    if any(part.startswith('.') for part in Path(relative).parts) or candidate.is_symlink():
        raise ValueError(f'Hidden/symlink source not exportable: {relative}')
    path = candidate.resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Missing/outside source: {relative}')
    return path


def selected_papers(papers, config):
    selected, seen = [], set()
    for rule in config['papers']:
        slug = rule['slug']
        if slug in seen: raise ValueError(f'Duplicate publication rule: {slug}')
        seen.add(slug)
        matches = [p for p in papers if p['slug'] == slug]
        if len(matches) != 1: raise ValueError(f'Unknown publication paper: {slug}')
        p = copy.deepcopy(matches[0])
        allowed = rule.get('stages', [])
        if len(set(allowed)) != len(allowed) or any(k not in build_site.STAGES for k in allowed):
            raise ValueError(f'Invalid public stages: {slug}')
        available = set(p.get('stages', {})) | ({'deep-read'} if p.get('card') else set())
        if not set(allowed) <= available: raise ValueError(f'No source for public stage: {slug}')
        p['stages'] = {k: v for k, v in p.get('stages', {}).items() if k in allowed}
        if 'deep-read' not in allowed: p.pop('card', None)
        if rule.get('include_pdf') is not True: p.pop('pdf', None)
        p['reviews'] = {k: v for k, v in p.get('reviews', {}).items() if k in allowed}
        # Research questions are private by default, even for a selected paper.
        if rule.get('include_questions') is not True: p.pop('openQuestions', None)
        p['_public'] = True
        p['_embedded_approved'] = rule.get('allow_embedded_images') is True
        selected.append(p)
    if not selected:
        raise ValueError('No public papers selected. Review publish.json before exporting or deploying.')
    return selected


def export(profile='local'):
    papers = json.loads((ROOT / 'papers.json').read_text())
    config = json.loads((ROOT / 'publish.json').read_text())
    public = profile == 'public'
    chosen = selected_papers(papers, config) if public else papers
    # Render from source; never copy stale generated pages from the working tree.
    outputs, normalized = build_site.build(chosen, write=False, overview=config['overview'] is True if public else True)
    for paper in normalized:
        for stage, source in paper['_sources'].items():
            if source.suffix == '.html':
                outputs[f"papers/{paper['slug']}/{stage}.html"] = source.read_text()
        if public:
            # Remove local source-card links, without modifying the source note.
            page = f"papers/{paper['slug']}/index.html"
            outputs[page] = re.sub(r'<a href="[^\"]*">原始 Markdown</a>', '', outputs[page])
            if not paper.get('_embedded_approved'):
                for stage in paper['available']:
                    if re.search(r'data:image/', outputs[f"papers/{paper['slug']}/{stage}.html"]):
                        raise ValueError(f"{paper['slug']}: embedded paper images need explicit allow_embedded_images review")
    output = ROOT / ('_site-public' if public else '_site')
    if output.is_symlink() or (output.exists() and not (output / 'site-manifest.json').is_file()):
        raise ValueError(f'Refusing to replace an unmanaged output directory: {output.name}')
    staging = Path(tempfile.mkdtemp(prefix='.site-build-', dir=ROOT))
    before_bytes = sum(len(text.encode()) for text in outputs.values())
    extracted = set()
    try:
        for name, text in outputs.items():
            # Move embedded image bytes to content-addressed files for lazy loading/caching.
            # Pixels are not recompressed and authored HTML remains untouched.
            def extract_image(match):
                kind, encoded = match.groups()
                data = base64.b64decode(encoded, validate=True)
                digest = hashlib.sha256(data).hexdigest()
                ext = 'jpg' if kind == 'jpeg' else kind
                relative = f'assets/paper-images/{digest}.{ext}'
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                extracted.add(relative)
                return os.path.relpath(relative, str(Path(name).parent))
            text = re.sub(r'data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=]+)', extract_image, text)
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
        allowed = set(ASSETS)
        if public:
            for relative in config.get('assets', []):
                if Path(relative).parts[0] in PROTECTED or Path(relative).suffix.lower() not in ('.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.woff', '.woff2'):
                    raise ValueError(f'Only explicit image/font assets may be added: {relative}')
                source_path(relative)
                allowed.add(relative)
            for paper in chosen:
                if paper.get('pdf'): allowed.add(paper['pdf'])
        # Explicit assets first, then validate every referenced dependency.
        for relative in sorted(allowed):
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path(relative), target)
        dependencies = []
        for name in outputs:
            dependencies.extend((Path(name).parent, link) for link in Page(staging / name).links)
        for relative in ASSETS:
            if relative.endswith('.css'):
                dependencies.extend((Path(relative).parent, value.strip()) for value in re.findall(r'url\(\s*[\"\x27]?([^\)\"\x27]+)', (staging / relative).read_text()))
        for parent, value in dependencies:
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path: continue
            dest = (staging / parent / unquote(url.path)).resolve()
            if not dest.is_relative_to(staging) or url.path.startswith('/'):
                raise ValueError(f'Link leaves exported site: {parent}: {value}')
            relative = dest.relative_to(staging).as_posix()
            if dest.exists(): continue
            if public and relative not in allowed:
                raise ValueError(f'Unapproved file linked from public page: {relative}; remove link or explicitly review permitted asset')
            if Path(relative).parts[0] in {'tmp', 'skills', 'ai-context', 'scripts'}:
                raise ValueError(f'Non-site dependency: {relative}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path(relative), dest)
        exported_papers = [{'slug': p['slug'], 'category': p['category'], 'venue': p['venue'], 'stages': {k: f'{k}.html' for k in sorted(p['available'])}} for p in normalized]
        (staging / '.nojekyll').write_text('')
        total = sum(p.stat().st_size for p in staging.rglob('*') if p.is_file())
        if total > config.get('maxTotalMB', 900) * 1024**2:
            raise ValueError('Export exceeds configured size budget')
        report = {
            'profile': profile, 'papers': exported_papers,
            'htmlBytesBeforeImageExtraction': before_bytes,
            'htmlBytesAfterImageExtraction': sum((staging / name).stat().st_size for name in outputs),
            'extractedImageFiles': len(extracted), 'totalBytes': total,
            'largePages': [name for name in outputs if (staging / name).stat().st_size > config.get('warnPageMB', 2) * 1024**2],
            'files': {p.relative_to(staging).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(staging.rglob('*')) if p.is_file()},
        }
        (staging / 'site-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        check(staging)
        backup = None
        if output.exists():
            backups = ROOT / 'tmp/site-backups'
            backups.mkdir(parents=True, exist_ok=True)
            backup = backups / (output.name + '-' + staging.name.removeprefix('.site-build-'))
            output.rename(backup)
        try:
            staging.rename(output)
        except OSError:
            if backup: backup.rename(output)
            raise
        print(f'Exported {output.name}: {total / 1024**2:.2f} MiB; {len(extracted)} extracted images; {len(report["largePages"])} oversized HTML pages.')
        if backup: print(f'Previous export preserved: {backup.relative_to(ROOT)}')
        return report
    finally:
        if staging.exists(): shutil.rmtree(staging)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['local', 'public'], default='local')
    args = parser.parse_args()
    export(args.profile)
