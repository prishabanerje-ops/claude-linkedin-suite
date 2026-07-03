---
name: post-linkedin
description: >
  Research-backed LinkedIn assistant with two modes.
  WRITE mode drafts data-driven LinkedIn posts on three pillars —
  (1) SEO landscape evolution and AI's impact on search,
  (2) AI in everyday professional life,
  (3) Vibe Coding and AI-assisted development — by scraping 3-5 live
  authoritative sources, then scores the post for engagement potential.
  Posts can be text-only or carry one auto-generated image — the flow asks which
  (or treats "with an image" as an explicit image request).
  ENGAGE mode drives a logged-in browser to read the comments on your own
  posts and reply to them, and to scan your home feed and comment on relevant
  posts (always with your per-item approval).
  Invoke this skill whenever the user wants to write a LinkedIn post OR engage
  on LinkedIn — e.g. "write me a LinkedIn post about X", "help me post on
  LinkedIn", "reply to the comments on my LinkedIn post", "check my LinkedIn
  comments", "draft a reply to this comment", "comment on relevant posts in my
  feed", or "engage on LinkedIn for me". Even brief asks like "draft a LinkedIn
  reply" or "see my LinkedIn feed and comment" should trigger this skill.
  Image-post asks like "write me a LinkedIn post about X with an image" are also
  handled (the flow generates a visual); if image vs text is unspecified, it asks.
user-invokable: true
argument-hint: "[write | engage] [topic or context] [with an image]"
metadata:
  author: Aakash Srivastava
  version: "1.1.0"
  category: social
---

# LinkedIn Post Creator

Writes data-driven LinkedIn posts on three topic pillars, grounded in real sources
scraped from authoritative sites. Each post follows proven LinkedIn engagement patterns.

## Mode — Write or Engage (decide this first)

This skill has two modes. Detect which one the request needs:

- **Write mode** (default) — the user wants to *create* a new LinkedIn post.
  Continue with Step 1 below.
- **Engage mode** — the user wants to *interact* with existing LinkedIn content:
  read/reply to comments on their own posts, or comment on posts in their home feed.
  Triggers include "reply to my comments", "check the comments on my post",
  "draft a reply", "comment on relevant posts in my feed", "engage on LinkedIn".
  → **Read `references/engage-and-comment.md` and follow it.** Engage mode uses
  **browser automation** (Chrome DevTools MCP) on a logged-in session — it does
  **not** use the post-creation steps or the post API below, because that API cannot
  read the feed or post comments.

If it's genuinely ambiguous which mode is wanted, ask the user.

## Step 1 — Detect Topic Type

Match the user's request to one of three pillars:

| Pillar | Trigger phrases | Slug |
|--------|----------------|------|
| **SEO + AI** | "SEO", "search", "Google AI", "AI Overviews", "search landscape", "ranking" | `seo-ai` |
| **AI in Daily Life** | "AI daily", "AI productivity", "AI tools I use", "day to day AI", "everyday AI" | `ai-life` |
| **Vibe Coding** | "vibe coding", "AI coding", "cursor", "claude code", "copilot", "AI developer", "build with AI" | `vibe-coding` |

If unclear, ask the user: _"Which topic: (1) SEO + AI changes, (2) AI in your daily life, or (3) Vibe Coding?"_

Read `references/source-domains.md` for authoritative sources per pillar.

## Step 1b — Image post or text-only? (decide before writing)

Every write-mode post is either **text-only** or has **one auto-generated image**.
Settle this up front so the publish step knows which path to take:

- **Explicit image request → image post.** Triggers in the user's words: "with an
  image", "with a visual", "add an image/picture/graphic", "image post".
- **Explicit text-only → text-only post.** Triggers: "text only", "no image", "just text".
- **Unspecified → ASK the user** (one quick question, before researching/writing):
  > "Do you want this as an **image post** (I'll generate a visual from the post) or **text-only**?"

Remember the choice. The image itself is generated **later** — in **Step 7**, after the
post text is approved (the prompt is derived from the final text). Writing/research below
is identical either way; only the publish step branches.

## Step 2 — Research Phase (scrape 3-5 sources)

Use WebSearch to find 3-5 recent, authoritative articles on the detected topic:

```
Search query examples:
- seo-ai:       "AI Overviews SEO impact 2026" OR "how AI is changing search 2026"
- ai-life:      "AI productivity tools professionals 2026" OR "how people use AI daily"
- vibe-coding:  "vibe coding trend developers 2026" OR "AI pair programming results"
```

For each result, use WebFetch to pull the actual page content (not just snippets).
Extract:
- **The core insight** (1-2 sentences: what changed, what's new, what's surprising)
- **A specific data point or quote** (numbers, percentages, named examples — these make posts credible)
- **Source name + URL** (for transparency in your reasoning, not published in the post)

Aim for facts that would make a LinkedIn reader stop scrolling. Surprising stats beat
obvious observations. Recent beats evergreen.

## Step 3 — Write the LinkedIn Post

Read `references/post-formats.md` for hook patterns, storytelling templates, and CTA options.

### Post structure (non-negotiable order):

```
[HOOK — 1 line, ends with either a bold claim, surprising stat, or question]

[BLANK LINE]

[SETUP — 2-3 lines context. What was true before? What changed?]

[BLANK LINE]

[STORY or INSIGHT — 3-5 lines. The meat. Use the scraped data here.
 Short sentences. One idea per line where possible.]

[BLANK LINE]

[TAKEAWAYS — 2-4 bullets, each starting with an emoji or →]
→ ...
→ ...
→ ...

[BLANK LINE]

[PERSPECTIVE — 1-2 lines. Your take. First-person. Opinionated.]

[BLANK LINE]

[CTA — question that invites a reply. Not generic "thoughts?" — make it specific.]

[BLANK LINE]

[HASHTAGS — exactly 3-5, on one line, relevant and searchable]
```

