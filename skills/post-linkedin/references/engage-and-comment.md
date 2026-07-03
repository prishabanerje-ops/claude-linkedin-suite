# LinkedIn Engagement — Reply to Comments & Comment on the Feed

This is the **engage mode** of the `post-linkedin` skill. Where the main skill *writes*
new posts, this workflow *interacts* with existing LinkedIn content on the user's behalf:

1. **Check comments** on the user's own recent posts.
2. **Reply** to those comments (in the user's voice, with per-reply approval).
3. **Scan the home feed** and **comment on 2-3 relevant posts**.

Read this whole file before acting. It encodes lessons that are easy to get wrong and
expensive to rediscover.

---

## Critical: use the browser, NOT the post API

The post-creation script (`scripts/linkedin_post.py`) talks to LinkedIn's official API,
which **can only create posts**. It cannot read the feed, read comments, or post
comments/replies. The LinkedIn MCP tools (`linkedin_create_post`, `linkedin_get_user_info`,
etc.) are likewise post/profile only.

**Engagement must go through browser automation** using the Chrome DevTools MCP tools,
driving a Chrome profile that is already logged into LinkedIn. If those tools are not
available, or no logged-in session exists, **stop and tell the user** — do not pretend
to engage and never fabricate that a comment was posted.

Chrome DevTools MCP tools you'll use: `list_pages`, `new_page`, `navigate_page`,
`select_page`, `evaluate_script`, `take_screenshot`, `take_snapshot`, `click`, `fill`,
`wait_for`.

---

## Hard-won DOM lessons (read before writing any selector)

LinkedIn ships two *different* front-ends, and they behave differently:

- **Post-detail pages and the profile activity page still use the older, readable
  markup.** Classic selectors like `.feed-shared-update-v2` and
  `[data-urn*="urn:li:activity"]` work there, and `main.innerText` returns the full
  post + comment text cleanly. **This is the reliable way to READ comments.**
- **The home feed (`/feed/`) uses a newer UI with OBFUSCATED, hashed class names**
  (e.g. `_02cbf902`, `f7efdb6d`) and `componentkey` attributes. There are **no**
  `feed-shared-*` classes and **no** `urn:li:activity` attributes in that DOM, and the
  feed is **virtualized** so `innerText`/`textContent` returns almost nothing even
  though the page looks full of posts. **Do not rely on text extraction on the feed.**
  Use `take_screenshot` to READ the feed, then open each candidate's permalink to read
  it properly on its detail page.

Other realities of the session:

- **`list_pages` indices REORDER between calls.** Never reuse a remembered page index.
  Always call `list_pages`, find the LinkedIn tab by URL substring, and `select_page`
  that id right before you act.
- **The MCP connection drops intermittently** (`MCP error -32000: Connection closed`,
  or `Could not find DevToolsActivePort`). On any drop: retry `list_pages` once,
  re-select the LinkedIn tab by URL, and continue. Chrome occasionally restarts and
  closes tabs — re-open the URL you need.
- **First navigation to `/feed/` may auto-redirect to the profile** (`/in/<vanity>/`).
  That's normal and actually confirms you're logged in.
- **Login detection via CSS classes is unreliable** (classes change). Detect login by
  reading the nav text instead — a logged-in page's `document.body.innerText` contains
  `Home`, `My Network`, `Jobs`, `Messaging`, `Notifications`, `Me`.

---

## Key URLs

| Purpose | URL |
|---------|-----|
| Home feed | `https://www.linkedin.com/feed/` |
| User's post history | `https://www.linkedin.com/in/<vanity>/recent-activity/all/` |
| User's posts only | `https://www.linkedin.com/in/<vanity>/recent-activity/shares/` |
| A single post + its comments | `https://www.linkedin.com/feed/update/urn:li:activity:<ACTIVITY_ID>/` |

Get `<vanity>` from the profile redirect (e.g. `aakash-srivastava`). Get `<ACTIVITY_ID>`
from the `data-urn` on the activity page (it looks like `urn:li:activity:7474759971167961089`).

---

## Step 0 — Confirm a logged-in session

`list_pages`. If a `linkedin.com` tab exists, `select_page` it; otherwise `new_page` to
`https://www.linkedin.com/feed/` (expect a ~10s timeout — LinkedIn is slow; that's not a
failure, just re-`list_pages` and select the tab). Then:

```js
() => {
  const t = document.body.innerText;
  return { url: location.href,
           loggedIn: ['Home','My Network','Messaging','Notifications'].every(s => t.includes(s)) };
}
```

If not logged in (a sign-in wall), **stop** and ask the user to log in — you cannot do
their password/2FA.

---

## Step 1 — Check all comments on the user's posts

Navigate to `…/recent-activity/all/` and extract the user's recent posts. The activity
page uses the older markup, so this works:

```js
() => {
  const out = [];
  const seen = new Set();
  document.querySelectorAll('.feed-shared-update-v2, [data-urn*="urn:li:activity"]').forEach(el => {
    const urn = el.getAttribute('data-urn')
      || el.querySelector('[data-urn]')?.getAttribute('data-urn') || '';
    if (urn && seen.has(urn)) return; if (urn) seen.add(urn);
    const text = (el.querySelector('.update-components-text, .feed-shared-update-v2__description')?.innerText || '').trim().slice(0, 400);
    const counts = el.querySelector('.social-details-social-counts')?.innerText.replace(/\s+/g,' ').trim() || '';
    if (text || counts) out.push({ urn, text, counts });
  });
  return out;
}
```

The `counts` string reveals how many comments each post has (e.g. `"… 3 comments"`).
For every post **that has comments**, open its detail page
(`/feed/update/<urn>/`) and read the full thread:

```js
async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(2500);
  // expand truncated comments/replies
  for (let r = 0; r < 3; r++) {
    document.querySelectorAll('button, a[role="button"]').forEach(b => {
      if (/see more|more repl|previous repl|load more|view .* comment/i.test(b.innerText || '')) {
        try { b.click(); } catch {}
      }
    });
    await sleep(1200); window.scrollBy(0, 800); await sleep(500);
  }
  return document.querySelector('main').innerText;
}
```

Parse the thread into: each commenter (name + headline), their comment text, and whether
the **user has already replied** beneath it. **Prioritize comments the user has not yet
replied to** — those are the open conversations worth answering. Present the threads to
the user as a readable summary (who said what, which are unanswered).

---

## Step 2 — Reply to comments (per-reply approval)

For each comment worth replying to, **draft a reply in the user's voice** (see *Voice*
below). Then run the **approval gate**:

