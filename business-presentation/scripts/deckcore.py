"""Checker for business-presentation deck plans (deck.json).

Tests action titles, slop rules, length limits and sources, and estimates whether
each slide fits the grid in references/design.md. It does not build slides.
"""
import json
import re
import sys

# ---------------------------------------------------------------- slide grid (references/design.md)
W = 1920
PAD_X = 128
CONTENT_W = W - 2 * PAD_X            # 1664
BODY_TOP = 340                        # exhibit starts here
BODY_BOTTOM = 900                     # content ends here; bottom rule at 932, footer below
GAP = 32
FS = {"note": 24, "body": 28}         # footnote/source and box text sizes in px

NEUTRAL_ACCENT = "#2B59C3"
BG = "#FDFDFC"
CHAR_W = 0.55  # average glyph width as a share of font size (bold ~0.58)

CHART_TYPES = {"bar", "column", "stacked_bar", "stacked_column", "line", "waterfall"}
LIBRARY = {"competitor-benchmark", "positioning-matrix", "market-sizing", "market-growth", "company-profile", "swot",
           "five-forces", "pestel", "value-chain", "issue-tree", "scoring-model", "pros-cons", "risk-matrix", "scr",
           "interview-findings"}   # templates in assets/exhibits/
SLIDE_TYPES = {"title", "summary", "agenda", "section", "chart", "kpis", "table", "library",
               "columns", "quotes", "steps", "sources", "closing"}
LABEL_TYPES = {"title", "agenda", "section", "sources", "closing"}   # no action title needed
TEXT_EXHIBITS = {"kpis", "table", "columns", "quotes", "steps", "library"}       # must not repeat back to back
THEMES = {"clean", "neutral", "midnight", "classic", "company"}
DATA_TYPES = {"chart", "kpis", "table"}                    # must cite a source

MARKER = re.compile(r"\[(TEAM|DATA MISSING):\s*([^\]]*)\]")


# ---------------------------------------------------------------- helpers
def lines_needed(text, width, size, bold=False):
    if not text:
        return 0
    per_line = max(1, int(width / (size * (0.58 if bold else CHAR_W))))
    total = 0
    for para in str(text).split("\n"):
        words, line, n = para.split(), 0, 1
        for w_ in words:
            add = len(w_) + (1 if line else 0)
            if line + add > per_line and line:
                n += 1
                line = len(w_)
            else:
                line += add
        total += n
    return total


def luminance(h):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def source_line(slide, deck):
    srcs = {s["id"]: s for s in deck.get("sources", [])}
    parts = []
    for ref in slide.get("sources", []) or []:
        if ref in srcs:
            s = srcs[ref]
            parts.append(", ".join(x for x in [s.get("org"), s.get("doc"), s.get("date")] if x))
        else:
            parts.append(str(ref))
    return ("Source: " + "; ".join(parts)) if parts else ""


# ---------------------------------------------------------------- vertical budget
def body_layout(slide, deck, width=CONTENT_W):
    """Height left for the exhibit after footnotes and boxes. The source sits in the footer, below the bottom rule."""
    notes = [f"{i + 1}. {n}" for i, n in enumerate(slide.get("footnotes") or [])]
    notes_h = sum(lines_needed(n, width, FS["note"]) for n in notes) * 32
    bottom_h = 0
    texts = [t for t in (slide.get("callout"), slide.get("team_input")) if t]
    if texts:
        box_w = width if len(texts) == 1 else (width - GAP) / 2
        ln = max(lines_needed(t, box_w - 64, FS["body"]) for t in texts)
        bottom_h = 40 + 34 + ln * 38  # padding + label + lines
    main_bottom = BODY_BOTTOM - notes_h - (16 if notes_h else 0) - (bottom_h + 24 if bottom_h else 0)
    return {"main_h": main_bottom - BODY_TOP}


# ---------------------------------------------------------------- loading
def load(path):
    with open(path, encoding="utf-8") as f:
        deck = json.load(f)
    used = set()
    for i, s in enumerate(deck.get("slides", [])):
        sid = s.get("id") or (s.get("type", "slide") + f"-{i + 1:02d}")
        sid = re.sub(r"[^A-Za-z0-9_-]", "-", sid)[:64]
        while sid in used:
            sid += "x"
        used.add(sid)
        s["id"] = sid
    return deck