**Tone:** Conversational but credible. Write like a senior professional sharing a
real observation with peers — not a marketer broadcasting. Avoid corporate jargon,
excessive adjectives, and hollow phrases like "game-changer" or "revolutionize".

**Length:** 150-250 words is the sweet spot for LinkedIn engagement. Don't pad.

## Step 4 — Engagement Analysis

After writing the post, score it across 5 dimensions. Be honest — a hard score is more
useful than flattery.

```
## Post Engagement Analysis

Hook strength:        [1-10] — Does line 1 force you to keep reading?
Readability:          [1-10] — Short paragraphs, white space, easy scan?
Relatability:         [1-10] — Does the audience recognize their own situation?
CTA quality:          [1-10] — Is the question specific enough to get replies?
Credibility signals:  [1-10] — Stats, named examples, real data present?

Overall score:        [avg/10]
Predicted engagement: Low / Medium / High / Viral potential

Key strengths:
- ...

What could improve it:
- ...

Suggested A/B test: [alternative hook line to try]
```

**Engagement benchmarks:**
- 8-9 avg → High engagement likely (top 10% LinkedIn posts)
- 6-7 avg → Medium engagement (above average)
- Below 6 → Needs a rewrite — identify the weakest dimension and fix it

## Step 5 — Output Format

Present to the user in this order:
1. **Sources used** — short bulleted list with 1-line summaries
2. **The LinkedIn post** — inside a copyable code block
3. **Engagement analysis** — the scorecard
4. **Offer a rewrite** — "Want me to try a different hook / shorter version / more personal angle?"

## Approval Gate (mandatory)

After presenting the post, always ask:

> "Ready to post this, or would you like any changes first?"

Do not treat the task as complete until the user explicitly approves the post.
Never simulate posting, schedule it, or mark it ready-to-go without a clear "yes" or "approved" from the user.

**After approval, route by the Step 1b decision:**
- **Text-only post → Step 6** below.
- **Image post → Step 7** (generate + preview the image, get a second approval on the
  image, then publish text + image in one call). Do **not** also run Step 6 — Step 7 does the publishing.

## Step 6 — Publish text-only (after explicit approval)

This skill can publish directly to LinkedIn via `scripts/linkedin_post.py` — there is
**no MCP tool**; publishing is done by running this script. Do not tell the user there
is "no LinkedIn integration" — use this script.

- **Credentials:** read from `~/.config/linkedin-api.env`
  (`LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_ID`; also `LINKEDIN_CLIENT_ID`/`SECRET`).
  Never print or echo the token.
- **How to call** (pipe the exact approved text via stdin to avoid shell-escaping
  arrows/em-dashes; write it to a temp file first):
  ```
  python3 scripts/linkedin_post.py < /path/to/approved_post.txt
  # or: python3 scripts/linkedin_post.py "post text here"
  ```
- **Success looks like:** JSON with `"status": "success"`, `"http_status": 201`, and a
  `post_id` (e.g. `urn:li:share:...`). Report the `post_id` back to the user — that is
  the verified confirmation it went live.
- **On failure** (non-201, missing env file, missing keys): STOP, report the exact
  `detail`/`http_status` returned, and do NOT claim the post was published.

## Step 7 — Image posts (when Step 1b chose an image post)

Run this **instead of Step 6** when the post is an image post. It attaches a single
image generated for **free** (no API key) from the post's own text, via Pollinations,
and uploaded through LinkedIn's modern Images API. (A user-supplied image works too —
see 7c.) The text-only flow (Step 6) is unchanged and unaffected.

### 7a. Derive the image prompt (Claude does this)
Read the approved post text and write a concise (1–3 sentence) visual prompt.
- Favor **abstract / conceptual / isometric / flat-illustration** styles.
- **Avoid** literal faces, hands, and embedded text — the free model renders
  these poorly. Surface the derived prompt to the user before generating.

### 7b. Generate and preview
Run the generator (separate, previewable step):
```
python3 scripts/linkedin_image.py --prompt "<derived prompt>" --out /tmp/li_image.jpg [--seed <int>]
```
- Output is **768×768 JPEG** (the free model caps resolution; size params are
  ignored). Use `--seed <int>` to reproduce a chosen image.
- On success it prints `{"status":"success","path":...}`; on failure
  `{"status":"error","detail":...}` and exits 1 — STOP and report the detail.
- **Show the image to the user and get approval** before publishing. Regenerate
  with a new seed or revised prompt if they want changes.

### 7c. Publish with the image
After approval, publish (post text via stdin, as usual):
```
python3 scripts/linkedin_post.py --image /tmp/li_image.jpg --alt-text "<alt text>" < /path/to/approved_post.txt
```
- If `--alt-text` is omitted, the first line of the post is used.
- A user-supplied image works the same way — just point `--image` at any
  existing PNG/JPEG (< 5 MB).
- Success prints a final JSON with `"status":"success"` and a `post_id`. On any
  non-201 / upload error it reports the exact `detail`/`http_status` and exits 1
  — do NOT claim the post was published.

### Known limitations
- **768×768** max (below LinkedIn's ideal ~1200²; fine for feed display).
- **No SLA** — Pollinations is a free community service; failures are surfaced.
- **Not private** — prompts/images may be publicly cached on Pollinations' feed;
  use generic conceptual prompts, never confidential content.