> Show the original comment + your draft reply. Ask: *"Post this reply, edit it, or skip?"*
> Only after an explicit **yes/approved** do you submit. Never auto-submit.

To post a reply, the markup may be obfuscated, so don't hard-code selectors — take a
fresh `take_snapshot`, locate the comment's **Reply** control by its accessible label,
`click` it, then `fill` the comment editor with the approved text and submit (the editor
is a `contenteditable`; after filling, click the **Post**/**Reply** submit button found
in the latest snapshot, or press Enter only if the box is single-line — it usually isn't,
so prefer the button).

**Verify before claiming success:** re-read `main.innerText` and confirm your reply text
now appears in the thread. Report the post permalink as proof. If you cannot reliably
find the editor/submit button after a couple of tries, **fall back**: type the text into
the box and ask the user to click Post themselves — and say clearly that you did not
submit it.

---

## Step 3 — Comment on 2-3 relevant feed posts

Navigate to `/feed/`. Because the feed is obfuscated + virtualized, **read it with
screenshots**, not text extraction:

1. Scroll in steps (`window.scrollBy(0, ~1000)` with short waits) and `take_screenshot`
   between scrolls to capture a run of posts. Note each candidate's **author + headline,
   the gist of the post, rough recency, and visible engagement**.
2. To open a candidate properly, get its **permalink**: click the post's timestamp (it
   links to `/feed/update/urn:li:activity:<id>/`), or use the post's "**…**" menu →
   **Copy link to post**. Opening the detail page gives you clean text + existing comments.

**Relevance filter** (the user's chosen criteria — apply all):

- **On-topic with the user's pillars:** SEO / AI-search / AI Overviews / GEO; AI in daily
  professional work; vibe coding & AI-assisted development. Skip off-topic posts.
- **Recent or already gaining traction:** favor posts from roughly the last 24-48h, or
  ones already collecting reactions/comments — an early, substantive comment there earns
  more visibility.
- **Avoid promotional / political:** skip overt sales pitches, "we're hiring" spam,
  engagement-bait, and politically charged posts. Engage only where there's genuine
  professional discussion.

Surface a **shortlist of ~5 candidates** with one-line summaries and let the user pick
the **2-3** to comment on (this is also the approval gate for *which* posts to touch).

For each chosen post: open its detail page, **read the full text and the existing
comments first** (so your comment adds something new and doesn't echo what others already
said), draft a comment in the user's voice, run the per-comment approval gate, then post
+ verify exactly as in Step 2.

---

## Voice & comment quality

Match the user's own voice. Read 3-5 of their recent posts from the activity page to
calibrate. Observed characteristics (Aakash's style): short, punchy lines; data-driven;
arrows (`→`) for lists; ends with a specific question; no corporate jargon; no
"game-changer"/"revolutionize" filler; at most 1-2 emojis. See `references/post-formats.md`
for tone, and `references/source-domains.md` if you need a credible stat to back a point.

Replies and comments are **much shorter than posts** — usually **1-4 short lines**, and
**no hashtags**.

A strong reply/comment:
- **Engages the specific point** the other person made (quote or paraphrase it), not a
  generic "Great post!".
- **Adds one concrete thing** — a data point, a counter-example, a sharper framing, or a
  lived observation. Bring something the thread didn't already have.
- Often **ends with a specific question** back to the author to keep the conversation
  going (good for the user's visibility), but don't force it on every comment.
- Sounds like a peer talking shop — never sycophantic, never salesy.

---

## Safety & etiquette (non-negotiable)

- **Explicit per-item approval before every post.** This mirrors the main skill's
  mandatory approval gate. When in doubt, draft and ask.
- **Cap at ~2-3 feed comments per run.** Mass/rapid commenting trips LinkedIn's
  automation defenses and reads as spam.
- **Never fabricate data** in a comment. Only cite numbers you can support (from the
  user's own posts, the source-domains references, or numbers the user supplied).
- **On any tool failure** (connection drop that won't recover, navigation error, missing
  login), STOP and report exactly what failed and what's missing — do not proceed on
  assumed state and never claim a comment posted when it didn't.
- **Always verify** a posted comment/reply by re-reading the thread, and report its
  permalink as the confirmation.
