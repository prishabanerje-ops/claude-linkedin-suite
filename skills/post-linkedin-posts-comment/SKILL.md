---
name: post-linkedin-posts-comment
description: >
  Read and reply to the comments on YOUR OWN LinkedIn posts. Drives a logged-in
  browser (Chrome DevTools MCP) to open your recent posts, pull every comment
  thread, flag the comments you haven't answered yet, draft replies in your
  voice, and post each one only after your explicit approval. Use this whenever
  the user wants to deal with comments on their own posts — e.g. "check the
  comments on my LinkedIn posts", "reply to my LinkedIn comments", "who
  commented on my latest post", "draft replies to the comments on my post", or
  the slash command /post-linkedin-posts-comment. This is for the user's OWN
  posts; use post-linkedin-feed-comments for commenting on other people's posts
  in the home feed.
user-invokable: true
argument-hint: "[optional: a specific post URL, or 'latest']"
metadata:
  author: Aakash Srivastava
  version: "1.0.0"
  category: social
---

# Reply to Comments on Your LinkedIn Posts

Opens your own recent LinkedIn posts in a logged-in browser, reads every comment
thread, highlights comments you haven't replied to, drafts replies in your voice,
and posts each only **after you approve it**.

This skill is self-contained. For the complete background — DOM quirks, URL formats,
voice guide, and safety rules — read
`~/.claude/skills/post-linkedin/references/engage-and-comment.md` (Steps 0-2, Voice,
Safety). The essentials are inline below.

## Critical: use the browser, NOT the API

LinkedIn's post API (and the `linkedin_*` MCP tools) can only **create posts** — they
cannot read or post comments. This work must go through **browser automation** (Chrome
DevTools MCP) on a Chrome profile already logged into LinkedIn. If those tools aren't
available or no logged-in session exists, **stop and tell the user** — never fabricate
that a reply was posted.

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

## Step 1 — Pull the comments on your posts

If the user gave a specific post URL, open it directly. Otherwise go to the activity
page: `https://www.linkedin.com/in/<vanity>/recent-activity/all/` (get `<vanity>` from
the profile redirect, e.g. `aakash-srivastava`). The activity page uses the older,
readable markup, so this extraction works:

```js
() => { const out=[], seen=new Set();
  document.querySelectorAll('.feed-shared-update-v2, [data-urn*="urn:li:activity"]').forEach(el => {
    const urn = el.getAttribute('data-urn') || el.querySelector('[data-urn]')?.getAttribute('data-urn') || '';
    if (urn && seen.has(urn)) return; if (urn) seen.add(urn);
    const text = (el.querySelector('.update-components-text, .feed-shared-update-v2__description')?.innerText||'').trim().slice(0,200);
    const counts = el.querySelector('.social-details-social-counts')?.innerText.replace(/\s+/g,' ').trim()||'';
    if (text||counts) out.push({urn, text, counts}); });
  return out; }
```

The `counts` string shows how many comments each post has. For every post **with
comments**, open its detail page `https://www.linkedin.com/feed/update/<urn>/` and read
the full thread (post-detail pages render comment text cleanly via `main.innerText`),
expanding truncated replies first:

```js
async () => { const sleep=ms=>new Promise(r=>setTimeout(r,ms)); await sleep(2500);
  for (let r=0;r<3;r++){ document.querySelectorAll('button,a[role="button"]').forEach(b=>{
    if(/see more|more repl|previous repl|load more|view .* comment/i.test(b.innerText||'')){try{b.click();}catch{}}});
    await sleep(1200); window.scrollBy(0,800); await sleep(500);} 
  return document.querySelector('main').innerText; }
```

Parse each thread into: commenter (name + headline), their comment, and whether **you've
already replied** beneath it. **Prioritize the unanswered ones** — those are the open
conversations. Present a readable summary to the user (who said what, which are open).

## Step 2 — Draft replies and post them (per-reply approval)

Draft a reply for each comment worth answering, in the user's voice (see *Voice*).

**Approval gate:** show the original comment + your draft and ask *"Post this, edit it,
or skip?"*. Only after an explicit **yes** do you submit. Never auto-submit.

To post: the markup may be obfuscated, so don't hard-code selectors — take a fresh
`take_snapshot`, find that comment's **Reply** control by its accessible label, `click`
it, `fill` the editor (`contenteditable`) with the approved text, then click the
**Post/Reply** submit button from the latest snapshot. **Verify** by re-reading
`main.innerText` and confirming your text appears; report the post permalink as proof.
If you can't reliably find the editor/submit after a couple tries, **fall back**: type
the text into the box and ask the user to click Post — and say clearly you didn't submit.

## Voice

Match the user's own style (read 3-5 recent posts to calibrate): short punchy lines,
data-driven, arrows (`→`) for lists, ends with a specific question, no corporate jargon,
1-2 emojis max. Replies are **1-4 short lines** and carry **no hashtags**. A strong reply
**engages the specific point** made (not "Great post!"), **adds one concrete thing** (a
data point, counter-example, sharper framing), and often **ends with a question** back to
keep the thread alive. Never sycophantic. See `post-linkedin/references/post-formats.md`
for tone.

## Safety

- **Explicit approval before every reply.** When in doubt, draft and ask.
- **Never fabricate data** — only cite numbers you can support.
- **On any tool failure** (connection drop, navigation error, no login), STOP and report
  exactly what failed; do not proceed on assumed state or claim a reply posted.
- **Always verify** a posted reply by re-reading the thread; report its permalink.
