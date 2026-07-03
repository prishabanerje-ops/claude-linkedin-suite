# PRD — LinkedIn Reach Optimization across the `post-linkedin` skill family

- **Date:** 2026-07-03
- **Author:** Aakash Srivastava (spec drafted with Claude)
- **Status:** Draft — awaiting review
- **Affected skills:** `post-linkedin`, `post-linkedin-feed-comments`, `post-linkedin-posts-comment`
- **Related:** LinkedIn reach diagnostic (03 Jul 2026) + 104-agent deep-research pass on 2026 LinkedIn reach mechanics

---

## 1. Background & problem

A live diagnostic of the author's account (2,652 followers) found that reach — not content quality — is the bottleneck:

- A representative post reached **~3% of followers (78 impressions)** vs. a verified healthy band of **8–12%**.
- Engagement **rate** was healthy (**~5%**, vs. a ~5.2% platform average) — people who see the posts engage; too few see them.
- Account-wide 7-day impressions were **down 24% WoW**.

Meanwhile the current skills contain guidance that actively works *against* reach as now understood:

| Current behavior | Conflicts with finding |
|---|---|
| `post-linkedin` publishes **only text or a single image** | Text-only is the **weakest** format (0.88× reach); documents (1.45×) unsupported |
| `post-linkedin` **mandates "exactly 3–5 hashtags"** | Hashtags have **no reliable 2026 reach effect** (claim survived as *not* a lever) |
| No guidance on outbound links | Link-in-body is the **lowest-reach** format (~3.25–3.7%) |
| Engagement scorecard rates **copy only** (hook/readability/relatability/CTA/credibility) | Ignores the **format + dwell + comment-pull** mechanics that actually drive reach |
| Generic "specific question" CTA | Under-weights that **comments ≫ likes** for breaking the distribution test-batch |

The two comment skills are already well-aligned (substantive comments, end-with-a-question, cap 2–3, no hashtags, verify-before-claiming); they mainly need the reach *rationale* baked in, plus one new bridging capability.

## 2. Goals

- G1. Make **format** a first-class, reach-ordered choice in `post-linkedin`, with **document carousels** fully supported (generation + publishing).
- G2. Encode the **verified 2026 reach mechanics** as the single source of truth all three skills follow.
- G3. Re-point `post-linkedin`'s CTA, link, and hashtag rules at **comment-pull and dwell**, not folklore.
- G4. Upgrade the engagement scorecard to score **reach**, not just copy.
- G5. Bake reach rationale + a **"seed your own first comment"** capability into the comment skills.
- G6. Preserve every existing safety property: explicit per-item approval, verify-before-claiming, never fabricate, stop-on-tool-failure.

## 3. Non-goals

- NG1. Do **not** rebuild the research/source-scraping or voice engines that already work.
- NG2. Do **not** implement myths the research **refuted**: a fixed "golden-hour" timer, a hashtag-count lever, an exact best-time-of-day, or a "3–5 posts/week magic frequency."
- NG3. Do **not** build browser-automation **poll creation** (polls are recommend-only — see R2.5).
- NG4. Do **not** change the UAE-vs-India audience strategy here (flagged in the diagnostic; out of scope for this PRD).

## 4. Success metrics

- M1. `post-linkedin` can generate and publish a ≥1-slide document carousel end-to-end (or cleanly fall back and say so).
- M2. Default recommended format is a document carousel; text-only requires passing a reach warning.
- M3. No skill instructs adding hashtags for reach; links default to the first comment.
- M4. The engagement scorecard emits a Reach Score with the four reach sub-dimensions.
- M5. All three skills cite `references/reach-playbook.md`; the playbook lists the refuted myths so they are never re-introduced.
- M6. Observationally (author-tracked, not a build gate): median post reach moves toward the 8–12% band over ~2–4 weeks.

## 5. Verified findings this PRD is built on

