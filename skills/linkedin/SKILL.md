---
name: linkedin
description: >
  Research-backed LinkedIn assistant with four modes.
  WRITE mode drafts data-driven LinkedIn posts on three pillars —
  (1) SEO landscape evolution and AI's impact on search,
  (2) AI in everyday professional life,
  (3) Vibe Coding and AI-assisted development — by scraping 3-5 live
  authoritative sources, then scores the post for engagement potential.
  Posts can be text-only, carry one auto-generated image, or use an external
  (bring-your-own) image: the flow writes a ready-to-paste image-generation prompt
  (Nano Banana / Gemini, Midjourney, DALL-E) alongside the post, then publishes the
  image the user brings back. The flow asks which format (or treats "with an image"
  as an explicit image request and "give me an image prompt" / "I'll make the image
  myself" as the external-image path).
  FEED ENGAGE mode drives a logged-in browser to scan your home feed and
  comment on relevant posts (always with your per-item approval), logging each
  posted comment to a ledger. REPLY mode drives a logged-in browser to read the
  comments on your own posts and reply to them. CHECK REPLIES mode sweeps that
  ledger and the notifications page to find replies to comments you left on
  OTHER people's posts ("any replies to my comments?") and answers them with
  per-reply approval.
  Invoke this skill whenever the user wants to write a LinkedIn post OR engage
  on LinkedIn — e.g. "write me a LinkedIn post about X", "help me post on
  LinkedIn", "reply to the comments on my LinkedIn post", "check my LinkedIn
  comments", "draft a reply to this comment", "comment on relevant posts in my
  feed", or "engage on LinkedIn for me". Even brief asks like "draft a LinkedIn
  reply" or "see my LinkedIn feed and comment" should trigger this skill.
  Image-post asks like "write me a LinkedIn post about X with an image" are also
  handled (the flow generates a visual); if image vs text is unspecified, it asks.
  Also triggers on "comment on relevant posts in my feed", "scan my feed and
  comment", "reply to the comments on my posts", "check my LinkedIn comments",
  or "/linkedin".
user-invokable: true
argument-hint: "[write | engage] [topic or context] [with an image | image prompt only]"
metadata:
  author: Aakash Srivastava
  version: "1.4.1"
  category: social
---

# LinkedIn Hub

## On EVERY /linkedin invocation — open-threads reminder (before anything else)

Read `data/comments-log.jsonl`. If any entry has `status: "open"`, start the response
with a one-line reminder BEFORE running the requested mode, e.g.:

> 🔔 You have N open comment threads (Lydia Fox, Lidia Infante, …) — want me to check
> for replies after this?

- Just a reminder — do NOT switch modes uninvited; run what the user asked for, then
  offer the check at the end.
- If the user invoked check-replies mode itself, skip the reminder (redundant).
- Ledger missing/empty or no `open` entries → no reminder, proceed silently.

Four modes. WRITE (draft/score/publish a post — the default) continues in
THIS file below. For the other three, Read the mapped reference and follow it:

| Mode | Trigger | Reference |
|---|---|---|
| feed engage | comment on others' posts in my home feed | `references/feed-comments.md` |
| reply | reply to comments on MY OWN posts | `references/reply-comments.md` |
| check replies | replies to comments I left on OTHERS' posts ("any replies to my comments?", "did <author> reply to me?") | `references/check-comment-replies.md` |

If it's genuinely ambiguous which mode is wanted, ask the user. Note the reply/check-replies
split: comments on YOUR posts → reply mode; replies to YOUR comments elsewhere → check
replies. "Check my LinkedIn comments" with no other context should cover BOTH.

# LinkedIn Post Creator

Writes data-driven LinkedIn posts on three topic pillars, grounded in real sources
scraped from authoritative sites. Each post follows proven LinkedIn engagement patterns.

## Step 1 — Detect Topic Type

Match the user's request to one of three pillars:

| Pillar | Trigger phrases | Slug |
|--------|----------------|------|
| **SEO + AI** | "SEO", "search", "Google AI", "AI Overviews", "search landscape", "ranking" | `seo-ai` |
| **AI in Daily Life** | "AI daily", "AI productivity", "AI tools I use", "day to day AI", "everyday AI" | `ai-life` |
| **Vibe Coding** | "vibe coding", "AI coding", "cursor", "claude code", "copilot", "AI developer", "build with AI" | `vibe-coding` |

If unclear, ask the user: _"Which topic: (1) SEO + AI changes, (2) AI in your daily life, or (3) Vibe Coding?"_

Read `references/source-domains.md` for authoritative sources per pillar.

## Step 1b — Image post, external image, or text-only? (decide before writing)

Every write-mode post takes one of **three** formats. Settle this up front so the
publish step knows which path to take:

1. **Text-only** — just the post. Triggers: "text only", "no image", "just text".
2. **Auto-generated image** — one free Pollinations image generated in this flow
   (Step 7). Triggers: "with an image", "with a visual", "add an image/picture/graphic",
   "image post".
3. **External image (bring-your-own)** — the user generates the image themselves in an
   external tool (Nano Banana / Gemini, Midjourney, DALL-E, etc.); this flow supplies a
   ready-to-paste **image-generation prompt alongside the post**, then publishes the
   image the user brings back (Step 8). Triggers: "give me a prompt for the image",
   "I'll make the image myself", "nanobanana/midjourney prompt", "I'll generate the
   image and give it to you".

- **Unspecified → ASK the user** (one quick question, before researching/writing):
  > "How do you want this: (1) **text-only**, (2) **image post** — I generate a free
  > visual, or (3) **I write you an image-gen prompt** (Nano Banana etc.) and you bring
  > the image back for me to post?"

Remember the choice. For formats 2 and 3 the image work happens **after** the post text
is approved (the prompt is derived from the final text) — except that in format 3 the
image prompt is also **presented together with the post draft** (see Step 5).
Writing/research below is identical either way; only the publish step branches.

## Step 2a — Novelty check (MANDATORY, before any research)

Repetition kills reach. Observed on this account: three same-topic posts in one
week earned 52 → 33 → 25 impressions — each repeat did worse, and account-wide
distribution stayed cold.

- Read `data/posted-log.jsonl` (one JSON object per published post: date, pillar,
  hook, key_stats).
- If the requested topic/angle overlaps a post from the **last 14 days**, or reuses
  any `key_stats` entry from the **last 30 days**, STOP and tell the user which
  post it collides with. Propose a different pillar or a genuinely new angle
  (new study, new dataset, opposite take). Proceed on the overlapping topic only
  if the user explicitly insists after being told.
- Hook patterns count too: don't reuse the same hook structure + headline statistic
  combination that's already in the ledger.

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
3. **Image-generation prompt** (external-image posts only) — the ready-to-paste prompt
   from Step 8a, in its own copyable code block, with 2-3 bullets explaining the visual
   choices. If the post text changes in revision, regenerate the prompt to match.
4. **Engagement analysis** — the scorecard
5. **Offer a rewrite** — "Want me to try a different hook / shorter version / more personal angle?"

## Approval Gate (mandatory)

After presenting the post, always ask:

> "Ready to post this, or would you like any changes first?"

Do not treat the task as complete until the user explicitly approves the post.
Never simulate posting, schedule it, or mark it ready-to-go without a clear "yes" or "approved" from the user.

**After approval, route by the Step 1b decision:**
- **Text-only post → Step 6** below.
- **Auto-generated image post → Step 7** (generate + preview the image, get a second
  approval on the image, then publish text + image in one call). Do **not** also run
  Step 6 — Step 7 does the publishing.
- **External image post → Step 8** (the image prompt was already presented in Step 5;
  wait for the user to bring the image back, locate it on disk, then publish text +
  image in one call). Do **not** also run Step 6 or 7.

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

## Step 8 — External image posts (when Step 1b chose bring-your-own image)

Run this **instead of Steps 6/7**. The user generates the image in an external tool
(Nano Banana / Gemini, Midjourney, DALL-E, …) from a prompt this flow writes, then
brings the image back for publishing.

### 8a. Write the image-generation prompt (presented WITH the post in Step 5)
Derive one detailed prompt from the post's core idea. Unlike Step 7a's free model,
external tools (especially Nano Banana) handle **photorealism** well, so:
- Default to a **realistic, cinematic/editorial** style unless the user asks otherwise.
- Encode the post's central contrast as a single visual scene (e.g. "AI answer box
  glowing, clicks chart falling").
- Faces: prefer **over-the-shoulder / silhouette** framing — realistic without
  identity weirdness. Limit readable screen text to **one short label**; dense UI
  text still renders messy.
- Specify palette, lighting, aesthetic reference ("Bloomberg/Wired-style"), and a
  **landscape 1200×627 composition** (LinkedIn's ideal feed ratio; offer 1080×1080
  square as the alternative).
- Present the prompt in its own copyable code block + 2-3 bullets on the visual
  choices, and offer one alternative (more conceptual/metaphorical) angle.
- If the post text is revised afterwards, regenerate the prompt to match.

### 8b. Receive the image back
The user returns with the image either as a **file path** or **pasted inline** in chat.
A pasted image is viewable but NOT uploadable — the publish script needs a file on disk.
- If they gave a path → use it.
- If they pasted the image only → find the file: search likely folders for recent images
  (`find ~/Downloads ~/Desktop ~/Documents -maxdepth 2 \( -iname "*.png" -o -iname
  "*.jpg" -o -iname "*.jpeg" \) -mmin -180 -exec ls -lat {} + | head -20`). Externally
  generated files often have telltale names (`Gemini_Generated_Image_*`, `DALL·E*`).
- **Verify before publishing:** Read the candidate file and confirm it visually matches
  the pasted image; check it's PNG/JPEG and **< 5 MB**. If no confident match, ask the
  user for the path — never upload an unverified guess.

### 8c. Publish with the image
Identical mechanics to Step 7c — post text via stdin, image via `--image`:
```
python3 scripts/linkedin_post.py --image "<path>" --alt-text "<alt text>" < /path/to/approved_post.txt
```
- Write a descriptive `--alt-text` from the image content (don't rely on the fallback).
- Success = final JSON with `"status":"success"`, `http_status` 201, and a `post_id` —
  report the `post_id` and the post URL (`https://www.linkedin.com/feed/update/<post_id>`).
- On any failure: STOP, report the exact `detail`/`http_status`, do NOT claim published.

## Step 9 — After EVERY successful publish (Steps 6, 7c, 8c)

### 9a. Verify the live text
Fetch the post URL (`https://www.linkedin.com/feed/update/<post_id>/` — WebFetch, or
the logged-in browser if available) and confirm the live text matches the approved
text **end to end**, especially the final lines. The script escapes LinkedIn's
"little text format" reserved chars (`( ) [ ] < > @ * _ ~ |`) since v1.3.0 — an
unescaped reserved char is the known cause of silent truncation. If the live post is
truncated or mangled, report it immediately with the diff; never leave the user to
discover it. The user should NOT need to hand-edit a live post (edits shortly after
publishing are anecdotally linked to dampened distribution — unverified, but avoid).

### 9b. Log the post
Append one line to `data/posted-log.jsonl`:
```json
{"date":"YYYY-MM-DD","post_id":"urn:li:share:...","pillar":"seo-ai|ai-life|vibe-coding","format":"text|image|external-image","hook":"<first line>","key_stats":["<each headline stat used>"]}
```
This ledger feeds the Step 2a novelty check — skipping it re-enables the
duplicate-post reach collapse.

### 9c. Engagement routine (reach depends on this, not just the post)
LinkedIn distributes in waves: a small follower sample first, wider only if that
sample engages (comments ≫ likes). A post with zero conversation stalls. After
confirming the post is live, offer to run:
1. **Reply mode** over the next few hours — answer every comment on the new post
   fast (first ~2 hours matter most).
2. **Feed engage mode** — 20-30 min commenting on 5-10 relevant posts from larger
   accounts in the niche; this warms account-level distribution beyond this one post.
Also remind: no second post the same day; 2-3 distinct-topic posts/week beats
daily repeats.
