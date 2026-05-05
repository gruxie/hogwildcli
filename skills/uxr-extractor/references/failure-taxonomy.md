# Failure Taxonomy

Defines the named failure modes used by both the extractor (to avoid them) and the evaluator (to detect them).

---

## EXTRAPOLATION

**Definition:** The transcript shows X, but the insight claims Y — where Y is a logical consequence the participant did not state.

**Example:**
- Transcript: *"I use VS Code for the AI stuff because it was easier to set up."*
- Bad: *"Devon prefers VS Code as his primary development environment."*
- Good: *"Devon uses VS Code specifically for AI-assisted tasks due to easier setup, not as his primary IDE."*

**Check:** Can you find the exact claim in the participant's words? If not, it's extrapolation.

---

## ATTRIBUTION BLEED

**Definition:** A claim about "participants" or "users" when only one person's turns support it. Or: a claim attributed to the interviewee that comes from the moderator's framing.

**Example:**
- Moderator: "Would you say trust is a big factor?" — Participant: "Yeah, definitely."
- Bad: *"Trust is a key factor in developers' AI adoption."*
- Good: *"When asked, Devon agreed that trust is a factor — though this was prompted, not volunteered."*

---

## HYPOTHESIS PROJECTION

**Definition:** The insight mirrors hypothesis language so closely it appears the analyst confirmed what they expected rather than reading what was said.

**Example:**
- Hypothesis: *"Developers hesitate due to lack of trust in output quality."*
- Bad: *"Devon hesitates to adopt AI due to lack of trust in output quality."*
- Good: *"Devon's early hesitation stemmed from wanting to understand and control what the code does — a preference for transparency over delegation."*

---

## FREQUENCY DISTORTION

**Definition:** The insight implies a pattern or habit when evidence shows it was mentioned once, briefly, or tentatively.

**Example:**
- Transcript: Participant mentions once they sometimes ask AI for suggestions.
- Bad: *"Devon regularly uses AI to generate code suggestions."*
- Good: *"Devon described occasionally asking the AI for suggestions, which he then reviews."*

---

## UNSUPPORTED

**Definition:** No turn contains evidence for this insight. The claim may be plausible but isn't in the data.

**Check:** Search `_turns.json` for the speaker and any quoted text. If neither appears, the insight is unsupported.

---

## QUOTE DISTORTION

**Definition:** A quote is included but has been altered or paraphrased in a way that changes its meaning.

**Check:** String-match the quote against the corresponding turn. Minor filler removal is acceptable. Paraphrasing is not.

---

## MODERATOR CONTAMINATION

**Definition:** The insight relies on the moderator's words — either as a proxy for the participant's view, or because the participant only agreed without elaborating.

**Check:** Is the supporting quote from the interviewee? Does it stand on its own without the moderator's framing?
