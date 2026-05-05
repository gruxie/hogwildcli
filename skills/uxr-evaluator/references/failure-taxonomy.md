# Failure Taxonomy

Defines the named failure modes used by both the extractor (to avoid them) and the evaluator (to detect them).

---

## EXTRAPOLATION

**Definition:** The transcript shows X, but the insight claims Y — where Y is a logical consequence the participant did not state.

**Check:** Can you find the exact claim in the participant's words? If not, it's extrapolation.

---

## ATTRIBUTION BLEED

**Definition:** A claim about "participants" or "users" when only one person's turns support it. Or: a claim attributed to the interviewee that comes from the moderator's framing.

**Check:** Is the claim scoped to the individual? Does the quote come from the interviewee?

---

## HYPOTHESIS PROJECTION

**Definition:** The insight mirrors hypothesis language so closely it appears the analyst confirmed expectations rather than reading what was said.

**Check:** Does the insight use the same framing as the hypothesis? If yes, re-derive from participant's own words.

---

## FREQUENCY DISTORTION

**Definition:** The insight implies a pattern when evidence shows it was mentioned once or tentatively.

**Check:** Count the supporting turns. Does the claim language match actual frequency?

---

## UNSUPPORTED

**Definition:** No turn contains evidence for this insight.

**Check:** Search `_turns.json` for the quoted text. If not found, the insight is unsupported.

---

## QUOTE DISTORTION

**Definition:** A quote has been altered in a way that changes meaning.

**Check:** String-match against the turn. Minor filler removal is OK. Paraphrasing is not.

---

## MODERATOR CONTAMINATION

**Definition:** The insight relies on the moderator's words as evidence.

**Check:** Does the supporting quote stand on its own without the moderator's framing?
