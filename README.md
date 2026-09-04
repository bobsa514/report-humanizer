# report-humanizer

A Claude Code skill for technical reports that a domain expert will read.

It extends [blader/humanizer](https://github.com/blader/humanizer) with seven
patterns that a standard humanizer pass does not catch, plus a script that
counts them.

## Why it exists

A 12,000 word program evaluation went through a humanizer pass. Every em dash
was gone, the stock AI vocabulary was gone, and two subject-matter reviewers
still marked it as machine-written, eleven times.

Their comments named patterns the Wikipedia "Signs of AI writing" list does not
cover. The most useful one:

> "You have 101 colons throughout this report. This is the new 'm-dash', i.e.,
> it is very clearly AI. It reads fine, usually, but it can damage credibility."

The colon had absorbed the job the em dash used to do. Removing one tell had
produced another. That is the gap this skill fills.

## What it adds

| Section | Pattern | Reviewer comment that identified it |
|---|---|---|
| 36 | Colon splices | "This is the new m-dash" |
| 37 | Runs of short paragraph openers | "Note these short topic sentences on almost all paragraphs. Def AI." |
| 38 | Unearned superlatives | AI flag on "the cleanest of the four events" |
| 39 | Process-virtue adjectives | AI flag on "deliberately conservative" |
| 40 | Announcing a point instead of making it | Correction pass |
| 41 | Sections that open on a caveat | "It should start out broad to orient the reader" |
| 42 | Executive summary depth | "Getting pretty deep into the weeds for an executive summary" |

Plus a short section of technical report conventions, drawn from the review
comments that were about comprehension rather than provenance: introduce every
table in the narrative above it, state the denominator, give results a lead-in,
and so on.

Sections 1 through 35 are unchanged from upstream humanizer.

## Install

```bash
git clone git@github.com:bobsa514/report-humanizer.git ~/.claude/skills/report-humanizer
```

Restart Claude Code. Newly installed skills are read at session start, so the
slash command will not resolve until you do.

Then invoke it as `/report-humanizer`, or ask for a humanizer pass on a report
and it will be selected by its description.

## The audit script

The new patterns are mechanical enough to count, which is faster and more
reliable than rereading a long document for cadence.

```bash
python3 scripts/audit.py REPORT.md          # summary
python3 scripts/audit.py REPORT.md -v       # print every flagged sentence
```

```
report.md
63 prose paragraphs, 3,988 words

[ok  ] S14  em/en dashes                0
[ok  ] S36  colon splices               0   (5 legitimate colons kept)
[ok  ] S37  short-opener runs of 3+     0   (longest run 2; 18/63 paragraphs, 29%)
[ok  ] S38  unearned superlatives       0
[ok  ] S39  process-virtue adjectives   0
[ok  ] S41  sections with no lead-in    0

all hard checks pass
```

It exits non-zero when a hard check fails, so it can gate a build. It reads
Markdown and skips front matter, headings, tables, figure captions and source
lines, so it measures prose only.

The counts are a prompt to look, not a verdict. A colon introducing a list is
not a splice, and two short openers in a row are not a run. The script applies
those exemptions, but judgment still belongs to the writer.

## Does it work

Run against the marked-up report that prompted the skill, with no knowledge of
which spans a human had flagged:

```
[FAIL] S36  colon splices               32   (40 legitimate colons kept)
[FAIL] S37  short-opener runs of 3+     6   (longest run 29; 62/134, 46%)
[warn] S38  unearned superlatives       5   ['the cleanest', 'the most direct', ...]
[warn] S39  process-virtue adjectives   8   ['deliberately', 'disciplined']
```

It recovered "the cleanest", "the most direct" and "deliberately", three of the
exact spans the reviewer marked by hand.

## Files

```
SKILL.md                        the skill; sections 36 to 42 are the additions
scripts/audit.py                pattern counter
references/reviewer-flags.md    the review markup the additions came from
LICENSE                         MIT, with upstream attribution
```

## License

MIT. Sections 1 through 35 of SKILL.md derive from
[blader/humanizer](https://github.com/blader/humanizer) (MIT), itself based on
[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(CC BY-SA 4.0). See LICENSE.
