---
description: Spot-check a call-extractor record against its transcript (external QA).
argument-hint: [record] [transcript]
---

External QA for a `call-extractor` output. You are given one extracted record and the transcript it came from. Audit the record against the transcript on every dimension:

1. **Citations** — does every `verbatim_quote` appear word-for-word in the transcript? (missing or altered quote = fail)
2. **Grounding** — is any pain point, competitor, or figure present that was never said? (invented = fail)
3. **Completeness** — is there a use case or a stated pain in the transcript the record missed?
4. **Pain vs. pull** — is anything filed as a pain that is really a wish (a pull)?
5. **Canonical names** — are all products and competitors using the canonical labels?
6. **Edge cases** — for short, internal, or non-English calls, were the rules applied (confidence, scope, nulls)?
7. **Format** — valid JSON, all schema keys present, and nothing but JSON?

Score each dimension 1-5 and flag any failure with the specific field. If everything passes, say so in one line.
