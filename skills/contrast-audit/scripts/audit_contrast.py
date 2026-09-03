#!/usr/bin/env python3
"""Project-wide WCAG contrast audit for rendered HTML."""

from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SKIP_DIRS = {".git", ".next", ".nuxt", ".venv", "build", "coverage", "dist", "node_modules", "vendor"}
HTML_SUFFIXES = {".htm", ".html"}

CONTRAST_AUDIT_JS = r"""
options => {
  const srgb = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); };
  const lum = ([r,g,b]) => .2126 * srgb(r) + .7152 * srgb(g) + .0722 * srgb(b);
  const parse = value => {
    const match = String(value || '').match(/[\d.]+/g);
    if (!match || match.length < 3) return null;
    return [+match[0], +match[1], +match[2], match.length > 3 ? +match[3] : 1];
  };
  const over = (fg, bg) => {
    const alpha = fg[3];
    return [0,1,2].map(i => fg[i] * alpha + bg[i] * (1 - alpha)).concat([1]);
  };
  const ratio = (a, b) => {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
  };
  const cssPath = element => {
    const parts = [];
    for (let node = element; node && node.nodeType === 1 && parts.length < 6; node = node.parentElement) {
      let part = node.tagName.toLowerCase();
      if (node.id) { parts.unshift(`${part}#${node.id}`); break; }
      const classes = [...node.classList].slice(0, 2);
      if (classes.length) part += '.' + classes.join('.');
      parts.unshift(part);
    }
    return parts.join(' > ');
  };
  const background = element => {
    const explicit = element.closest('[data-contrast-bg]');
    if (explicit) {
      const color = parse(explicit.getAttribute('data-contrast-bg'));
      if (color) return { color, confidence: 'declared', reason: null };
    }
    const stack = [];
    let reason = null;
    for (let node = element; node && node.nodeType === 1; node = node.parentElement || (node.ownerSVGElement ? node.ownerSVGElement.parentElement : null)) {
      const style = getComputedStyle(node);
      if (style.backgroundImage && style.backgroundImage !== 'none') reason ||= 'image-or-gradient-background';
      const color = parse(style.backgroundColor);
      if (color && color[3] > .004) {
        stack.push(color);
        if (color[3] >= .999) break;
      }
    }
    let color = [255,255,255,1];
    for (let i = stack.length - 1; i >= 0; i--) color = over(stack[i], color);
    return { color, confidence: reason ? 'review' : 'computed', reason };
  };
  const visible = element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && effectiveOpacity(element) > .01 && rect.width >= 1 && rect.height >= 1;
  };
  const effectiveOpacity = element => {
    let opacity = 1;
    for (let node = element; node && node.nodeType === 1; node = node.parentElement) {
      opacity *= +(getComputedStyle(node).opacity || 1);
    }
    return opacity;
  };

  let roots;
  if (options.rootSelector) roots = [...document.querySelectorAll(options.rootSelector)];
  else {
    roots = [...document.querySelectorAll('.slide')];
    if (!roots.length) roots = [document.body];
  }
  const failures = [], manual = [], seen = new Set();
  let audited = 0;
  roots.forEach((root, rootIndex) => {
    const elements = [root, ...root.querySelectorAll('*')];
    elements.forEach(element => {
      if (!visible(element) || element.matches(':disabled,[aria-disabled="true"],[aria-hidden="true"]')) return;
      if (element.tagName === 'CANVAS') {
        manual.push({root: rootIndex, reason: 'canvas-content', path: cssPath(element)});
        return;
      }
      const pseudo = [getComputedStyle(element, '::before').content, getComputedStyle(element, '::after').content]
        .some(content => content && content !== 'none' && content !== 'normal' && content !== '""');
      if (pseudo) manual.push({root: rootIndex, reason: 'pseudo-content', path: cssPath(element)});
      const text = [...element.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(' ').replace(/\s+/g, ' ').trim();
      if (!text) return;
      const key = `${rootIndex}:${cssPath(element)}:${text}`;
      if (seen.has(key)) return;
      seen.add(key);
      const style = getComputedStyle(element);
      const isSvg = !!element.ownerSVGElement || ['text', 'tspan'].includes(element.tagName.toLowerCase());
      let foreground = parse(isSvg ? style.fill : style.color);
      if (!foreground || foreground[3] < .05) return;
      const bg = background(isSvg ? (element.parentElement || element) : element);
      const opacity = effectiveOpacity(element);
      if (foreground[3] < 1) foreground = over(foreground, bg.color);
      const size = parseFloat(style.fontSize) || 12;
      const weight = parseInt(style.fontWeight) || 400;
      const large = size >= 24 || (size >= 18.66 && weight >= 700);
      const required = options.level === 'AAA' ? (large ? 4.5 : 7) : (large ? 3 : 4.5);
      const observed = ratio(foreground, bg.color);
      audited++;
      const record = {
        root: rootIndex, path: cssPath(element), tag: element.tagName.toLowerCase(),
        text: text.slice(0, 120), font_px: +size.toFixed(1), weight, large_text: large,
        ratio: +observed.toFixed(2), required,
        foreground: foreground.slice(0, 3).map(Math.round),
        background: bg.color.slice(0, 3).map(Math.round), confidence: bg.confidence
      };
      if (opacity < .999) manual.push({...record, reason: 'element-or-ancestor-opacity'});
      else if (isSvg && !element.closest('[data-contrast-bg]')) manual.push({...record, reason: 'svg-background-not-declared'});
      else if (bg.reason) manual.push({...record, reason: bg.reason});
      else if (observed + .001 < required) failures.push(record);
    });
  });
  return { roots: roots.length, audited, failures, manual_review: manual };
}
"""


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https", "file"}


