#!/usr/bin/env python3
"""course_sync.py: keeps token-cheap text copies of a course folder in _text/.

Converts slides, readings, exercises and notes (PDF, PPTX, DOCX, XLSX, IPYNB,
CSV, legacy Office files) into Markdown once, then only touches files that are
new, changed, renamed or deleted. Pages that depend on images or charts are
flagged so Claude knows when to look at the original.

Commands
  install            copy this script into <course>/_text/_tools/
  status             show what is new, changed, removed or not yet indexed
  sync               convert what changed and update the manifest
  render FILE PAGES  render PDF pages (e.g. 4 or 4,7-8) to PNG for viewing
  mark-indexed       record that INDEX.md covers these files (--all or paths)
  stats              token estimate: originals vs text copies
  doctor             show which PDF and render backends are available

Only Python's standard library is required for Office files. PDFs need
PyMuPDF (best: text + rendering) or pypdf (text only): pip install pymupdf
"""

import argparse
import csv
import datetime as _dt
import fnmatch
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "1.0.1"
TEXT_DIR = "_text"
MANIFEST = ".manifest.json"
IGNORE_FILE = ".ignore"

PDF_EXT = {".pdf"}
OFFICE_EXT = {".pptx", ".docx", ".xlsx", ".xlsm"}
LEGACY_EXT = {".doc", ".rtf", ".odt", ".ppt", ".odp", ".key", ".pages", ".xls", ".ods"}
DATA_EXT = {".ipynb", ".csv", ".tsv"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".bmp", ".tif", ".tiff"}
NATIVE_TEXT_EXT = {".md", ".txt", ".tex", ".py", ".r", ".rmd", ".qmd", ".sql", ".json", ".html", ".m", ".do"}
MEDIA_EXT = {".mp4", ".mov", ".m4a", ".mp3", ".wav", ".avi", ".mkv", ".webm"}
ARCHIVE_EXT = {".zip", ".rar", ".7z", ".tar", ".gz"}
CONVERT_EXT = PDF_EXT | OFFICE_EXT | LEGACY_EXT | DATA_EXT | IMAGE_EXT

SKIP_DIRS = {TEXT_DIR, ".claude", ".git", "__pycache__", "node_modules", ".ipynb_checkpoints", ".venv", "venv"}
SKIP_FILES = {"CLAUDE.md", "AGENTS.md", ".DS_Store", "Thumbs.db", "desktop.ini"}

PDF_TOKENS_PER_PAGE = 1500   # rough cost of handing Claude a PDF page directly
MAX_XLSX_CELLS = 3000        # per sheet
MAX_CHART_POINTS = 40        # per series
MAX_NB_OUTPUT_LINES = 15     # per notebook cell output
MAX_CSV_ROWS = 30


# --------------------------------------------------------------------------- paths

def default_root(arg_root):
    if arg_root:
        return Path(arg_root).expanduser().resolve()
    here = Path(__file__).resolve().parent
    if here.name == "_tools" and here.parent.name == TEXT_DIR:
        return here.parent.parent
    cur = Path.cwd().resolve()
    for p in [cur, *cur.parents]:
        if (p / TEXT_DIR / MANIFEST).exists():
            return p
    return cur


def out_path_for(rel):
    """Text copy keeps the source extension so X.pdf and X.pptx never collide."""
    return f"{TEXT_DIR}/{rel}.md"


def load_ignore(root):
    f = root / TEXT_DIR / IGNORE_FILE
    if not f.exists():
        return []
    pats = []
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pats.append(line)
    return pats


def ignored(rel, pats):
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p.rstrip("/") + "/*") for p in pats)