Tagged **[B]** = benchmark from verified research; **[M]** = measured on the account. Full sourcing lives in the reach-playbook (R1).

- **[B] Format reach multipliers (personal profiles):** poll **1.64×** › document **1.45×** › image **1.18×** › video **1.10×** › **text-only 0.88×** (below baseline). *(medium confidence — van der Blom; exact decimals are single-report.)*
- **[B] Format engagement rate:** native document ~7.0% (highest) … link posts ~3.25–3.7% (lowest). *(company-page-skewed — contextual, not 1:1.)*
- **[B] Dwell time is the #1 confirmed ranking signal** (LinkedIn Engineering, first-party). Carousels/video hold dwell; plain text is a 2-second scan.
- **[B] Engagement weighting:** comments & saves ≫ reactions/likes (directional consensus; exact 5×/2× multipliers are *unconfirmed*).
- **[B] Distribution = test-then-expand:** shown to a network slice first, expands only on strong early signal. The fixed "golden hour" framing was **refuted**.
- **[B] Benchmarks:** platform avg engagement ~5.2%; healthy per-post reach 8–12% of followers; organic reach down ~50% YoY.
- **[B] REFUTED (do not repeat):** golden-hour timer · saves-weighted-5× as fact · 3–5/week frequency sweet-spot · "company-page reach +33%" · "4+ links = higher reach" · video ~5× / live ~24× engagement · documents = highest *reach* (they lead on *rate*, not reach).
- **[M] Account context:** 2,652 followers; ~17% core SEO/marketing audience; 42% Senior; India-centric; reach ~3% vs 8–12% band; impressions −24% WoW.

## 6. Architecture

```
references/reach-playbook.md          NEW — single source of truth
        ▲            ▲            ▲
        │            │            │
 post-linkedin   feed-comments   posts-comment
   │  │  │                          ▲
   │  │  └── seed-first-comment ────┘  (post-publish handoff)
   │  └───── engagement scorecard += Reach Score
   └──────── scripts/linkedin_carousel.py  NEW (HTML→PDF→document publish)
             scripts/linkedin_post.py       EXTENDED (document publish path)
```

Precedence rule (unchanged): user's explicit words → existing skill behavior → this PRD's defaults.

## 7. Requirements

### R1 — `references/reach-playbook.md` (NEW, in `post-linkedin/references/`)
- R1.1 Contains: format multipliers table, engagement-weighting hierarchy, dwell-time note, distribution model, benchmarks, cadence guidance (2–4×/week, consistency-not-frequency), link/hashtag rules, and the **"Refuted — do not repeat"** list.
- R1.2 Every figure carries an integrity tag (**Measured / Benchmark / Inferred**) and a source link, mirroring the diagnostic's discipline.
- R1.3 Includes a dated **"data freshness"** header (figures are 2024–2026 vintage) so future readers know when to re-verify.
- R1.4 All three SKILL.md files add a one-line pointer: *"Reach decisions follow `references/reach-playbook.md`."*

### R2 — `post-linkedin/SKILL.md` changes
- **R2.1 Format chooser (replaces Step 1b image/text question).** Present formats in reach order with the multiplier shown:
  - Document carousel — **recommended** (1.45×)
  - Single image (1.18×)
  - Text-only (0.88×) — **allowed, but show a one-line reach warning** and confirm
  - Poll — **recommend-only** (see R2.5)
  Remembered choice routes publishing (R3 for carousel; existing image/text paths otherwise).