# ---------------------------------------------------------------- checking
WEAK_START = re.compile(
    r"^(overview|introduction|background|agenda|analysis|results|key (findings|insights|takeaways)|"
    r"findings|market (overview|analysis)|company (overview|profile)|recommendations?|next steps|"
    r"methodology|method|conclusions?|summary|executive summary|context|situation|"
    r"the (chart|graph|table|figure|slide)|this (chart|graph|table|slide)|figure\b|overview of|analysis of)\b",
    re.I)
VAGUE = [
    (r"\bplays? an? (important|key|major|crucial|significant) role\b", "empty phrase 'plays a key role'"),
    (r"\bis (very )?important\b", "empty phrase 'is important'"),
    (r"\bvar(y|ies|ied)\b", "'varies' says nothing; state how"),
    (r"\bvarious\b", "'various' is vague"),
    (r"\bcould potentially\b|\bmight possibly\b", "double hedge"),
    (r"\bthe following\b", "'the following' points at the slide instead of stating the message"),
    (r"\b(shows?|depicts?|illustrates?|displays?) (the|an?|how)\b", "narrates the exhibit"),
]

# Slop rules (references/writing-style.md), applied to every text on a slide.
SLOP_ERRORS = [
    (r"—", "em dash; use a full stop, comma or 'and'/'but'"),
    (r"\s–\s", "spaced en dash used as an em dash; en dashes only in ranges like 2020–2024"),
    (r"!", "exclamation mark"),
]
SLOP_WARNS = [
    (r"\b(it'?s|it is|this is|that'?s|that is)\s+not\b[^.]{0,60}?,\s*(it'?s|it is|but)\b", "'it's not X, it's Y' construction"),
    (r"\bnot (just|only|merely)\b", "'not just/only X, but Y' construction"),
    (r"\bisn'?t the (problem|issue|point)\b", "'X isn't the problem' construction"),
    (r"\b(less \w+, more \w+)\b", "'less X, more Y' slogan"),
    (r"\b(revolutionar\w*|game.?chang\w*|groundbreaking|cutting.?edge|state.of.the.art|world.class|best.in.class|"
     r"unparalleled|unprecedented|seamless\w*|powerful|innovative|transformative|next.level|exciting|amazing|"
     r"incredible|remarkable|stunning)\b", "advertising word"),
    (r"\b(leverag\w*|synerg\w*|unlock\w*|empower\w*|elevat\w*|supercharg\w*|harness\w*|foster\w*|holistic|robust|"
     r"ever.evolving|paradigm|going forward|at the end of the day|value at stake|journey|landscape|realm|delv\w*|"
     r"pivotal|crucial|vital|fast.paced)\b", "buzzword"),
    (r"\b(here'?s why|let'?s dive|dive in|one thing is clear)\b|\b(the bottom line\?|the result:|the verdict:)", "speaker phrase"),
]
COLON_SENTENCE = re.compile(r"[A-Za-z)]:\s+[A-Za-z]")
COLON_FIELDS = ("title", "header", "callout", "takeaways", "points", "kpis", "columns", "steps")
CAUSAL = re.compile(r"\b(drives?|drove|driven|causes?|caused|leads? to|led to|results? in|because of|due to)\b", re.I)
NUM = re.compile(r"(?<![A-Za-z\d.,])[-−+]?\d[\d,]*(?:\.\d+)?")


def _numbers(text):
    out = []
    for m in NUM.finditer(text or ""):
        raw = m.group(0).replace(",", "").replace("−", "-").lstrip("+")
        try:
            out.append(float(raw))
        except ValueError:
            pass
    return out


def _slide_strings(slide):
    acc = []

    def walk(x):
        if isinstance(x, str):
            acc.append(x)
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            acc.append(repr(x))
        elif isinstance(x, list):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            for k, y in x.items():
                if k not in ("title", "id", "type"):
                    walk(y)
    walk(slide)
    return acc


