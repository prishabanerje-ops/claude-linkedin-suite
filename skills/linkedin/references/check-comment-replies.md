---
name: linkedin-check-comment-replies
description: >
  Check for replies to comments YOU left on OTHER people's LinkedIn posts, and
  answer them. Reads the outbound-comments ledger (data/comments-log.jsonl),
  revisits each thread in a logged-in browser (Chrome DevTools MCP), checks the
  notifications page for "replied to your comment" items, surfaces who replied
  and what they said, drafts replies in your voice, and posts each only after
  your explicit approval. Use for "any replies to my comments?", "did Lydia
  reply to me?", "check replies to the comments I left", or after a feed-engage
  run. For comments on your OWN posts, use references/reply-comments.md instead.
metadata:
  author: Aakash Srivastava
  version: "1.0.0"
  category: social
---

# Check Replies to Your Outbound Comments

Feed-engage mode plants comments on other people's posts; this mode harvests the
conversations they start. A fast, substantive reply to an author who answered you is
worth more visibility than the original comment.

## Why this exists

LinkedIn notifies the user natively, but nothing in this skill watched those threads —
"check my LinkedIn comments" (reply mode) only covers the user's OWN posts. This mode
covers the outbound direction using the ledger written by feed-engage mode.

## Critical: use the browser, NOT the API

Same as the other comment modes: the API cannot read comments or notifications. Use
Chrome DevTools MCP on a logged-in profile. No login → STOP and tell the user.

## Step 0 — Confirm a logged-in session

Same as `feed-comments.md` Step 0: find/select the linkedin.com tab or open
`https://www.linkedin.com/feed/`, verify nav text (Home / My Network / Messaging /
Notifications), STOP on a sign-in wall.

## Step 1 — Read the ledger

Read `data/comments-log.jsonl` (one JSON object per outbound comment: date, post_urn,
post_author, comment_first_line, asked_question, status).

- Check every entry with `status: "open"`.
- Entries older than ~30 days: skip and (with user OK) mark `status: "stale"` — threads
  that old rarely produce replies worth chasing.
- Ledger missing or empty → fall back to Step 2 (notifications) only, and tell the user
  the ledger had nothing to sweep.

## Step 2 — Check notifications (fast signal)

Open `https://www.linkedin.com/notifications/?filter=all`. Read the page (innerText
usually works here; fall back to screenshots if it comes back empty — same virtualized-UI
caveat as the feed). Collect items matching /replied to your comment|reacted to your
comment|mentioned you/i with who + which post. This catches replies on threads that
never made it into the ledger.

## Step 3 — Sweep the ledger threads (ground truth)

For each open ledger entry, open `https://www.linkedin.com/feed/update/<post_urn>/`,
expand replies (click "see more / more replies / load more" buttons, scroll), then
locate YOUR comment by matching the first ~60 chars of `comment_first_line` in
`main.innerText` and read what sits under it.

For each reply found, capture: who (name + headline), what they said, and whether it's
addressed to you (vs. a general reply in the same sub-thread). Note especially replies
from the POST AUTHOR — highest priority, they answered your question.

Present a readable summary: per thread — author, their reply, your original comment,
priority (author-reply > question-back > substantive > pleasantry).

## Step 4 — Draft replies and post them (per-reply approval)

Draft a reply for each item worth answering, in the user's voice (see Voice in
`feed-comments.md`): 1-4 short lines, no hashtags, engage their specific point, add one
concrete thing, questions back are welcome. Never fabricate data.

**Formatting — single line breaks ONLY.** Comments render every newline as a
full-height paragraph block; a blank line becomes a tall empty row. Single `\n` between
lines, or one compact paragraph.

**Approval gate:** show their reply + your draft, ask "Post this, edit it, or skip?".
Only an explicit yes submits.

To post: on the thread page, click the **Reply** control on the relevant comment (find
it by accessible label from a fresh snapshot; the comment box class is
`comments-comment-box`), focus the `contenteditable` editor, insert the approved text
(`document.execCommand('insertText', ...)` works), click the submit button
(`comments-comment-box__submit-button`). **Verify** by re-reading `main.innerText` and
confirming your reply text appears; report the permalink.

## Step 5 — Update the ledger

- Replied → set that entry's `status` to `"replied"` and add `last_checked` (YYYY-MM-DD).
- Checked, nothing new → keep `status: "open"`, update `last_checked`.
- Conversation clearly finished → `status: "closed"`.

## Safety

Same rules as the other modes: explicit approval before every reply, never fabricate
data, STOP and report on any tool failure, always verify a posted reply in the live
thread.
