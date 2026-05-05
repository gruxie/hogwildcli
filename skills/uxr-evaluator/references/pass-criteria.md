# Pass Criteria — Borderline Cases

Covers situations where the evaluation call is not obvious. Default to `flag` rather than `fail` when in doubt.

---

## Prompted vs. unprompted responses

A prompted response can still be valid evidence — the question is whether the participant *elaborated in their own voice*.

- Restated moderator's framing + added detail → **pass** (or flag if thin)
- Only said "yeah" / "right" / "exactly" → **fail** (moderator-contamination)
- Redirected or added something moderator didn't suggest → **pass**

---

## Single-occurrence insights

A single mention is valid evidence for a `medium` or `low` confidence insight. Only **fail** if the claim implies recurrence that isn't there.

---

## Hedged participant language

Flag as `flag` if the claim removes hedges and presents something tentative as definite. The confidence should be `low` and claim should preserve tentativeness.

---

## Paraphrased quotes

- **Cosmetic changes → pass:** Removing filler words, condensing repeated phrases, minor punctuation.
- **Synonym substitution with same meaning → pass**
- **Different vocabulary that shifts meaning → fail**

---

## Compound claims

**Fail** and instruct extractor to split. Both claims need independent evidence.

---

## Absence of evidence

Negative claims only valid if topic was explicitly raised and participant actively dismissed it. If topic never came up → **fail** as `unsupported`.

---

## Cross-session synthesis

Evaluate each evidence block independently. If one file's evidence would fail alone, flag the insight and note which source is weak.