def _slide_values(slide):
    vals = []
    for t in _slide_strings(slide):
        vals += _numbers(t)
    c = slide.get("chart")
    if c:
        for s in c.get("series", []):
            vals += [abs(v) for v in s.get("values", []) if isinstance(v, (int, float))]
    return vals


def check(deck):
    errors, warns = [], []
    E = lambda n, msg: errors.append(f"slide {n}: {msg}")
    Wn = lambda n, msg: warns.append(f"slide {n}: {msg}")

    theme = deck.get("theme") or {}
    for k in ("accent", "accent2"):
        if theme.get(k) and not re.fullmatch(r"#[0-9A-Fa-f]{6}", theme[k]):
            errors.append(f"theme.{k} must be a 6-digit hex colour like #2B59C3")
    name = (theme.get("name") or "clean").lower()
    if name not in THEMES:
        errors.append(f"theme.name '{name}' is unknown; use clean, midnight, classic or company")
    if name == "company" and not theme.get("accent"):
        errors.append("the company theme needs theme.accent (the brand colour as hex)")
    if name == "company" and not (deck.get("meta") or {}).get("logo"):
        warns.append("company theme without meta.logo; add the logo file or set it to 'placeholder'")
    accent = theme.get("accent") or NEUTRAL_ACCENT
    if not errors and contrast(accent, BG) < 3:
        warns.append("theme.accent is too light for text and thin lines on white (contrast < 3:1); darken it")

    src_ids = {s.get("id") for s in deck.get("sources", [])}
    for s in deck.get("sources", []):
        if not s.get("id") or not (s.get("org") or s.get("doc")):
            errors.append(f"source {s}: needs id and org or doc")

    slides = deck.get("slides", [])
    if not slides:
        errors.append("deck has no slides")
    content = [s for s in slides if s.get("type") not in LABEL_TYPES]
    if not any(s.get("type") == "summary" for s in slides) and len(content) > 5:
        warns.append("deck has no summary slide; decks over 5 content slides should open with one")

    for n, s in enumerate(slides, 1):
        typ = s.get("type")
        if typ not in SLIDE_TYPES:
            E(n, f"unknown type '{typ}'. Use one of {sorted(SLIDE_TYPES)}")
            continue
        title = (s.get("title") or "").strip()

        # ---- action title
        if typ not in LABEL_TYPES:
            if not title:
                E(n, "missing action title")
            else:
                words = len(title.split())
                # a logo in the header band narrows the title from 1664 to 1404 px
                hard, soft = (105, 85) if (deck.get("meta") or {}).get("logo") else (120, 95)
                if len(title) > hard:
                    E(n, f"title is {len(title)} characters; the limit is {hard} (two lines"
                         f"{' next to the logo' if hard == 105 else ''})")
                elif len(title) > soft:
                    Wn(n, f"title is {len(title)} characters; aim for under {soft}")
                if words < 6:
                    E(n, f"title '{title}' has {words} words; it reads like a label, not a sentence")
                if title.endswith("?"):
                    E(n, "title is a question; put the question in 'tracker' and answer it in the title")
                if WEAK_START.match(title):
                    E(n, f"title starts like a label or narrates the slide: '{title[:40]}'")
                for pat, why in VAGUE:
                    if re.search(pat, title, re.I):
                        Wn(n, f"title: {why}")
                if title.count(" and ") >= 2 or title.count(";"):
                    Wn(n, "title may carry more than one message; keep one claim (a single 'but' is fine)")
                if CAUSAL.search(title):
                    Wn(n, "title claims a cause; check that the material shows causality, not just a correlation")
                # numbers in the title must be on the slide
                vals = _slide_values(s)
                if typ == "summary":  # the summary condenses the whole deck
                    vals = [x for o in slides for x in _slide_values(o)] + _numbers(
                        " ".join(o.get("title", "") for o in slides if o is not s))
                for v in _numbers(title):
                    if 1900 <= v <= 2100 and any(abs(v - x) < 0.01 for x in vals):
                        continue
                    if not any(abs(abs(v) - x) <= max(0.051, abs(v) * 0.005) for x in vals):
                        Wn(n, f"number {v:g} in the title is not shown on the slide; show it or footnote how it is derived")
        elif typ == "section" and not title:
            E(n, "section slide needs a title")

        # ---- slop rules on every text of the slide
        texts = [title] + _slide_strings(s)
        clean = [MARKER.sub("", x) for x in texts]
        seen = set()
        for x in clean:
            for pat, why in SLOP_ERRORS:
                if re.search(pat, x) and why not in seen:
                    seen.add(why)
                    E(n, f"{why}: '{x[:50]}'")
            for pat, why in SLOP_WARNS:
                if re.search(pat, x, re.I) and why not in seen:
                    seen.add(why)
                    Wn(n, f"{why}: '{x[:50]}'")
        colon_texts = [title]
        for key in COLON_FIELDS[1:]:
            v = s.get(key)
            colon_texts += [y for y in _slide_strings({key: v})] if v else []
        for x in colon_texts:
            if COLON_SENTENCE.search(MARKER.sub("", x or "")):
                Wn(n, f"colon construction; write one plain sentence: '{x[:50]}'")
                break

        # ---- common text limits
        for key, lim in (("tracker", 40), ("header", 110), ("callout", 180), ("team_input", 200)):
            if s.get(key) and len(s[key]) > lim:
                E(n, f"{key} is {len(s[key])} characters; limit {lim}")
        src = source_line(s, deck)
        if src and len(src) > 200:
            E(n, f"source line is {len(src)} characters; the footer holds two lines (about 200 characters). Shorten the source names")
        elif src and len(src) > 110:
            Wn(n, f"source line is {len(src)} characters and takes two lines in the footer; one line (110) looks cleaner")
        if len(s.get("footnotes") or []) > 3:
            E(n, "more than 3 footnotes; move detail to the appendix")
        for f in s.get("footnotes") or []:
            if len(f) > 180:
                E(n, "a footnote is over 180 characters")
        for ref in s.get("sources") or []:
            if ref not in src_ids and re.fullmatch(r"S\d+", str(ref)):
                E(n, f"source '{ref}' is not in the deck's sources list")
        if typ in DATA_TYPES and not s.get("sources"):
            E(n, "data slide without a source; add 'sources' (use e.g. 'Team survey (n=48)' for own data)")
        if typ in ("chart", "table") and not s.get("header"):
            Wn(n, "no exhibit header; say what is shown, the unit and the period, e.g. 'Revenue by segment, 2020–24, €M'")

        # ---- type specific
        if typ == "summary":
            pts = s.get("points") or []
            if not 3 <= len(pts) <= 6:
                E(n, "summary needs 3 to 6 points")
            for p in pts:
                if len(p) > 170:
                    E(n, "a summary point is over 170 characters")
        elif typ == "agenda":
            if not 2 <= len(s.get("items") or []) <= 7:
                E(n, "agenda needs 2 to 7 items")
        elif typ == "chart":
            c = s.get("chart") or {}
            ct = c.get("type")
            if ct not in CHART_TYPES:
                E(n, f"chart.type must be one of {sorted(CHART_TYPES)}")
                continue
            cats, series = c.get("categories") or [], c.get("series") or []
            if not cats or not series:
                E(n, "chart needs categories and series")
                continue
            for sr in series:
                if len(sr.get("values") or []) != len(cats):
                    E(n, f"series '{sr.get('name')}' has {len(sr.get('values') or [])} values for {len(cats)} categories")
            maxcat = 12 if ct in ("line", "column", "stacked_column", "waterfall") else 10
            if len(cats) > maxcat:
                E(n, f"{len(cats)} categories; a {ct} chart holds at most {maxcat}")
            if len(series) > (5 if ct == "line" else 4):
                E(n, "too many series; split the chart or group the rest as 'Other'")
            if ct == "waterfall" and len(series) != 1:
                E(n, "a waterfall takes exactly one series")
            if ct in ("bar", "column", "stacked_bar", "stacked_column") and any(
                    (v or 0) < 0 for sr in series for v in sr.get("values") or []):
                E(n, "negative values are not supported in bar or column charts; use a waterfall or a table")
            if ct in ("stacked_bar", "stacked_column") and len(series) < 2:
                E(n, "a stacked chart needs at least 2 series")
            for cat in cats:
                if len(str(cat)) > 32:
                    E(n, f"category label '{cat}' is over 32 characters")
            if c.get("type") in ("bar", "column") and len(series) == 1 and not c.get("highlight"):
                Wn(n, "single-series chart without 'highlight'; highlight the bar(s) the title talks about")
            tk = s.get("takeaways") or []
            kn = s.get("key_number")
            if kn:
                if len(str(kn.get("value", ""))) > 8:
                    E(n, f"key_number value '{kn.get('value')}' is over 8 characters")
                if not kn.get("label") or len(kn["label"]) > 60:
                    E(n, "key_number needs a label of at most 60 characters")
            if len(tk) > (2 if kn else 3):
                E(n, f"at most {2 if kn else 3} takeaways{' next to a key number' if kn else ''}")
            for x in tk:
                if len(x) > 110:
                    E(n, "a takeaway is over 110 characters")
        elif typ == "kpis":
            k = s.get("kpis") or []
            if not 1 <= len(k) <= 4:
                E(n, "kpis needs 1 number (hero) or 2 to 4 numbers (number row)")
            for x in k:
                if len(str(x.get("value", ""))) > 8:
                    E(n, f"kpi value '{x.get('value')}' is over 8 characters")
                if len(x.get("label", "")) > 40:
                    E(n, "a kpi label is over 40 characters")
                if not x.get("context"):
                    Wn(n, f"kpi '{x.get('value')}' has no context (compared to what, which period?)")
                elif len(x["context"]) > 110:
                    E(n, "a kpi context is over 110 characters")
        elif typ == "table":
            tb = s.get("table") or {}
            cols, rows = tb.get("columns") or [], tb.get("rows") or []
            if not cols or not rows:
                E(n, "table needs columns and rows")
                continue
            if len(cols) > 6:
                E(n, "a table holds at most 6 columns")
            if len(rows) > 8:
                E(n, "a table holds at most 8 rows; split it or move detail to the appendix")
            for r in rows:
                if len(r) != len(cols):
                    E(n, f"row {r[:1]} has {len(r)} cells for {len(cols)} columns")
                for cell in r:
                    if len(str(cell)) > 70:
                        E(n, f"table cell '{str(cell)[:30]}…' is over 70 characters")
        elif typ == "columns":
            cl = s.get("columns") or []
            if not 1 <= len(cl) <= 4:
                E(n, "columns needs 1 to 4 columns")
            for x in cl:
                body = x.get("body") or ""
                bl = x.get("bullets") or []
                if len(bl) > 5:
                    E(n, "a column holds at most 5 bullets")
                size = len(body) + sum(len(b) for b in bl)
                limit = {1: 600, 2: 420, 3: 300, 4: 220}.get(len(cl), 220)
                if size > limit:
                    E(n, f"column '{x.get('heading', '')}' holds {size} characters; limit {limit} for {len(cl)} columns")
                if len(x.get("heading", "")) > 40:
                    E(n, "a column heading is over 40 characters")
        elif typ == "quotes":
            q = s.get("quotes") or []
            if not 1 <= len(q) <= 4:
                E(n, "quotes needs 1 to 4 quotes")
            lim = 240 if len(q) <= 2 else 160
            for x in q:
                if len(x.get("text", "")) > lim:
                    E(n, f"a quote is over {lim} characters")
            if not s.get("sources"):
                Wn(n, "quotes without a source; say who was interviewed and when")
        elif typ == "library":
            pat = s.get("pattern")
            if pat not in LIBRARY:
                E(n, f"library pattern '{pat}' is unknown; use one of {sorted(LIBRARY)}")
            if not s.get("content"):
                E(n, "library slide needs 'content' with the labels, numbers and points for the template")
            if not s.get("sources") and pat not in ("scr",):
                Wn(n, "library slide without sources; name the data or say 'team assessment based on S2'")
        elif typ == "steps":
            st = s.get("steps") or []
            if not 3 <= len(st) <= 5:
                E(n, "steps needs 3 to 5 steps")
            for x in st:
                if len(x.get("heading", "")) > 32:
                    E(n, "a step heading is over 32 characters")
                if len(x.get("body", "")) > 140:
                    E(n, "a step body is over 140 characters")

        # ---- vertical fit
        if typ not in LABEL_TYPES and typ != "summary":
            lay = body_layout(s, deck)
            if lay["main_h"] < 300:
                E(n, f"too much below the exhibit (notes, callout, team input) leaves only {int(lay['main_h'])}px for it; cut text")

    # ---- variety (references/exhibits.md)
    def layout_of(s):
        t = s.get("type")
        if t == "kpis":
            return "hero number" if len(s.get("kpis") or []) == 1 else "number row"
        if t == "library":
            return s.get("pattern") or "library"
        return t

    body = [(n, s) for n, s in enumerate(slides, 1) if s.get("type") not in LABEL_TYPES | {"summary"}]
    big = [n for n, s in body if s.get("type") == "kpis"]
    if len(big) > 1:
        errors.append(f"big numbers (kpis) appear on {len(big)} slides ({', '.join(map(str, big))}); use at most one "
                      "big-number slide per deck and show the other numbers in a chart, a table or a library exhibit")
    keys = [n for n, s in body if s.get("key_number")]
    if len(keys) > 1:
        errors.append(f"key_number is used on {len(keys)} slides ({', '.join(map(str, keys))}); use it at most once per deck")
    pats = {}
    for n, s in body:
        if s.get("type") == "library":
            pats.setdefault(s.get("pattern"), []).append(n)
    for pat, ns in pats.items():
        if len(ns) > 1:
            errors.append(f"library pattern '{pat}' is used on slides {', '.join(map(str, ns))}; use each pattern once")
    for (n1, a), (n2, b) in zip(body, body[1:]):
        if n2 == n1 + 1 and a.get("type") in TEXT_EXHIBITS and layout_of(a) == layout_of(b):
            errors.append(f"slides {n1} and {n2} both use '{layout_of(a)}'; never use the same text exhibit twice in a row")
    if len(body) >= 6:
        counts = {}
        for _, s in body:
            if s.get("type") != "chart":
                counts[layout_of(s)] = counts.get(layout_of(s), 0) + 1
        for lay_name, c in counts.items():
            if c > len(body) / 3:
                warns.append(f"'{lay_name}' is used on {c} of {len(body)} content slides; vary the exhibits")
    deck["_sequence"] = ", ".join(layout_of(s) for _, s in body)

    # ---- open items
    open_items = []
    for n, s in enumerate(slides, 1):
        for txt in _slide_strings(s) + [s.get("title") or ""]:
            for m in MARKER.finditer(txt):
                open_items.append(f"slide {n}: [{m.group(1)}] {m.group(2).strip()}")
        if s.get("team_input"):
            open_items.append(f"slide {n}: [TEAM BOX] {s['team_input']}")
    return errors, warns, sorted(set(open_items), key=lambda x: int(x.split()[1].rstrip(":")))