def scan(root):
    """Return (convertible, other) where each is {rel: kind}."""
    pats = load_ignore(root)
    conv, other = {}, {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name in SKIP_FILES or name.startswith(".") or name.startswith("~$") or name.startswith(".~lock"):
                continue
            full = Path(dirpath) / name
            rel = full.relative_to(root).as_posix()
            if ignored(rel, pats):
                continue
            ext = full.suffix.lower()
            if ext in CONVERT_EXT:
                conv[rel] = ext
            elif ext in NATIVE_TEXT_EXT:
                other[rel] = "text"
            elif ext in MEDIA_EXT:
                other[rel] = "media"
            elif ext in ARCHIVE_EXT:
                other[rel] = "archive"
            else:
                other[rel] = "other"
    return conv, other


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(root):
    f = root / TEXT_DIR / MANIFEST
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": VERSION, "files": {}}


def save_manifest(root, man):
    man["version"] = VERSION
    man["updated"] = _dt.datetime.now().isoformat(timespec="seconds")
    f = root / TEXT_DIR / MANIFEST
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(man, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


# --------------------------------------------------------------------------- text cleanup

BULLET_RE = re.compile("^[•●▪■◦○◆◇►▶➢➤·‣⁃∙]\\s*")
PAGENUM_RE = re.compile(r"^(?:(?:page|seite|slide|folie|p\.)\s*)?\d{1,4}(?:\s*(?:/|of|von|de)\s*\d{1,4})?$", re.I)


def clean_line(s):
    s = s.replace(" ", " ").replace("\t", " ").replace("​", "")
    s = re.sub(r" {2,}", " ", s).strip()
    s = BULLET_RE.sub("- ", s)
    if s.startswith((">", "#")):
        s = "\\" + s   # keep generated text apart from headings and Claude's notes
    return s


def clean_lines(text):
    out = []
    for raw in (text or "").splitlines():
        s = clean_line(raw)
        if s:
            out.append(s)
    return out


def strip_repeated(pages):
    """Drop page numbers and header/footer lines that repeat on most pages."""
    n = len(pages)
    removed = []
    if n >= 3:
        counts = {}
        for lines in pages:
            for key in {re.sub(r"\d+", "#", l.lower()) for l in lines if len(l) <= 100}:
                counts[key] = counts.get(key, 0) + 1
        need = max(3, 0.5 * n) if n >= 6 else n      # short files: only lines on every page
        rep = {k for k, c in counts.items() if c >= need and k.strip("#- ")}
        if rep:
            seen = set()
            new_pages = []
            for lines in pages:
                keep = []
                for l in lines:
                    k = re.sub(r"\d+", "#", l.lower())
                    if k in rep:
                        if k not in seen:
                            seen.add(k)
                            removed.append(l)
                        continue
                    keep.append(l)
                new_pages.append(keep)
            pages = new_pages
    return [drop_page_numbers(lines, i + 1) for i, lines in enumerate(pages)], removed


def drop_page_numbers(lines, page_no):
    """Remove a page-number line only at the top or bottom and only if it matches this page."""
    edge = set(range(min(2, len(lines)))) | set(range(max(0, len(lines) - 2), len(lines)))
    out = []
    for i, l in enumerate(lines):
        if i in edge and PAGENUM_RE.match(l):
            m = re.search(r"\d+", l)
            if m and abs(int(m.group()) - page_no) <= 3:
                continue
        out.append(l)
    return out


def ranges(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


# --------------------------------------------------------------------------- document model

class Doc:
    """A converted file: header lines plus ordered sections (key, flag, lines)."""

    def __init__(self, kind, units=None):
        self.kind = kind
        self.units = units          # pages / slides / sheets
        self.meta = []              # extra header lines
        self.sections = []          # [key, flag, lines]
        self.visual = []            # section numbers flagged visual

    def add(self, key, lines, flag=None, num=None):
        self.sections.append([key, flag, lines])
        if flag and num is not None:
            self.visual.append(num)


def section_key(header):
    h = header[3:] if header.startswith("## ") else header
    h = re.sub(r"\s*\[[^\]]*\]\s*$", "", h)        # drop [visual ...] flag
    m = re.match(r"^((?:Page|Slide|Sheet|Cell|Image)\b[^:]*)", h)
    return (m.group(1) if m else h).strip()


NUM_LINE_RE = re.compile(r"^[-+]?[$€£]?\d[\d.,]*\s?%?$")


def merge_numeric_runs(lines):
    """Axis ticks and counters ('10', '20', '30' …) on one line instead of many."""
    out, run = [], []
    for l in lines + [None]:
        if l is not None and NUM_LINE_RE.match(l):
            run.append(l)
            continue
        if len(run) >= 4:
            out.append(" ".join(run))
        else:
            out.extend(run)
        run = []
        if l is not None:
            out.append(l)
    return out


def read_notes(md_path):
    """Claude's own notes ('> ' lines) per section, so a re-sync keeps them."""
    notes = {}
    if not md_path.exists():
        return notes
    key, fence = None, False
    for line in md_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if line.startswith("## "):
            key = section_key(line)
        elif line.startswith(">") and key is not None:
            notes.setdefault(key, []).append(line)
    return notes


def render_md(doc, rel, notes):
    title = Path(rel).name
    units = f" · {doc.units}" if doc.units else ""
    out = [f"# {title}", "",
           f"Source: `{rel}` · {doc.kind}{units} · converted {_dt.date.today().isoformat()} by course_sync {VERSION}"]
    if doc.visual:
        word = "Slides" if doc.kind == "PowerPoint" else "Pages"
        out.append(f"{word} with visual content (look at the original when the question depends on them): {ranges(doc.visual)}")
    out += doc.meta
    out.append("")
    used = set()
    for key, flag, lines in doc.sections:
        out.append(f"## {key}" + (f" [{flag}]" if flag else ""))
        out.append("")
        out += merge_numeric_runs(lines) if lines else ["_(no text)_"]
        k = section_key("## " + key)
        if k in notes:
            out.append("")
            out += notes[k]
            used.add(k)
        out.append("")
    left = [k for k in notes if k not in used]
    if left:
        out += ["## Notes from an earlier version (the source changed, check they still apply)", ""]
        for k in left:
            out.append(f"From {k}:")
            out += notes[k]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# --------------------------------------------------------------------------- PDF

def mupdf():
    """PyMuPDF module or None (new name 'pymupdf', old name 'fitz')."""
    try:
        import pymupdf
        return pymupdf
    except Exception:
        pass
    try:
        import fitz
        return fitz
    except Exception:
        return None


def pdf_backend():
    if mupdf():
        return "pymupdf"
    try:
        import pypdf  # noqa: F401
        return "pypdf"
    except Exception:
        pass
    if shutil.which("pdftotext"):
        return "pdftotext"
    return None


PATH_OP_RE = re.compile(rb"(?<![A-Za-z/])(?:re|l|c|v|y)(?![A-Za-z])")
TEXT_OBJ_RE = re.compile(rb"BT.*?ET", re.S)
AXIS_RE = re.compile(r"^[-+]?[$€£]?\d[\d.,]*\s?%?$")


def count_path_ops(data):
    try:
        return len(PATH_OP_RE.findall(TEXT_OBJ_RE.sub(b"", data or b"")))
    except Exception:
        return 0


def convert_pdf(path):
    backend = pdf_backend()
    if backend is None:
        raise RuntimeError("no PDF backend: run  pip install pymupdf  (or pypdf)")
    pages, imgs, draws = [], [], []
    if backend == "pymupdf":
        fitz = mupdf()
        with fitz.open(path) as d:
            xref_pages = {}
            raw_imgs = []
            for i, p in enumerate(d):
                pages.append(p.get_text("text"))
                xr = {im[0] for im in p.get_images(full=True)}
                raw_imgs.append(xr)
                for x in xr:
                    xref_pages[x] = xref_pages.get(x, 0) + 1
                try:   # number of drawn segments: charts, diagrams, trees
                    draws.append(sum(len(dr.get("items", [])) for dr in p.get_drawings()))
                except Exception:
                    draws.append(0)
            n = len(pages)
            template = {x for x, c in xref_pages.items() if n >= 4 and c >= 0.6 * n}   # logos, backgrounds
            imgs = [len(s - template) for s in raw_imgs]
    elif backend == "pypdf":
        import logging
        import pypdf
        logging.getLogger("pypdf").setLevel(logging.ERROR)
        r = pypdf.PdfReader(str(path))
        ref_pages, raw, form_ops, page_forms = {}, [], {}, []
        for p in r.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
            refs, ops = set(), 0
            try:
                c = p.get_contents()
                ops = count_path_ops(c.get_data() if c is not None else b"")
                xo = p["/Resources"].get_object().get("/XObject")
                if xo:
                    xo = xo.get_object()
                    for name in xo:
                        ind = xo.raw_get(name)
                        o = ind.get_object()
                        rid = getattr(ind, "idnum", None) or name
                        if o.get("/Subtype") == "/Image":
                            refs.add(rid)
                        elif o.get("/Subtype") == "/Form":
                            form_ops.setdefault(rid, count_path_ops(o.get_data()))
                            page_forms.append((len(pages) - 1, rid))
                            ref_pages[("f", rid)] = ref_pages.get(("f", rid), 0) + 1
            except Exception:
                pass
            draws.append(ops)
            raw.append(refs)
            for x in refs:
                ref_pages[x] = ref_pages.get(x, 0) + 1
        n = len(pages)
        template = {x for x, c in ref_pages.items() if n >= 4 and c >= 0.6 * n}
        imgs = [len(s - template) for s in raw]
        for i, rid in page_forms:          # charts often live in form objects
            if not (n >= 4 and ref_pages.get(("f", rid), 0) >= 0.6 * n):
                draws[i] += form_ops.get(rid, 0)
        draws = [d // 3 for d in draws]    # path operators → rough number of shapes, like PyMuPDF's count
    else:
        txt = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout
        pages = txt.split("\f")
        if pages and not pages[-1].strip():
            pages = pages[:-1]
        imgs = [0] * len(pages)
        draws = [0] * len(pages)

    if draws:   # drawings every page shares (frames, backgrounds) are the template, not content
        base = sorted(draws)[len(draws) // 4]
        draws = [max(0, d - base) for d in draws]
    lines = [clean_lines(t) for t in pages]
    lines, removed = strip_repeated(lines)
    doc = Doc("PDF", f"{len(lines)} pages")
    total_chars = 0
    for i, ls in enumerate(lines):
        chars = sum(len(l) for l in ls)
        total_chars += chars
        flag = None
        if chars < 20:
            flag = "visual: no text" + (f", {imgs[i]} img" if imgs[i] else "")
        elif imgs[i] and chars < 600:
            flag = f"visual: {imgs[i]} img"
        elif draws[i] >= 40:
            flag = "visual: chart or diagram"
        elif sum(1 for l in ls if AXIS_RE.match(l)) >= 6:
            flag = "visual: chart or table (many numbers)"
        elif imgs[i] >= 2:
            flag = f"visual: {imgs[i]} img"
        doc.add(f"Page {i + 1}", ls, flag, i + 1)
    if lines and total_chars / len(lines) < 40:
        doc.meta.append("Looks scanned or image-based: almost no text layer. Render pages to read them, then add notes.")
    if removed:
        shown = "; ".join(f'"{r[:60]}"' for r in removed[:6])
        doc.meta.append(f"Repeated header/footer lines removed: {shown}")
    if backend == "pdftotext":
        doc.meta.append("Converted with pdftotext: image counts unavailable, so visual pages may be missed.")
    return doc


# --------------------------------------------------------------------------- Office XML helpers

R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def read_rels(z, part):
    """Relationships of a part: {rId: (abs_target, type)}."""
    d, name = posixpath.split(part)
    relp = posixpath.join(d, "_rels", name + ".rels")
    out = {}
    if relp not in z.namelist():
        return out
    root = ET.fromstring(z.read(relp))
    for r in root:
        tgt = r.get("Target", "")
        if r.get("TargetMode") == "External":
            continue
        absn = tgt.lstrip("/") if tgt.startswith("/") else posixpath.normpath(posixpath.join(d, tgt))
        out[r.get("Id")] = (absn, r.get("Type", ""))
    return out


def texts(el, tag="t"):
    return "".join(t.text or "" for t in el.iter() if local(t.tag) == tag)


def fmt_num(v):
    try:
        f = float(v)
    except Exception:
        return v
    if f.is_integer() and abs(f) < 1e15:
        return str(int(f))
    return f"{f:.6g}"


def chart_lines(z, part):
    try:
        root = ET.fromstring(z.read(part))
    except Exception:
        return ["[chart: could not read]"]
    kinds = sorted({local(e.tag) for e in root.iter()
                    if local(e.tag).endswith("Chart") and local(e.tag) not in ("chart",)})
    title = ""
    for e in root.iter():
        if local(e.tag) == "title":
            title = texts(e).strip()
            break
    out = [f"[chart: {', '.join(kinds) or 'chart'}" + (f' "{title}"' if title else "") + "]"]

    def pts(el):
        vals = {}
        for p in el.iter():
            if local(p.tag) == "pt":
                v = next((c.text for c in p if local(c.tag) == "v"), "")
                vals[int(p.get("idx", len(vals)))] = v or ""
        return [vals[k] for k in sorted(vals)]

    for ser in (e for e in root.iter() if local(e.tag) == "ser"):
        name, cats, vals, xs = "", [], [], []
        for c in ser:
            t = local(c.tag)
            if t == "tx":
                name = " ".join(pts(c)) or texts(c)
            elif t == "cat":
                cats = pts(c)
            elif t in ("val", "yVal"):
                vals = pts(c)
            elif t == "xVal":
                xs = pts(c)
        labels = cats or xs
        pairs = []
        for i, v in enumerate(vals[:MAX_CHART_POINTS]):
            lab = labels[i] if i < len(labels) else str(i + 1)
            pairs.append(f"{fmt_num(lab)}={fmt_num(v)}")
        more = f" … (+{len(vals) - MAX_CHART_POINTS})" if len(vals) > MAX_CHART_POINTS else ""
        out.append(f"- series {name or '?'}: " + ", ".join(pairs) + more)
    return out


def table_lines(tbl, cell_tag, row_tag, para_tag="p"):
    rows = []
    for tr in (e for e in tbl.iter() if local(e.tag) == row_tag):
        cells = []
        for tc in (e for e in tr if local(e.tag) == cell_tag):
            ps = [texts(p).strip() for p in tc.iter() if local(p.tag) == para_tag]
            cells.append(" ".join(p for p in ps if p).replace("|", "/"))
        if any(cells):
            rows.append("| " + " | ".join(cells) + " |")
    return rows


# --------------------------------------------------------------------------- PPTX

def convert_pptx(path):
    z = zipfile.ZipFile(path)
    pres = ET.fromstring(z.read("ppt/presentation.xml"))
    prels = read_rels(z, "ppt/presentation.xml")
    order = [prels[s.get(R_NS + "id")][0] for s in pres.iter()
             if local(s.tag) == "sldId" and s.get(R_NS + "id") in prels]
    doc = Doc("PowerPoint", f"{len(order)} slides")
    for n, part in enumerate(order, 1):
        root = ET.fromstring(z.read(part))
        rels = read_rels(z, part)
        title, lines, notes = "", [], []
        info = {"img": 0, "chart": 0, "diagram": 0, "media": 0}

        def ph_type(sp):
            for e in sp.iter():
                if local(e.tag) == "ph":
                    return e.get("type", "body")
            return None

        def walk(el):
            nonlocal title
            for ch in el:
                t = local(ch.tag)
                if t == "sp":
                    ph = ph_type(ch)
                    if ph in ("sldNum", "dt", "ftr"):
                        continue
                    paras = [texts(p).strip() for p in ch.iter() if local(p.tag) == "p"]
                    paras = [clean_line(p) for p in paras if p.strip()]
                    if ph in ("title", "ctrTitle") and paras and not title:
                        title = " ".join(paras)
                        continue
                    lines.extend(paras)
                elif t == "grpSp":
                    walk(ch)
                elif t == "pic":
                    info["media" if any(local(e.tag) in ("videoFile", "audioFile") for e in ch.iter()) else "img"] += 1
                elif t == "graphicFrame":
                    tbl = next((e for e in ch.iter() if local(e.tag) == "tbl"), None)
                    if tbl is not None:
                        lines.extend(table_lines(tbl, "tc", "tr"))
                        continue
                    ch_ref = next((e for e in ch.iter() if local(e.tag) == "chart"), None)
                    if ch_ref is not None and ch_ref.get(R_NS + "id") in rels:
                        info["chart"] += 1
                        lines.extend(chart_lines(z, rels[ch_ref.get(R_NS + "id")][0]))
                        continue
                    dgm = next((e for e in ch.iter() if local(e.tag) == "relIds"), None)
                    if dgm is not None:
                        info["diagram"] += 1
                        dm = rels.get(dgm.get(R_NS + "dm"))
                        if dm:
                            try:
                                dtext = [texts(p).strip() for p in ET.fromstring(z.read(dm[0])).iter() if local(p.tag) == "p"]
                                dtext = [d for d in dtext if d]
                                if dtext:
                                    lines.append("[diagram] " + " → ".join(dtext))
                            except Exception:
                                pass
                    else:
                        info["img"] += 1
                elif t in ("cxnSp",):
                    continue

        tree = next((e for e in root.iter() if local(e.tag) == "spTree"), None)
        if tree is not None:
            walk(tree)
        for rid, (tgt, typ) in rels.items():
            if typ.endswith("/notesSlide"):
                try:
                    nroot = ET.fromstring(z.read(tgt))
                    for sp in (e for e in nroot.iter() if local(e.tag) == "sp"):
                        if ph_type(sp) in ("sldNum", "sldImg", "dt", "ftr", "hdr"):
                            continue
                        for p in (e for e in sp.iter() if local(e.tag) == "p"):
                            s = clean_line(texts(p))
                            if s:
                                notes.append(s)
                except Exception:
                    pass
        if notes:
            lines += ["", "Speaker notes:"] + notes
        hidden = root.get("show") == "0"
        chars = sum(len(l) for l in lines) + len(title)
        bits = []
        if info["chart"]:
            bits.append("chart, data below")
        if info["diagram"]:
            bits.append("diagram")
        if info["img"]:
            bits.append(f"{info['img']} img")
        if info["media"]:
            bits.append("video/audio")
        flag = None
        if bits and (chars < 600 or info["chart"] or info["diagram"] or info["img"] >= 2):
            flag = "visual: " + ", ".join(bits)
        elif chars < 20:
            flag = "visual: no text"
        if hidden:
            flag = (flag + ", hidden slide") if flag else "hidden slide"
        key = f"Slide {n}" + (f": {title}" if title else "")
        doc.add(key, lines, flag, n if flag and flag != "hidden slide" else None)
    return doc


# --------------------------------------------------------------------------- DOCX

def convert_docx(path):
    z = zipfile.ZipFile(path)
    part = "word/document.xml"
    root = ET.fromstring(z.read(part))
    rels = read_rels(z, part)
    body = next(e for e in root.iter() if local(e.tag) == "body")
    doc = Doc("Word")
    cur_key, cur = "Text", []
    n_img = 0
    heads = 0

    def para(p):
        nonlocal n_img
        out = []
        for e in p.iter():
            t = local(e.tag)
            if t == "t":
                out.append(e.text or "")
            elif t in ("tab",):
                out.append(" ")
            elif t in ("br", "cr"):
                out.append("\n")
            elif t == "chart" and e.get(R_NS + "id") in rels:
                out.append("\n" + "\n".join(chart_lines(z, rels[e.get(R_NS + "id")][0])) + "\n")
            elif t in ("drawing", "pict"):
                if not any(local(x.tag) == "chart" for x in e.iter()):
                    n_img += 1
                    out.append(" [image] ")
        return "".join(out)

    def style(p):
        lvl, is_list = None, False
        for e in p.iter():
            t = local(e.tag)
            if t == "pStyle":
                v = (e.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val") or "").lower()
                m = re.search(r"(heading|berschrift|titre|titolo|título|kop)\s*(\d)", v)
                if m:
                    lvl = int(m.group(2))
                elif v in ("title", "titel"):
                    lvl = 1
            elif t == "numPr":
                is_list = True
        return lvl, is_list

    for el in body:
        t = local(el.tag)
        if t == "p":
            txt = para(el)
            lvl, is_list = style(el)
            ls = clean_lines(txt)
            if not ls:
                continue
            if lvl and lvl <= 2:
                if cur or cur_key != "Text":
                    doc.add(cur_key, cur)
                cur_key, cur = " ".join(ls).lstrip("\\"), []
                heads += 1
            elif lvl:
                cur.append("### " + " ".join(ls).lstrip("\\"))
            else:
                if is_list:
                    ls = [l if l.startswith("- ") else "- " + l for l in ls]
                cur.extend(ls)
        elif t == "tbl":
            cur.extend(table_lines(el, "tc", "tr"))
    if cur or not doc.sections:
        doc.add(cur_key, cur)
    if n_img:
        doc.meta.append(f"Contains {n_img} embedded image(s), marked [image] in the text.")
    return doc


# --------------------------------------------------------------------------- XLSX

def col_letters(ref):
    m = re.match(r"([A-Z]+)(\d+)", ref or "")
    return (m.group(1), int(m.group(2))) if m else ("?", 0)


def col_num(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def col_name(n):
    out = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        out = chr(65 + r) + out
    return out


CELL_REF_RE = re.compile(r"(?<![A-Za-z_\d!'\.])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\d(A-Za-z_])")


def shift_formula(formula, src, dst):
    """Rewrite a shared formula from its master cell to this cell, like Excel's copy."""
    (sc, sr), (dc, dr) = col_letters(src), col_letters(dst)
    dcol, drow = col_num(dc) - col_num(sc), dr - sr
    parts = re.split(r'("[^"]*")', formula)      # leave string literals alone

    def fix(m):
        c = m.group(2) if m.group(1) else col_name(col_num(m.group(2)) + dcol)
        r = m.group(4) if m.group(3) else str(int(m.group(4)) + drow)
        return f"{m.group(1)}{c}{m.group(3)}{r}"
    return "".join(p if i % 2 else CELL_REF_RE.sub(fix, p) for i, p in enumerate(parts))


def convert_xlsx(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    wrels = read_rels(z, "xl/workbook.xml")
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            shared.append(texts(si))
    sheets = [(s.get("name"), wrels.get(s.get(R_NS + "id"), (None,))[0], s.get("state"))
              for s in wb.iter() if local(s.tag) == "sheet"]
    doc = Doc("Excel", f"{len(sheets)} sheets")
    names = [(d.get("name"), d.text or "") for d in wb.iter() if local(d.tag) == "definedName"]
    for num, (name, part, state) in enumerate(sheets, 1):
        if not part or part not in z.namelist():
            continue
        root = ET.fromstring(z.read(part))
        shared_f = {}
        rows, count, total = [], 0, 0
        for row in (e for e in root.iter() if local(e.tag) == "row"):
            cells = []
            for c in (e for e in row if local(e.tag) == "c"):
                ref, typ = c.get("r"), c.get("t")
                f_el = next((e for e in c if local(e.tag) == "f"), None)
                v_el = next((e for e in c if local(e.tag) == "v"), None)
                v = v_el.text if v_el is not None else None
                if typ == "s" and v is not None:
                    try:
                        v = shared[int(v)]
                    except Exception:
                        pass
                elif typ == "inlineStr":
                    v = texts(c)
                elif typ == "b" and v is not None:
                    v = "TRUE" if v == "1" else "FALSE"
                elif v is not None and typ != "str" and typ != "e":
                    v = fmt_num(v)
                formula = None
                if f_el is not None:
                    if f_el.text:
                        formula = f_el.text
                        if f_el.get("t") == "shared":
                            shared_f[f_el.get("si")] = (ref, f_el.text)
                    elif f_el.get("t") == "shared" and f_el.get("si") in shared_f:
                        src, ftxt = shared_f[f_el.get("si")]
                        formula = shift_formula(ftxt, src, ref)
                if v in (None, "") and not formula:
                    continue
                total += 1
                if count >= MAX_XLSX_CELLS:
                    continue
                count += 1
                col, _ = col_letters(ref)
                val = str(v if v is not None else "").replace("\n", " ").replace("|", "/")
                cells.append(f"{col}: ={formula} → {val}" if formula else f"{col}: {val}")
            if cells:
                rows.append(f"{row.get('r')} | " + " | ".join(cells))
        if total > count:
            rows.append(f"… {total - count} more cells not shown; open the file for the rest.")
        charts = []
        for rid, (tgt, typ) in read_rels(z, part).items():
            if typ.endswith("/drawing"):
                for rid2, (tgt2, typ2) in read_rels(z, tgt).items():
                    if typ2.endswith("/chart"):
                        charts.extend(chart_lines(z, tgt2))
        rows += charts
        flag = "visual: chart, data below" if charts else None
        key = f"Sheet {num}: {name}" + (" (hidden)" if state in ("hidden", "veryHidden") else "")
        doc.add(key, rows, flag, num if flag else None)
    if names:
        solver = [n for n in names if (n[0] or "").lower().startswith("solver_")]
        other = [n for n in names if n not in solver and not (n[0] or "").startswith("_xlnm")]
        lines = []
        if solver:
            lines.append("Solver model (from defined names):")
            lines += [f"- {k}: {v}" for k, v in solver[:60]]
        if other:
            lines.append("Named ranges:")
            lines += [f"- {k}: {v}" for k, v in other[:60]]
        if lines:
            doc.add("Defined names", lines)
    return doc


# --------------------------------------------------------------------------- notebooks, csv, legacy, images

def convert_ipynb(path):
    nb = json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))
    lang = (nb.get("metadata", {}).get("kernelspec", {}) or {}).get("language", "python")
    doc = Doc("Notebook", f"{len(nb.get('cells', []))} cells")
    key, cur = "Notebook", []
    for cell in nb.get("cells", []):
        src = "".join(cell.get("source", "")) if isinstance(cell.get("source"), list) else cell.get("source", "")
        if cell.get("cell_type") == "markdown":
            m = re.match(r"^\s*#{1,2}\s+(.+)", src)
            if m:
                if cur:
                    doc.add(key, cur)
                key, cur = m.group(1).strip(), []
                src = src[m.end():]
            for l in src.strip().splitlines():
                if l.strip():
                    l = l.rstrip()
                    if re.match(r"^#{1,2}\s", l):
                        l = "### " + l.lstrip("# ")      # keep ## for real sections only
                    elif l.startswith(">"):
                        l = "\\" + l
                    cur.append(l)
        elif cell.get("cell_type") == "code" and src.strip():
            cur += [f"```{lang}", src.rstrip(), "```"]
            outs = []
            for o in cell.get("outputs", []):
                if o.get("output_type") == "stream":
                    outs += "".join(o.get("text", "")).splitlines()
                elif o.get("output_type") in ("execute_result", "display_data"):
                    data = o.get("data", {})
                    if any(k.startswith("image/") for k in data):
                        outs.append("[output: image/plot, run the notebook or open it to see]")
                    elif "text/plain" in data:
                        outs += "".join(data["text/plain"]).splitlines()
                elif o.get("output_type") == "error":
                    outs.append(f"[error: {o.get('ename')}: {o.get('evalue')}]")
            if outs:
                more = len(outs) - MAX_NB_OUTPUT_LINES
                outs = outs[:MAX_NB_OUTPUT_LINES] + ([f"… {more} more output lines"] if more > 0 else [])
                cur += ["Output:"] + ["    " + l for l in outs]
    if cur or not doc.sections:
        doc.add(key, cur)
    return doc


def convert_csv(path):
    delim = "\t" if str(path).lower().endswith(".tsv") else ","
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            delim = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except Exception:
            pass
        rows = list(csv.reader(f, delimiter=delim))
    doc = Doc("CSV", f"{len(rows)} rows")
    lines = ["| " + " | ".join(c.replace("|", "/") for c in r) + " |" for r in rows[:MAX_CSV_ROWS]]
    if len(rows) > MAX_CSV_ROWS:
        lines.append(f"… {len(rows) - MAX_CSV_ROWS} more rows; open the file or load it with pandas.")
    doc.add("Data", lines)
    return doc


def convert_legacy(path):
    ext = Path(path).suffix.lower()
    if ext in (".doc", ".rtf", ".odt") and shutil.which("textutil"):
        txt = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)],
                             capture_output=True, text=True).stdout
        doc = Doc("Word (legacy)")
        doc.add("Text", clean_lines(txt))
        return doc
    office = shutil.which("soffice") or shutil.which("libreoffice")
    if office:
        target = "pdf" if ext in (".ppt", ".odp", ".key", ".pages", ".doc", ".rtf", ".odt") else "xlsx"
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([office, "--headless", "--convert-to", target, "--outdir", td, str(path)],
                           capture_output=True, timeout=300)
            outs = list(Path(td).glob(f"*.{target}"))
            if outs:
                doc = convert_pdf(outs[0]) if target == "pdf" else convert_xlsx(outs[0])
                doc.kind += f" (from {ext})"
                return doc
    raise RuntimeError(f"cannot read {ext} here: export it as PDF/PPTX/DOCX/XLSX, or install LibreOffice")


def convert_image(path):
    doc = Doc("Image")
    doc.add("Image", ["_(image file: view it directly; after viewing, add a short '> ' note here so later questions can use the text)_"],
            "visual: image file", 1)
    return doc


def convert(path, ext):
    if ext in PDF_EXT:
        return convert_pdf(path)
    if ext == ".pptx":
        return convert_pptx(path)
    if ext == ".docx":
        return convert_docx(path)
    if ext in (".xlsx", ".xlsm"):
        return convert_xlsx(path)
    if ext == ".ipynb":
        return convert_ipynb(path)
    if ext in (".csv", ".tsv"):
        return convert_csv(path)
    if ext in IMAGE_EXT:
        return convert_image(path)
    if ext in LEGACY_EXT:
        return convert_legacy(path)
    raise RuntimeError(f"unsupported type {ext}")


# --------------------------------------------------------------------------- status / sync

def compute_status(root, man):
    conv, other = scan(root)
    files = man.get("files", {})
    new, changed, unchanged, failed = [], [], [], []
    for rel in conv:
        st = (root / rel).stat()
        e = files.get(rel)
        same = e and e.get("size") == st.st_size and abs(e.get("mtime", 0) - st.st_mtime) < 1
        if not e:
            new.append(rel)
        elif same and e.get("error"):
            failed.append(rel)          # retried only when the file changes
        elif same and (root / e.get("out", "")).exists():
            unchanged.append(rel)
        else:
            changed.append(rel)
    removed = [r for r in files if r not in conv]
    unindexed = [r for r in conv if r in files and not files[r].get("indexed")
                 and r not in changed and r not in failed]
    managed = {e.get("out") for e in files.values()}
    legacy = []
    tdir = root / TEXT_DIR
    if tdir.exists():
        for p in tdir.rglob("*.md"):
            relp = p.relative_to(root).as_posix()
            if relp.startswith(f"{TEXT_DIR}/_") or p.name in ("INDEX.md", "SYLLABUS.md") or relp in managed:
                continue
            legacy.append(relp)
    return {"new": new, "changed": changed, "removed": removed, "unchanged": unchanged, "failed": failed,
            "unindexed": unindexed, "other": other, "legacy": sorted(legacy)}


def write_doc(root, rel, ext):
    src = root / rel
    out = root / out_path_for(rel)
    notes = read_notes(out)
    doc = convert(src, ext)
    md = render_md(doc, rel, notes)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    st = src.stat()
    pages = len(doc.sections)
    return {
        "out": out_path_for(rel), "kind": doc.kind, "size": st.st_size, "mtime": st.st_mtime,
        "sha1": sha1(src), "sections": pages, "visual": doc.visual,
        "text_tokens": len(md) // 4,
        "pdf_tokens": pages * PDF_TOKENS_PER_PAGE if ext in PDF_EXT else None,
        "converted": _dt.datetime.now().isoformat(timespec="seconds"), "indexed": False,
        "notes_kept": sum(len(v) for v in notes.values()),
    }


def do_sync(root, quiet=False):
    man = load_manifest(root)
    files = man.setdefault("files", {})
    s = compute_status(root, man)
    conv, _ = scan(root)
    report = {"new": [], "changed": [], "removed": [], "renamed": [], "failed": [], "touched_same": []}

    # renames / moves: same content under a new path keeps text, notes and index status
    gone = {files[r].get("sha1"): r for r in s["removed"] if files[r].get("sha1")}
    for rel in list(s["new"]):
        if not gone:
            break
        h = sha1(root / rel)
        if h in gone:
            old = gone.pop(h)
            e = files.pop(old)
            old_out, new_out = root / e["out"], root / out_path_for(rel)
            if old_out.exists():
                new_out.parent.mkdir(parents=True, exist_ok=True)
                txt = old_out.read_text(encoding="utf-8").replace(f"`{old}`", f"`{rel}`", 1)
                new_out.write_text(txt, encoding="utf-8")
                old_out.unlink()
            st = (root / rel).stat()
            e.update(out=out_path_for(rel), size=st.st_size, mtime=st.st_mtime, indexed=False)
            files[rel] = e
            s["new"].remove(rel)
            s["removed"].remove(old)
            report["renamed"].append([old, rel])

    for rel in s["new"] + s["changed"]:
        is_new = rel in s["new"]
        old = files.get(rel)
        if old and old.get("sha1") and not old.get("error") and (root / old.get("out", "")).exists():
            if sha1(root / rel) == old["sha1"]:      # re-downloaded, same content
                old["mtime"] = (root / rel).stat().st_mtime
                report["touched_same"].append(rel)
                continue
        try:
            entry = write_doc(root, rel, conv[rel])
            if old and old.get("indexed"):
                entry["was_indexed"] = True
            files[rel] = entry
            report["new" if is_new else "changed"].append(rel)
        except Exception as ex:
            st = (root / rel).stat()
            files[rel] = {"out": out_path_for(rel), "size": st.st_size, "mtime": st.st_mtime,
                          "error": str(ex)[:300], "indexed": False}
            report["failed"].append([rel, str(ex)[:300]])

    for rel in s["removed"]:
        e = files.pop(rel)
        p = root / e.get("out", "")
        if e.get("out", "").startswith(TEXT_DIR + "/") and p.exists():
            p.unlink()
        report["removed"].append(rel)

    # tidy empty folders inside _text
    tdir = root / TEXT_DIR
    for d in sorted((p for p in tdir.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
        if d.name != "_tools" and not any(d.iterdir()):
            d.rmdir()

    save_manifest(root, man)
    s2 = compute_status(root, man)
    report["unindexed"] = s2["unindexed"]
    report["legacy"] = s2["legacy"]
    report["other"] = s2["other"]
    report["visual"] = {r: ranges(files[r].get("visual", [])) for r in report["new"] + report["changed"]
                        if files.get(r, {}).get("visual")}
    return report


def mark_indexed(root, paths, all_):
    man = load_manifest(root)
    files = man.get("files", {})
    done = []
    for rel, e in files.items():
        if all_ or rel in paths:
            if not e.get("error"):
                e["indexed"] = True
                e.pop("was_indexed", None)
                done.append(rel)
    save_manifest(root, man)
    missing = [p for p in paths if p not in files]
    return done, missing


# --------------------------------------------------------------------------- render

SWIFT_RENDER = r'''
import AppKit
import PDFKit
let a = CommandLine.arguments
guard let doc = PDFDocument(url: URL(fileURLWithPath: a[1])), let n = Int(a[2]), let page = doc.page(at: n - 1) else { exit(1) }
let box = page.bounds(for: .mediaBox)
let w = Double(a[4]) ?? 1600
let s = w / box.width
let size = NSSize(width: box.width * s, height: box.height * s)
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(size.width), pixelsHigh: Int(size.height), bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
let ctx = NSGraphicsContext(bitmapImageRep: rep)!
NSGraphicsContext.current = ctx
ctx.cgContext.setFillColor(NSColor.white.cgColor)
ctx.cgContext.fill(CGRect(origin: .zero, size: size))
ctx.cgContext.scaleBy(x: s, y: s)
page.draw(with: .mediaBox, to: ctx.cgContext)
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[3]))
'''


def parse_pages(spec):
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def render_pdf_page(pdf, n, out, width):
    fitz = mupdf()
    if fitz:
        with fitz.open(pdf) as d:
            p = d[n - 1]
            z = width / p.rect.width
            p.get_pixmap(matrix=fitz.Matrix(z, z)).save(str(out))
            return True
    if shutil.which("pdftoppm"):
        base = str(out)[:-4]
        r = subprocess.run(["pdftoppm", "-f", str(n), "-l", str(n), "-png", "-singlefile",
                            "-scale-to-x", str(width), "-scale-to-y", "-1", str(pdf), base], capture_output=True)
        if r.returncode == 0:
            return True
    if sys.platform == "darwin" and shutil.which("swift"):
        with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as f:
            f.write(SWIFT_RENDER)
        r = subprocess.run(["swift", f.name, str(pdf), str(n), str(out), str(width)], capture_output=True, timeout=180)
        os.unlink(f.name)
        if r.returncode == 0 and Path(out).exists():
            return True
    return False


def do_render(root, src, spec, outdir, width):
    srcp = Path(src)
    if not srcp.is_absolute():
        srcp = (root / src) if (root / src).exists() else Path.cwd() / src
    if not srcp.exists():
        raise SystemExit(f"not found: {src}")
    outdir = Path(outdir) if outdir else Path(tempfile.gettempdir()) / "course-renders"
    outdir.mkdir(parents=True, exist_ok=True)
    ext = srcp.suffix.lower()
    if ext in IMAGE_EXT:
        print(f"image file, view it directly: {srcp}")
        return
    pdf = srcp
    if ext != ".pdf":
        office = shutil.which("soffice") or shutil.which("libreoffice")
        cache = Path(tempfile.gettempdir()) / "course-renders" / f"{sha1(srcp)[:12]}.pdf"
        if office and not cache.exists():
            with tempfile.TemporaryDirectory() as td:
                subprocess.run([office, "--headless", "--convert-to", "pdf", "--outdir", td, str(srcp)],
                               capture_output=True, timeout=300)
                got = list(Path(td).glob("*.pdf"))
                if got:
                    shutil.move(str(got[0]), cache)
        if cache.exists():
            pdf = cache
        elif ext == ".pptx":
            # no renderer for slides: hand out the slide's own pictures instead
            z = zipfile.ZipFile(srcp)
            prels = read_rels(z, "ppt/presentation.xml")
            pres = ET.fromstring(z.read("ppt/presentation.xml"))
            order = [prels[s.get(R_NS + "id")][0] for s in pres.iter() if local(s.tag) == "sldId"]
            for n in parse_pages(spec):
                for rid, (tgt, typ) in read_rels(z, order[n - 1]).items():
                    if typ.endswith("/image"):
                        o = outdir / f"{srcp.stem}-s{n}-{Path(tgt).name}"
                        o.write_bytes(z.read(tgt))
                        print(o)
            print("(no slide renderer: these are the slide's pictures; export the deck as PDF for full slide images)")
            return
        else:
            raise SystemExit("cannot render this type: export it as PDF or install LibreOffice")
    safe = re.sub(r"[^\w.-]+", "_", srcp.stem)[:60]
    failed = []
    for n in parse_pages(spec):
        out = outdir / f"{safe}-p{n}.png"
        if render_pdf_page(pdf, n, out, width):
            print(out)
        else:
            failed.append(n)
    if failed:
        print(f"could not render page(s) {ranges(failed)}: install PyMuPDF (pip install pymupdf) or poppler, "
              f"or open the PDF with the Read tool and its pages option", file=sys.stderr)
        sys.exit(2)


# --------------------------------------------------------------------------- CLI

def fmt_list(title, items, limit=40):
    if not items:
        return []
    lines = [f"{title} ({len(items)}):"]
    for it in items[:limit]:
        lines.append("  - " + (" → ".join(it) if isinstance(it, (list, tuple)) else it))
    if len(items) > limit:
        lines.append(f"  … {len(items) - limit} more")
    return lines


def cmd_install(root):
    dst = root / TEXT_DIR / "_tools" / "course_sync.py"
    src = Path(__file__).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src != dst.resolve():
        if dst.exists():
            m = re.search(r'VERSION = "([\d.]+)"', dst.read_text(encoding="utf-8", errors="replace"))
            have = tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
            if have > tuple(int(x) for x in VERSION.split(".")):
                print(f"kept newer course copy {m.group(1)} at {dst}")
                return
        shutil.copy2(src, dst)
    ign = root / TEXT_DIR / IGNORE_FILE
    if not ign.exists():
        ign.write_text("# Paths (glob patterns, relative to the course folder) that course_sync should skip.\n"
                       "# Example:\n# Old semester/*\n", encoding="utf-8")
    print(f"installed course_sync {VERSION} at {dst}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="course folder (default: auto)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("install")
    p = sub.add_parser("status")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("sync")
    p.add_argument("--json", action="store_true")
    p.add_argument("--hook", action="store_true", help="quiet unless something needs Claude's attention")
    p.add_argument("--clean-legacy", action="store_true", help="delete old unmanaged .md files in _text/")
    p = sub.add_parser("render")
    p.add_argument("file")
    p.add_argument("pages")
    p.add_argument("--out", help="output folder (default: system temp/course-renders)")
    p.add_argument("--width", type=int, default=1600)
    p = sub.add_parser("mark-indexed")
    p.add_argument("paths", nargs="*")
    p.add_argument("--all", action="store_true")
    sub.add_parser("stats")
    sub.add_parser("doctor")
    a = ap.parse_args()
    root = default_root(a.root)

    if a.cmd == "install":
        cmd_install(root)
    elif a.cmd == "doctor":
        b = pdf_backend()
        if mupdf():
            rend = "pymupdf"
        else:
            rend = "pdftoppm" if shutil.which("pdftoppm") else ("macOS swift/PDFKit" if sys.platform == "darwin" and shutil.which("swift") else None)
        print(f"course_sync {VERSION} · python {sys.version.split()[0]} · root {root}")
        print(f"PDF text:    {b or 'MISSING (pip install pymupdf)'}")
        print(f"PDF render:  {rend or 'MISSING (pip install pymupdf)'}")
        print(f"Legacy docs: {'textutil ' if shutil.which('textutil') else ''}{'libreoffice' if (shutil.which('soffice') or shutil.which('libreoffice')) else ''}".rstrip() or "Legacy docs: none (export .ppt/.doc as PDF)")
    elif a.cmd == "status":
        s = compute_status(root, load_manifest(root))
        if a.json:
            s["unchanged"] = len(s["unchanged"])
            print(json.dumps(s, ensure_ascii=False, indent=1))
            return
        out = [f"Course folder: {root}"]
        out += fmt_list("New", s["new"]) + fmt_list("Changed", s["changed"]) + fmt_list("Removed", s["removed"])
        out += fmt_list("Converted but not yet in INDEX.md", s["unindexed"])
        out += fmt_list("Could not be converted (open the original)",
                        [f"{r}: {load_manifest(root)['files'][r].get('error')}" for r in s["failed"]])
        out += fmt_list("Old unmanaged text copies in _text/ (sync --clean-legacy removes them)", s["legacy"], 10)
        other = s["other"]
        for kind, label in (("text", "Plain-text/code files (read directly)"), ("media", "Video/audio (not convertible)"),
                            ("archive", "Archives (unzip to include)"), ("other", "Other files (skipped)")):
            out += fmt_list(label, [r for r, k in other.items() if k == kind], 15)
        out.append(f"Up to date: {len(s['unchanged'])} file(s).")
        print("\n".join(out))
    elif a.cmd == "sync":
        if a.clean_legacy:
            for relp in compute_status(root, load_manifest(root))["legacy"]:
                (root / relp).unlink()
        r = do_sync(root)
        if a.json:
            r["other"] = {k: v for k, v in r["other"].items()}
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return
        lines = []
        lines += fmt_list("Converted new", r["new"]) + fmt_list("Re-converted changed", r["changed"])
        lines += fmt_list("Renamed/moved (text kept)", r["renamed"]) + fmt_list("Removed (text copy deleted)", r["removed"])
        lines += fmt_list("FAILED", [f"{x[0]}: {x[1]}" for x in r["failed"]])
        if r["visual"]:
            lines.append("Visual pages in converted files:")
            lines += [f"  - {k}: {v}" for k, v in r["visual"].items()]
        if r["unindexed"]:
            lines += fmt_list("Not yet in INDEX.md (add entries, then run mark-indexed)", r["unindexed"])
        if r["legacy"]:
            lines.append(f"{len(r['legacy'])} old unmanaged .md file(s) in _text/; run sync --clean-legacy to remove them.")
        if a.hook:
            if lines:
                print("[course-index] Course files changed since the last session.\n" + "\n".join(lines) +
                      "\nUpdate _text/INDEX.md (and the schedule in CLAUDE.md if needed) for these files, "
                      "then run: python3 _text/_tools/course_sync.py mark-indexed <paths>")
            return
        print("\n".join(lines) if lines else "Everything is up to date.")
    elif a.cmd == "render":
        do_render(root, a.file, a.pages, a.out, a.width)
    elif a.cmd == "mark-indexed":
        done, missing = mark_indexed(root, a.paths, a.all)
        print(f"marked {len(done)} file(s) as indexed")
        if missing:
            print("not in manifest: " + ", ".join(missing))
    elif a.cmd == "stats":
        files = load_manifest(root).get("files", {})
        txt = sum(e.get("text_tokens") or 0 for e in files.values())
        pdf_pages = sum(e.get("sections") or 0 for e in files.values() if e.get("pdf_tokens"))
        pdf_direct = sum(e.get("pdf_tokens") or 0 for e in files.values())
        pdf_text = sum(e.get("text_tokens") or 0 for e in files.values() if e.get("pdf_tokens"))
        vis = sum(len(e.get("visual") or []) for e in files.values())
        print(f"{len(files)} file(s) converted, {vis} visual page(s)/slide(s) flagged")
        print(f"All text copies together: ≈{txt:,} tokens")
        if pdf_pages:
            print(f"PDFs: {pdf_pages} pages ≈{pdf_direct:,} tokens if read as PDF (rough, {PDF_TOKENS_PER_PAGE}/page) "
                  f"vs ≈{pdf_text:,} as text ({pdf_text / max(pdf_direct, 1):.0%})")
        print("A typical question reads INDEX.md plus a few pages, not whole files.")


if __name__ == "__main__":
    main()