- **R2.2 CTA rule.** The post must end with **one sharp, specific question engineered to pull comments** (not likes). Update Step 3 structure + `post-formats.md` CTA guidance accordingly.
- **R2.3 Links.** Never place an outbound link in the post body. If a source/link is needed, it goes in the **first comment** (ties to R4.3). State this in Step 3 and the publish steps.
- **R2.4 Hashtags.** Remove the "exactly 3–5 (mandatory)" rule. New rule: **0–3, optional, de-emphasized; never a reach lever.** Update Step 3 and `post-formats.md`.
- **R2.5 Poll (recommend-only).** When a poll fits, the skill **drafts the poll question + options** and tells the user to post it manually (API can't create polls). It must also surface the "reach-trap" caveat (high reach, weak downstream engagement). No automation.
- **R2.6 Engagement scorecard += Reach Score (Step 4).** Add a distribution-focused block alongside the existing copy dimensions:
  - Format multiplier (from the chosen format)
  - Dwell potential (length/structure/carousel-ness, hook strength)
  - Comment-pull of the CTA (does the closing question invite replies?)
  - Link/hashtag hygiene (no body links; hashtags not over-used)
  Emit an overall **Reach Score** + one-line "biggest reach lever to improve." Keep the existing copy scorecard.
- **R2.7 Post-publish seed offer.** After a successful publish (Step 6/7), **offer to seed the first comment** (R4.3). If the post carried a link (R2.3), the seed comment is where it goes.
- **R2.8 Cadence & timing note.** Replace any time-of-day/frequency folklore with: post **2–4×/week consistently**, and **post when you can be present for the first 60–90 min** to seed/answer comments. Explicitly note the refuted myths (do not chase them).

### R3 — Carousel pipeline: `scripts/linkedin_carousel.py` (NEW) + `linkedin_post.py` (EXTENDED)
- **R3.1 Generation.** Input = approved slide content (derived by Claude from the post). Render **HTML/CSS → PDF** via **headless Chromium (Playwright `page.pdf`)**. Reuse the scorecard design tokens for on-brand slides.
- **R3.2 Slide spec.** ~**9 slides** (verified sweet spot; enforce a soft **≤10** cap with a warning), **portrait 4:5 (~1080×1350)**, short copy per slide, no body-text links, strong slide-1 hook, payoff mid-deck (dwell).
- **R3.3 Preview + approval.** Generate the PDF, **show it to the user, get approval** (mirrors the image-post flow: regenerate on request) before publishing.
- **R3.4 Publishing (primary).** Publish as a **LinkedIn document**: Documents API `initializeUpload` → PUT the PDF → create the post referencing the returned document URN. Extend `linkedin_post.py` with a `--document <pdf>` path (or a sibling function). Success = HTTP 201 + `post_id`; report it as proof.
- **R3.5 Publishing (fallback).** If the token lacks document-upload scope (see Risk 1), **fall back** to: (a) browser-automation upload of the PDF via Chrome DevTools MCP, or (b) hand the PDF to the user to upload — **and say clearly which path ran / that it wasn't auto-published.** Never claim success on a non-201.
- **R3.6 CLI contract.**
  - `linkedin_carousel.py --slides <json|md> --out /tmp/li_carousel.pdf [--seed …]` → prints `{"status":"success","path":…,"slides":N}` or `{"status":"error","detail":…}` (exit 1).
  - `linkedin_post.py --document /tmp/li_carousel.pdf --title "…" < post.txt` → publishes; same success/failure contract as today.
- **R3.7 Dependencies.** Document the Playwright/Chromium dependency + install step; note **weasyprint** as a lighter pure-Python alternative if Chromium is unavailable. Data-integrity: on any generation/publish failure, STOP and report the exact detail.

### R4 — Comment skills: `feed-comments` + `posts-comment`
- **R4.1 Reach rationale (both).** Add a short "why this matters for reach" note citing the playbook: comments compound reach for **both** parties; a substantive early comment on someone's post earns visibility; feed-commenting is deliberate **audience concentration** (grow the ~17% core).
- **R4.2 Early-window prioritization (feed-comments).** Tighten the relevance filter to prefer posts **still inside their early distribution window** (very recent and/or actively gaining engagement) where an early comment has outsized effect. (Keep the existing "recent or gaining traction" criterion; make the *why* explicit.)
- **R4.3 NEW capability — "seed your own first comment" (posts-comment).** Given a just-published post URL, draft + (on approval) post the **first comment** on the user's own post. Uses the existing browser-automation reply/comment machinery + approval gate + verify-before-claiming. Invoked either standalone or as the handoff target from `post-linkedin` R2.7. The seed comment carries any outbound link (R2.3) and opens the thread with a substantive point.
- **R4.4 No mechanics regressions.** Preserve caps (2–3/run for feed), per-item approval, no-hashtags-in-comments, verify + report permalink, stop-on-tool-failure.

## 8. Interfaces & data flow (carousel happy path)

1. User: `/post-linkedin` → topic + **format = document carousel**.
2. Research + draft post text (unchanged) → user approves text.
3. Claude derives ~9 slide contents → `linkedin_carousel.py` renders PDF → **preview + approve**.
4. `linkedin_post.py --document …` publishes via Documents API → `post_id` reported.
5. Skill **offers to seed the first comment** → `posts-comment` R4.3 posts it (link + opener) on approval → verify + report permalink.

## 9. Risks & mitigations

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| 1 | Token lacks LinkedIn **Documents API** scope | Medium–High | **First implementation task = verify scope** with a throwaway upload. Browser-upload fallback (R3.5). PRD does not assume success. |
| 2 | Playwright/Chromium not installed in the skill env | Medium | Document install; weasyprint fallback; fail loudly with the exact detail |
| 3 | Carousel visual quality poor at PDF scale | Low | Reuse proven scorecard tokens; preview-and-approve gate before publish |
| 4 | Format multipliers are 2024–25 vintage / single-report | Known | Playbook tags confidence + freshness; treat as directional, re-verify periodically |
| 5 | Users over-use polls (reach trap) | Low | Recommend-only + explicit reach-trap caveat (R2.5) |
| 6 | Browser automation for seed-comment flaky | Medium | Existing fallback pattern: type text, ask user to click Post, say it wasn't submitted |

## 10. Rollout / phasing (within this build)

- **Phase A:** R1 playbook + R2.2/R2.3/R2.4/R2.6/R2.8 (text/CTA/link/hashtag/scorecard/cadence) + R4.1/R4.2 (comment rationale). Low-risk, ships value immediately.
- **Phase B:** R2.1 format chooser + R3 carousel pipeline (gated on Risk 1 verification) + R2.7/R4.3 seed-first-comment.
- **Phase C:** R2.5 poll recommend-only polish.

## 11. Testing strategy

- Unit tests for `linkedin_carousel.py` (slide-count cap, PDF produced, JSON contract, error path) — mirror the existing `scripts/tests/` patterns.
- Extend `linkedin_post.py` tests for the `--document` path (success 201, non-201 failure, missing-scope fallback signal).
- Dry-run/scope-probe for the Documents API before wiring publish.
- Manual: full carousel happy path on a real (throwaway or low-stakes) post; verify `post_id` + seeded first comment permalink.
- Regression: existing text-only and single-image flows unchanged; all safety gates intact.

## 12. Acceptance criteria

- [ ] `reach-playbook.md` exists, is cited by all three skills, and lists the refuted myths.
- [ ] `post-linkedin` format chooser defaults to carousel; text-only shows a reach warning.
- [ ] No skill recommends hashtags for reach; links route to the first comment.
- [ ] Engagement scorecard emits a Reach Score with all four sub-dimensions.
- [ ] Carousel generates a previewable PDF and publishes as a document **or** cleanly falls back with an honest status.
- [ ] "Seed your own first comment" works standalone and as the post-publish handoff.
- [ ] All existing safety properties (approval, verify, no-fabrication, stop-on-failure) preserved.

## 13. Out of scope / future

- UAE-vs-India audience concentration strategy (separate initiative).
- Poll creation automation.
- Analytics ingestion (auto-reading reach after posting to close the loop).
- Scheduling / cadence automation.