def storyline(deck):
    out = []
    for n, s in enumerate(deck.get("slides", []), 1):
        if s.get("type") in ("title", "agenda", "sources", "closing"):
            continue
        prefix = "  §" if s.get("type") == "section" else f"{n:>3}"
        out.append(f"{prefix}  {s.get('title', '')}")
    return out


# ---------------------------------------------------------------- deck plan document
EXHIBIT_NAMES = {"bar": "Bar chart", "column": "Column chart", "stacked_bar": "Stacked bar chart",
                 "stacked_column": "Stacked column chart", "line": "Line chart", "waterfall": "Waterfall"}


def _cell(x):
    return str(x).replace("|", "/").replace("\n", " ")


def _num(v, c, sign=False):
    if v is None:
        return ""
    d = c.get("decimals")
    if d is None:
        vals = [x for s in c.get("series", []) for x in s.get("values", []) if x is not None]
        d = 0 if all(float(x).is_integer() for x in vals) else 1
    pre = "−" if v < 0 else ("+" if sign and v > 0 else "")
    return f"{pre}{c.get('prefix', '')}{abs(v):,.{int(d)}f}{c.get('suffix', '')}"


def exhibit_name(s):
    t = s.get("type")
    if t == "chart":
        name = EXHIBIT_NAMES.get((s.get("chart") or {}).get("type"), "Chart")
        return name + (" + key number" if s.get("key_number") else "") + (" + takeaways" if s.get("takeaways") else "")
    if t == "library":
        return "Library: " + str(s.get("pattern", ""))
    if t == "kpis":
        return "Hero number" if len(s.get("kpis") or []) == 1 else "Number row"
    return {"table": "Table", "columns": "Columns", "quotes": "Quotes", "steps": "Steps", "summary": "Summary",
            "agenda": "Agenda", "section": "Section divider", "title": "Cover", "closing": "Closing",
            "sources": "Sources"}.get(t, t)


