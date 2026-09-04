# Where sections 36 to 42 come from

These patterns are not derived from a style guide. They come from line-by-line
markup on a technical report that had already been through a humanizer pass and
was still identified as machine-written by two subject-matter reviewers.

Reviewers are anonymized here as **Reviewer A** (subject-matter lead, who flagged
AI tells) and **Reviewer B** (program analyst, who flagged comprehension gaps).
The report itself is a program evaluation of roughly 12,000 words. Quotes are
verbatim; project-identifying detail has been removed.

## What made it detectable

Reviewer A left eleven comments reading only "AI flag" or "AI Flag" with no
elaboration, plus three that explained the tell. The explained ones are the
useful ones, because they name a pattern rather than a sentence.

### On colons

> "You have 101 colons throughout this report. This is the new 'm-dash', i.e.,
> it is very clearly AI. It reads fine, usually, but it can damage credibility.
> Need to rewrite anything that is easily detectable as AI."

This is the single highest-value comment in the set. The writer had already
removed every em dash, and the colon had absorbed the same job. The volume is
what gives it away, not any individual sentence, which is why a writer reading
their own draft never sees it.

The resolution adopted a rule: a colon is legitimate for a definition, a list of
three or more, a title, a ratio, or a short parenthetical. Everything else is a
splice and becomes a sentence boundary. Applying it took the executive summary
from 11 colons to 5, with the 4 legitimate ones untouched.

### On paragraph rhythm

> "Note these short topic sentences on almost all paragraphs. Def AI."

Left against a section where most paragraphs opened with a short declarative
claim followed by supporting detail. One such paragraph is ordinary. A run of
them is a cadence no writer sustains unintentionally.

### On section openings

> "AI flag. This is the first sentence of the methods section. It should start
> out broad to orient the reader about the methods, this just jumps directly
> into explaining a limitation of the many approaches. I might start with
> stating that [the program] was a long running program with many changes and
> pauses that can be leveraged to gain insight on the impact..."

The draft opened its methods section with the most defensible sentence rather
than the most orienting one. This is a specific habit: the model front-loads the
caveat because the caveat is what it is least likely to be wrong about.

### On executive summary scope

> "This is getting pretty deep into the weeds for an executive summary. I'm
> familiar with the approach and having trouble following this. Might just
> remove these sentences or simplify."

> "This doesn't seem like something that should be in executive summary."

> "If you want to include, maybe add as a footnote."

An executive summary written by compressing the body inherits the body's
priorities. It should instead be written from the decision the reader has to
make.

### On self-rating

Two comments marked "AI flag" landed on "the cleanest of the four events" and
"the most direct evidence comes from...". A later correction pass classified
these as unearned superlatives and the adjectives in "deliberately conservative"
and "documented audit" as process-virtue, then removed both categories.

## What reviewers asked for that is not an AI tell

Reviewer B's comments were about comprehension rather than provenance, and they
recur on technical reports regardless of authorship. They are collected in the
skill under "Technical report conventions" because they cost less to fix in
drafting than in review.

The most frequent, in order of how often they appeared:

- "Suggest a bit more explanation for this paragraph to help the non-technical
  reader understand" (four times)
- "Introduce table in narrative above"
- "Suggest a lead-in phrase. E.g., 'In the false-positive testing described
  [wherever the approach is described], ...'"
- "Recommend helping with interpretation. E.g., '..., suggesting...'"
- "Not sure what this means" and "Unclear what this means" (five times between
  them, always on a sentence carrying a defined term used loosely)
- "Context needed"
- "Suggest citing the source and describing what this is exactly"

A pattern worth noting: several of Reviewer B's "not sure what this means"
comments landed on sentences that were grammatically fine. The failure was a
term doing two jobs, or a percentage without its denominator.

## Validation

`scripts/audit.py` was run against the marked-up report after the patterns were
encoded. Without being given any of the flagged phrases, it reported:

```
[FAIL] S36  colon splices               32   (40 legitimate colons kept)
[FAIL] S37  short-opener runs of 3+     6   (longest run 29; 62/134, 46%)
[warn] S38  unearned superlatives       5   ['the cleanest', 'the most direct', ...]
[warn] S39  process-virtue adjectives   8   ['deliberately', 'disciplined']
```

It recovered "the cleanest", "the most direct", and "deliberately", which are
three of the specific spans a human reviewer marked. That is the argument for
running the script: these patterns are mechanical enough to count, and counting
them is faster and more reliable than rereading for cadence.
