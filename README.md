# claude-linkedin-suite

Portable **Claude Code** skill for LinkedIn — write & publish posts, comment on
your feed, reply to comments on your own posts, and track replies to comments
you left elsewhere. Clone onto any machine and run one command to get the
`/linkedin` hub working.

## What's inside

```
skills/
  linkedin/                        Unified LinkedIn hub — four modes, one skill
    SKILL.md                       WRITE mode: research, draft, score, publish (text / auto-image / bring-your-own-image)
    references/
      feed-comments.md             FEED ENGAGE mode: comment on 2–3 relevant posts in your home feed
      reply-comments.md            REPLY mode: reply to comments on your own posts
      check-comment-replies.md     CHECK REPLIES mode: find & answer replies to comments you left on others' posts
      engage-and-comment.md        Shared DOM/voice/safety background for the three comment modes
      post-formats.md              Hook patterns, storytelling templates, CTA/hashtag banks
      source-domains.md            Authoritative sources per content pillar
    scripts/                       linkedin_post.py, linkedin_image.py (+ tests)
    data/                          posted-log.jsonl (anti-repetition ledger), comments-log.jsonl (outbound-comment ledger)
    evals/evals.json
config/
  linkedin-api.env.example         Credentials template (copy to ~/.config/linkedin-api.env)
docs/
  2026-07-03-linkedin-reach-optimization-design.md   Roadmap PRD (reach optimization)
  reach-scorecard.html            Account reach diagnostic (private analytics)
install.sh                        One-command installer
requirements.txt                  (stdlib only today — nothing to pip install)
```

## One-command install (new machine)

This is a **private** repo, so use `gh` (which handles auth). On the new machine,
make sure the [GitHub CLI](https://cli.github.com) is installed and signed in as
the account that owns this repo (`gh auth login`), then:

```bash
gh repo clone claude-linkedin-suite ~/claude-linkedin-suite && bash ~/claude-linkedin-suite/install.sh
```

(`gh repo clone <name>` with no owner resolves to *your own* repo, so this works
regardless of your username.) Prefer SSH/git instead? Equivalent:

```bash
git clone git@github.com:<your-github-username>/claude-linkedin-suite.git ~/claude-linkedin-suite && bash ~/claude-linkedin-suite/install.sh
```

The installer:
1. Copies the skill into `~/.claude/skills/linkedin` (backing up any existing copy).
2. Creates `~/.config/linkedin-api.env` from the template if it doesn't exist.
3. Confirms Python 3 + the stdlib are present (no pip install needed).

## Credentials (required for publishing)

Edit `~/.config/linkedin-api.env` and fill in:

| Key | What it is |
|-----|-----------|
| `LINKEDIN_ACCESS_TOKEN` | OAuth member token with the `w_member_social` scope |
| `LINKEDIN_PERSON_ID` | Your person URN id (the part after `urn:li:person:`; the `sub` from `/v2/userinfo`) |

Your token lives **only** on your machine in that file — it is git-ignored and
never committed. See `config/linkedin-api.env.example` for how to obtain each.

## The modes

All four live under one skill — `/linkedin`. Say what you want and it routes itself
(or ask explicitly):

| Mode | Trigger | Does |
|---|---|---|
| **write** (default) | "write me a LinkedIn post about X" | Research-backed post on SEO+AI / AI-in-daily-life / vibe-coding pillars, novelty check against `data/posted-log.jsonl`, engagement scorecard, then publishes text, one auto-generated image, or a bring-your-own image (with an image-gen prompt handed to you) via the API. |
| **feed engage** | "comment on relevant posts in my feed" | Drives your logged-in Chrome to scan the home feed and comment on 2–3 relevant posts (per-item approval); logs each to `data/comments-log.jsonl`. |
| **reply** | "check the comments on my LinkedIn posts" | Drives your logged-in Chrome to read and reply to comments on your own posts (per-item approval). |
| **check replies** | "any replies to my comments?" | Sweeps `data/comments-log.jsonl` + your notifications page for replies to comments you left on *others'* posts, and answers them (per-item approval). |

Every `/linkedin` invocation opens with a one-line reminder if any outbound
comment thread is still open, so a question you asked an author never goes
unanswered.

**Publishing** (write mode) uses LinkedIn's API + your token — no browser needed.
**Comment modes** (feed engage / reply / check replies) use **browser automation**
(Chrome DevTools MCP) on a Chrome profile already **signed into LinkedIn** — the
API can't read feeds, comments, or notifications.

## Requirements

- **Python 3.9+** (standard library only for the current skills).
- **Claude Code** with the skill in `~/.claude/skills/linkedin` (the installer handles this). Restart Claude Code after installing so it discovers it.
- For the comment modes: **Chrome** signed into LinkedIn + the **Chrome DevTools MCP** available in your Claude Code session.

## Updating

Re-run the one-command install — it backs up your existing skill copy to
`~/.claude/skills/.backup-<timestamp>/` before overwriting, and leaves your
credentials file untouched.

## Security

- **No secrets in this repo.** The access token stays in `~/.config/linkedin-api.env` (git-ignored).
- `docs/reach-scorecard.html`, the PRD, and `skills/linkedin/data/*.jsonl` contain
  **your own account analytics and activity history** — a reason this repo is
  **private**. Keep it that way.
- Every mode posts/comments **only after your explicit approval** and verifies before claiming success.

## Roadmap

`docs/2026-07-03-linkedin-reach-optimization-design.md` is the original PRD for
retooling these skills around verified 2026 reach mechanics. Since it was written,
several of its concerns have been addressed directly in the skill: an
anti-repetition ledger gates same-topic posts, a bring-your-own-image path covers
photorealistic generators, and the check-replies mode closes the loop on outbound
engagement. Document carousels and a shared reach playbook remain open ideas —
see `git log` on `skills/linkedin/SKILL.md` for the detailed history of what's
shipped.