def plan_markdown(deck, open_items):
    """A readable deck plan: storyline, every slide's content with numbers and sources."""
    m = deck.get("meta") or {}
    srcs = {s["id"]: s for s in deck.get("sources", [])}
    theme = (deck.get("theme") or {}).get("name", "clean")
    out = [f"# Deck plan: {m.get('title', 'Untitled')}", ""]
    meta_bits = [f"Theme {theme.capitalize()}", m.get("team"), m.get("course"), m.get("date")]
    out += [" · ".join(b for b in meta_bits if b), ""]

    out += ["## Storyline", "", "Read the titles from top to bottom. Together they tell the whole story.", "",
            "| # | Action title | Exhibit | Sources |", "|---|---|---|---|"]
    for n, s in enumerate(deck["slides"], 1):
        if s.get("type") in ("title", "closing", "sources"):
            continue
        out.append(f"| {n} | {_cell(s.get('title', ''))} | {exhibit_name(s)} | {_cell(', '.join(map(str, s.get('sources') or [])))} |")
    out.append("")
    if open_items:
        out += ["## Open items for the team", ""] + [f"- {o}" for o in open_items] + [""]

    out += ["## Slide by slide", ""]
    for n, s in enumerate(deck["slides"], 1):
        t = s.get("type")
        if t in ("title", "closing", "sources"):
            continue
        out.append(f"### {n}. {s.get('title', '')}")
        out.append("")
        line = f"**{exhibit_name(s)}**"
        if s.get("tracker"):
            line = f"*{s['tracker']}* · " + line
        if s.get("header"):
            line += f" · {s['header']}"
        out += [line, ""]
        if t == "summary":
            out += [f"{i + 1}. {p}" for i, p in enumerate(s.get("points") or [])] + [""]
        elif t == "agenda":
            out += [f"{i + 1}. {p}" for i, p in enumerate(s.get("items") or [])] + [""]
        elif t == "chart":
            c = s.get("chart") or {}
            series = c.get("series") or []
            out.append("| | " + " | ".join(_cell(x.get("name", "")) for x in series) + " |")
            out.append("|---|" + "---|" * len(series))
            hl = set(c.get("highlight") or [])
            for i, cat in enumerate(c.get("categories") or []):
                vals = [_num((x.get("values") or [None] * (i + 1))[i], c, c.get("type") == "waterfall" and i not in (c.get("totals") or []))
                        for x in series]
                label = f"**{_cell(cat)}**" if i in hl else _cell(cat)
                out.append(f"| {label} | " + " | ".join(vals) + " |")
            out.append("")
            if s.get("key_number"):
                k = s["key_number"]
                out += [f"Key number **{k.get('value', '')}**, {k.get('label', '')}", ""]
            if s.get("takeaways"):
                out += [f"- {x}" for x in s["takeaways"]] + [""]
        elif t == "kpis":
            out += [f"- **{k.get('value', '')}** {k.get('label', '')}. {k.get('context', '')}" for k in s.get("kpis") or []] + [""]
        elif t == "table":
            tb = s.get("table") or {}
            cols = tb.get("columns") or []
            hl = set(tb.get("highlight_rows") or [])
            out.append("| " + " | ".join(_cell(x) for x in cols) + " |")
            out.append("|" + "---|" * len(cols))
            for i, r in enumerate(tb.get("rows") or []):
                cells = [_cell(x) for x in r]
                if i in hl:
                    cells[0] = f"**{cells[0]}**"
                out.append("| " + " | ".join(cells) + " |")
            out.append("")
        elif t == "columns":
            for col in s.get("columns") or []:
                head = " · ".join(x for x in [col.get("tag"), col.get("heading")] if x)
                out.append(f"- **{head}**" + (f". {col['body']}" if col.get("body") else ""))
                out += [f"  - {b}" for b in col.get("bullets") or []]
            out.append("")
        elif t == "quotes":
            for q in s.get("quotes") or []:
                out += [f"> “{q.get('text', '')}”  ", f"> {q.get('who', '')}", ""]
        elif t == "steps":
            out += [f"{i + 1}. **{x.get('label', '')}** {x.get('heading', '')}. {x.get('body', '')}"
                    for i, x in enumerate(s.get("steps") or [])] + [""]
        elif t == "library":
            for k, v in (s.get("content") or {}).items():
                label = str(k).replace("_", " ").capitalize()
                if isinstance(v, list) and v and all(isinstance(r, list) for r in v):
                    out.append(f"**{label}**")
                    out.append("")
                    width = max(len(r) for r in v)
                    out.append("| " + " | ".join([""] * width) + " |")
                    out.append("|" + "---|" * width)
                    out += ["| " + " | ".join(_cell(x) for x in r) + " |" for r in v]
                    out.append("")
                elif isinstance(v, list):
                    out.append(f"**{label}**")
                    out += [f"- {_cell(x) if not isinstance(x, dict) else ', '.join(f'{a}: {b}' for a, b in x.items())}" for x in v]
                    out.append("")
                elif isinstance(v, dict):
                    out.append(f"**{label}**")
                    out += [f"- {a}: {_cell(b)}" for a, b in v.items()]
                    out.append("")
                else:
                    out += [f"**{label}:** {_cell(v)}", ""]
        elif t == "section":
            pass
        for key, label in (("callout", "So what"), ("team_input", "Team input")):
            if s.get(key):
                out += [f"**{label}.** {s[key]}", ""]
        if s.get("footnotes"):
            out += [f"<sub>{i + 1}. {f}</sub>  " for i, f in enumerate(s["footnotes"])] + [""]
        if s.get("sources"):
            out += [f"<sub>{source_line(s, deck)}</sub>", ""]

    if srcs:
        out += ["## Sources", ""]
        for s in deck.get("sources", []):
            txt = ", ".join(x for x in [s.get("org"), s.get("doc"), s.get("date")] if x)
            url = f" [{s['url']}]({s['url']})" if str(s.get("url", "")).startswith("http") else ""
            out.append(f"- **{s.get('id')}** {txt}.{url}")
        out.append("")
    return "\n".join(out)


def run_check(path, quiet=False, plan=None):
    deck = load(path)
    errors, warns, open_items = check(deck)
    if plan:
        with open(plan, "w", encoding="utf-8") as f:
            f.write(plan_markdown(deck, open_items))
    if not quiet or errors:
        for e in errors:
            print("ERROR  ", e)
        for w in warns:
            print("WARN   ", w)
    if not quiet:
        print("\nStoryline (titles only, read top to bottom):")
        for line in storyline(deck):
            print(line)
        if deck.get("_sequence"):
            print("\nExhibit sequence (check for repeats):")
            print("   " + deck["_sequence"])
        if open_items:
            print("\nOpen items for the team:")
            for o in open_items:
                print("  ", o)
        print(f"\n{len(errors)} errors, {len(warns)} warnings")
        if plan:
            print(f"Deck plan written to {plan}")
    return deck, errors


if __name__ == "__main__":
    sys.exit(1 if run_check(sys.argv[1])[1] else 0)
