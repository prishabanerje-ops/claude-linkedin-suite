---
name: post-linkedin-feed-comments
description: >
  Scan your LinkedIn HOME FEED and comment on 2-3 relevant posts. Drives a
  logged-in browser (Chrome DevTools MCP) to read your feed via screenshots,
  filter to on-topic posts (SEO / AI-search / GEO, AI at work, vibe coding &
  AI-assisted dev) that are recent or gaining traction and not promotional or
  political, surface a shortlist for you to pick from, draft comments in your
  voice, and post each only after your explicit approval. Use this whenever the
  user wants to engage with OTHER people's posts in their feed — e.g. "comment
  on relevant posts in my feed", "engage with my LinkedIn feed", "find posts in
  my feed worth commenting on", "scan my feed and comment", or the slash command
  /post-linkedin-feed-comments. For replying to comments on the user's OWN posts,
  use post-linkedin-posts-comment instead.
user-invokable: true
argument-hint: "[optional: topic/filter, or how many posts]"
metadata:
  author: Aakash Srivastava
  version: "1.0.0"
  category: social
---

# Comment on Relevant Posts in Your LinkedIn Feed

Scans your home feed in a logged-in browser, finds the few posts genuinely worth
engaging with, drafts comments in your voice, and posts each only **after you approve
it**. Default cap: **2-3 comments per run** (more than that trips LinkedIn's automation
defenses and reads as spam).

This skill is self-contained. For the complete background — DOM quirks, voice guide, and
safety rules — read `~/.claude/skills/post-linkedin/references/engage-and-comment.md`
(Step 3, Voice, Safety). The essentials are inline below.

## Critical: use the browser, NOT the API

LinkedIn's post API (and the `linkedin_*` MCP tools) can only **create posts** — they
cannot read the feed or post comments. This work must go through **browser automation**
(Chrome DevTools MCP) on a Chrome profile already logged into LinkedIn. If those tools
aren't available or no logged-in session exists, **stop and tell the user** — never
fabricate that a comment was posted.

## Step 0 — Confirm a logged-in session

`list_pages` → if a `linkedin.com` tab exists, `select_page` it (indices **reorder**
between calls, so match by URL, never a remembered index); otherwise `new_page` to
`https://www.linkedin.com/feed/` (a ~10s timeout is normal — re-`list_pages` and select).
Confirm login by reading nav text:

```js
() => { const t = document.body.innerText;
  return ['Home','My Network','Messaging','Notifications'].every(s => t.includes(s)); }
```

If a sign-in wall shows, **stop** — you can't do the user's password/2FA.

## Step 1 — Read the feed with SCREENSHOTS (not text extraction)

The home feed (`/feed/`) uses a newer UI with **obfuscated, hashed class names** and is
**virtualized**, so `innerText`/`textContent` returns almost nothing even though the page
looks full. Do **not** rely on text extraction or old `.feed-shared-*` selectors here.

Instead: scroll in steps (`window.scrollBy(0, ~1000)` with short waits) and
`take_screenshot` between scrolls to read a run of posts. For each candidate note the
**author + headline, the gist, rough recency, and visible engagement**, and capture its
**permalink** — click the post's timestamp (links to
`/feed/update/urn:li:activity:<id>/`) or use the post's "**…**" menu → **Copy link to
post**. Opening that permalink later gives you clean text + existing comments.

## Step 2 — Filter for relevance, then let the user pick

Keep a candidate only if it passes all of:

- **On-topic with the pillars:** SEO / AI-search / AI Overviews / GEO; AI in daily
  professional work; vibe coding & AI-assisted development.
- **Recent or gaining traction:** roughly the last 24-48h, or already collecting
  reactions/comments (an early, substantive comment there earns more visibility).
- **Not promotional / political:** skip sales pitches, "we're hiring" spam,
  engagement-bait, and politically charged posts. Engage only where there's genuine
  professional discussion.

Surface a **shortlist of ~5** candidates with one-line summaries and let the user pick
the **2-3** to comment on. (This doubles as the approval gate for *which* posts to touch.)
Honor any topic/count hint passed as an argument.

## Step 3 — Draft comments and post them (per-comment approval)

For each chosen post: open its **permalink**, **read the full text and existing comments
first** (so your comment adds something new and doesn't echo others), then draft a comment
in the user's voice.

**Approval gate:** show the post gist + your draft and ask *"Post this, edit it, or
skip?"*. Only after an explicit **yes** do you submit. Never auto-submit.

To post: take a fresh `take_snapshot`, find the comment box / **Comment** control by its
accessible label, `click`/`fill` the editor (`contenteditable`) with the approved text,
then click the **Post** submit button from the latest snapshot. **Verify** by re-reading
`main.innerText` and confirming your text appears; report the post permalink as proof. If
you can't reliably find the editor/submit after a couple tries, **fall back**: type the
text into the box and ask the user to click Post — and say clearly you didn't submit.

## Voice

Match the user's own style (read 3-5 of their recent posts to calibrate): short punchy
lines, data-driven, arrows (`→`) for lists, ends with a specific question, no corporate
jargon, 1-2 emojis max. Comments are **1-4 short lines** and carry **no hashtags**. A
strong comment **engages the specific point** the author made (not "Great post!"), **adds
one concrete thing** (a data point, counter-example, sharper framing, or lived
observation), and often **ends with a question** to keep the conversation going. Sound
like a peer talking shop — never sycophantic, never salesy. See
`post-linkedin/references/post-formats.md` for tone and
`post-linkedin/references/source-domains.md` if you need a credible stat.

## Safety

- **Explicit approval before every comment**, and the user picks which posts.
- **Cap at ~2-3 comments per run** — never mass-comment.
- **Never fabricate data** — only cite numbers you can support.
- **On any tool failure** (connection drop, navigation error, no login), STOP and report
  exactly what failed; do not proceed on assumed state or claim a comment posted.
- **Always verify** a posted comment by re-reading the thread; report its permalink.
