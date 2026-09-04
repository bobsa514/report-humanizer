#!/usr/bin/env python3
"""
audit.py - count the AI writing patterns that survive a humanizer pass.

    python3 scripts/audit.py REPORT.md [--verbose]

Reads Markdown or plain text. Reports the patterns from SKILL.md sections 14,
36 through 39, and 41, each of which is mechanical enough to count. Exits 1 if
any hard check fails, so it can gate a build.

The counts are a prompt to look, not a verdict. A legitimate colon is not a
splice, and two short openers in a row are not a run.
"""
import argparse
import re
import sys

# Section 39. Adjectives that praise the method instead of describing it.
PROCESS_VIRTUE = [
    "deliberately", "carefully", "rigorously", "thoroughly", "systematically",
    "comprehensively", "robustly", "principled", "disciplined", "meticulously",
]

# Section 38. Self-rating rather than measurement.
SUPERLATIVE = [
    r"\bthe (?:most|least) (?:direct|compelling|convincing|robust|reliable|important)\b",
    r"\bthe (?:cleanest|strongest|clearest|sharpest|best)\b",
    r"\bmost notably\b", r"\bcrucially\b", r"\bcritically\b",
]

# Section 36. Colons that are correct punctuation and must not be counted.
def is_legitimate_colon(sentence: str) -> bool:
    # a terminal colon introduces whatever block follows: a list, a quote, a
    # code fence, a table. That is correct punctuation, not a splice.
    if sentence.rstrip().endswith(":"):
        return True
    before, _, after = sentence.partition(":")
    # a list of three or more items
    if after.count(",") >= 2 or after.count(";") >= 2:
        return True
    # a title, a ratio, or a time
    if re.search(r"\b\d+:\d+\b", sentence):
        return True
    if re.search(r"[*_\"']\s*$", before) or re.search(r"^\s*\d{4}\b", after.strip()):
        return True
    # an explicit definition
    if re.search(r"\b(?:defined as|termed|referred to as|means)\b", before, re.I):
        return True
    # a numbered lead-in: "Four fields establish the limit: a, b, c and d"
    if re.search(r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+", before, re.I) \
            and after.count(",") >= 1:
        return True
    return False


def strip_markdown(text: str):
    """Return prose paragraphs only: no front matter, headings, tables, figures."""
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    out, sections = [], []
    for block in text.split("\n\n"):
        b = block.strip()
        if not b:
            continue
        if b.startswith("#"):
            sections.append(b)
            out.append(("heading", b))
            continue
        if b.startswith(("|", "!", "Figure ", "Table ", ">")) or b.startswith("*Source"):
            continue
        if re.match(r"^\*[^*]+\*$", b):      # italic caption line
            continue
        out.append(("prose", b))
    return out


def sentences(p: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]


def drop_quoted(text: str) -> str:
    """Blank out quoted spans, code spans and links.

    A watched phrase inside a quotation is being discussed, not used. The skill's
    own false-positive rule exempts secondhand text, so the counter must too.
    """
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r'"[^"]*"', " ", text)
    text = re.sub(r"\u201c[^\u201d]*\u201d", " ", text)
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", text)
    return text


def audit(path: str, verbose: bool = False) -> int:
    raw = open(path, encoding="utf8").read()
    blocks = strip_markdown(raw)
    prose = [b for kind, b in blocks if kind == "prose"]
    words = sum(len(p.split()) for p in prose)
    failures = 0

    print(f"{path}\n{len(prose)} prose paragraphs, {words:,} words\n")

    # -- 14. em and en dashes -------------------------------------------------
    dashes = sum(len(re.findall(r"[—–]", p)) for p in prose)
    status = "ok" if dashes == 0 else "FAIL"
    failures += dashes > 0
    print(f"[{status:4s}] S14  em/en dashes                {dashes}")

    # -- 36. colon splices ----------------------------------------------------
    splices, legit = [], 0
    for p in prose:
        for s in sentences(drop_quoted(p)):
            if ":" not in s:
                continue
            if is_legitimate_colon(s):
                legit += 1
            else:
                splices.append(s)
    status = "ok" if not splices else "FAIL"
    failures += bool(splices)
    print(f"[{status:4s}] S36  colon splices               {len(splices)}   ({legit} legitimate colons kept)")
    if verbose:
        for s in splices:
            print(f"          {s[:150]}")

    # -- 37. runs of short paragraph openers ----------------------------------
    short = [i for i, p in enumerate(prose) if len(sentences(p)[0].split()) < 14]
    runs, cur = [], []
    for i in short:
        if cur and i == cur[-1] + 1:
            cur.append(i)
        else:
            if cur:
                runs.append(cur)
            cur = [i]
    if cur:
        runs.append(cur)
    bad = [r for r in runs if len(r) >= 3]
    longest = max((len(r) for r in runs), default=0)
    status = "ok" if not bad else "FAIL"
    failures += bool(bad)
    pct = len(short) / len(prose) * 100 if prose else 0
    print(f"[{status:4s}] S37  short-opener runs of 3+     {len(bad)}   "
          f"(longest run {longest}; {len(short)}/{len(prose)} paragraphs, {pct:.0f}%)")
    if verbose:
        for r in bad:
            for i in r:
                print(f"          p{i}: {sentences(prose[i])[0][:110]}")

    # -- 38 and 39. superlatives and process virtue ---------------------------
    unquoted = [drop_quoted(p) for p in prose]
    sup = [m.group(0) for p in unquoted for pat in SUPERLATIVE
           for m in re.finditer(pat, p, re.I)]
    status = "ok" if not sup else "warn"
    print(f"[{status:4s}] S38  unearned superlatives       {len(sup)}"
          + (f"   {sorted(set(x.lower() for x in sup))}" if sup else ""))

    virt = [w for p in unquoted for w in PROCESS_VIRTUE
            if re.search(rf"\b{w}\b", p, re.I)]
    status = "ok" if not virt else "warn"
    print(f"[{status:4s}] S39  process-virtue adjectives   {len(virt)}"
          + (f"   {sorted(set(virt))}" if virt else ""))

    # -- 41. numbered sections opening on a subsection ------------------------
    missing = []
    for i, (kind, b) in enumerate(blocks):
        if kind != "heading":
            continue
        if not re.match(r"^# (?:\d+\.|Appendix)", b):
            continue
        nxt = next((blocks[j] for j in range(i + 1, len(blocks))), None)
        if nxt and nxt[0] == "heading" and nxt[1].startswith("##"):
            missing.append(b.lstrip("# ").strip())
    status = "ok" if not missing else "FAIL"
    failures += bool(missing)
    print(f"[{status:4s}] S41  sections with no lead-in    {len(missing)}"
          + (f"   {missing}" if missing else ""))

    print("\n" + ("all hard checks pass" if not failures
                  else f"{failures} hard check(s) failed"))
    return 1 if failures else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print each flagged sentence")
    a = ap.parse_args()
    sys.exit(audit(a.path, a.verbose))
