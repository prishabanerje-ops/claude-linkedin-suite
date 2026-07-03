# claude-linkedin-suite

Portable **Claude Code** skills for LinkedIn — write & publish posts, comment on
your feed, and reply to comments on your own posts. Clone onto any machine and
run one command to get all three `/post-linkedin*` commands working.

## What's inside

```
skills/
  post-linkedin/                  Write + publish posts (text or image), score for engagement
    SKILL.md
    references/                   post-formats, source-domains, engage-and-comment guides
    scripts/                      linkedin_post.py, linkedin_image.py (+ tests)
  post-linkedin-feed-comments/    Comment on 2–3 relevant posts in your home feed
  post-linkedin-posts-comment/    Reply to comments on your own posts
config/
  linkedin-api.env.example        Credentials template (copy to ~/.config/linkedin-api.env)
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
1. Copies each skill into `~/.claude/skills/` (backing up any existing copy).
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

## The commands

| Command | Does |
|---------|------|
| `/post-linkedin` | Research-backed post on SEO+AI / AI-in-daily-life / vibe-coding pillars, engagement scorecard, then publishes text or one auto-generated image via the API. |
| `/post-linkedin-feed-comments` | Drives your logged-in Chrome to scan the home feed and comment on 2–3 relevant posts (per-item approval). |
| `/post-linkedin-posts-comment` | Drives your logged-in Chrome to read and reply to comments on your own posts (per-item approval). |

**Publishing** (`/post-linkedin`) uses LinkedIn's API + your token — no browser needed.
**Commenting** skills use **browser automation** (Chrome DevTools MCP) on a Chrome
profile already **signed into LinkedIn** — the API can't read feeds or post comments.

## Requirements

- **Python 3.9+** (standard library only for the current skills).
- **Claude Code** with the skills in `~/.claude/skills/` (the installer handles this). Restart Claude Code after installing so it discovers them.
- For the comment skills: **Chrome** signed into LinkedIn + the **Chrome DevTools MCP** available in your Claude Code session.

## Updating

Re-run the one-command install — it backs up your existing skill copies to
`~/.claude/skills/.backup-<timestamp>/` before overwriting, and leaves your
credentials file untouched.

## Security

- **No secrets in this repo.** The access token stays in `~/.config/linkedin-api.env` (git-ignored).
- `docs/reach-scorecard.html` and the PRD contain **your own account analytics** — a reason this repo is **private**. Keep it that way.
- Every skill posts/comments **only after your explicit approval** and verifies before claiming success.

## Roadmap

`docs/2026-07-03-linkedin-reach-optimization-design.md` is the PRD to re-tool
these skills around verified 2026 reach mechanics — document carousels
(highest-reach format the API supports), comment-pull CTAs, links-in-first-comment,
a reach-scoring engagement scorecard, and a shared reach playbook. Not yet built.