def discover(values: list[str]) -> tuple[list[str], list[str]]:
    found: list[str] = []
    skipped: list[str] = []
    for value in values:
        if is_url(value):
            found.append(value)
            continue
        matches = [Path(item) for item in glob.glob(value, recursive=True)] or [Path(value)]
        for path in matches:
            if path.is_dir():
                for child in path.rglob("*"):
                    if any(part in SKIP_DIRS for part in child.parts):
                        continue
                    if child.is_file() and child.suffix.lower() in HTML_SUFFIXES:
                        found.append(str(child.resolve()))
            elif path.is_file() and path.suffix.lower() in HTML_SUFFIXES:
                found.append(str(path.resolve()))
            else:
                skipped.append(value)
    return list(dict.fromkeys(found)), list(dict.fromkeys(skipped))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit rendered HTML contrast against WCAG 2.2")
    parser.add_argument("targets", nargs="+", help="HTML files, URLs, directories, or glob patterns")
    parser.add_argument("--json-out", default="contrast-audit.json", help="JSON report path, or - for stdout")
    parser.add_argument("--level", choices=("AA", "AAA"), default="AA")
    parser.add_argument("--root", help="CSS selector for independently reported roots; auto-detects .slide")
    parser.add_argument("--wait-ms", type=int, default=500, help="Wait after load for fonts/rendering")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets, skipped = discover(args.targets)
    if not targets:
        print("contrast-audit: no HTML targets found", file=sys.stderr)
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("contrast-audit: Python Playwright is required (python3 -m pip install playwright && playwright install chromium)", file=sys.stderr)
        return 2

    files = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for target in targets:
            url = target if is_url(target) else Path(target).as_uri()
            try:
                page.goto(url, wait_until="load", timeout=args.timeout_ms)
                page.wait_for_timeout(args.wait_ms)
                result = page.evaluate(CONTRAST_AUDIT_JS, {"level": args.level, "rootSelector": args.root})
                status = "fail" if result["failures"] else "review" if result["manual_review"] else "pass"
                files.append({"target": target, "url": url, "status": status, **result})
            except Exception as error:
                files.append({"target": target, "url": url, "status": "error", "error": str(error)})
        browser.close()

    summary = {
        "targets": len(targets),
        "passed": sum(item["status"] == "pass" for item in files),
        "failed": sum(item["status"] == "fail" for item in files),
        "review_required": sum(item["status"] == "review" for item in files),
        "errors": sum(item["status"] == "error" for item in files),
        "failures": sum(len(item.get("failures", [])) for item in files),
        "manual_review": sum(len(item.get("manual_review", [])) for item in files),
        "skipped": len(skipped),
    }
    report = {
        "version": "1.0.0", "standard": f"WCAG 2.2 {args.level}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary, "skipped": skipped, "files": files,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out == "-":
        sys.stdout.write(payload)
    else:
        output = Path(args.json_out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(
        f"contrast-audit: {summary['targets']} HTML · {summary['failures']} failures · "
        f"{summary['manual_review']} manual review · {summary['errors']} errors",
        file=sys.stderr,
    )
    return 2 if summary["errors"] else 1 if summary["failures"] or summary["manual_review"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
