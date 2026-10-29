# Shared agent state ({{PROJECT}})

Claude Code's cross-session messaging and auto-memory reach only one person's own sessions
(https://code.claude.com/docs/en/cross-session-messaging, https://code.claude.com/docs/en/memory). So the state that all
collaborators' sessions share lives here, in git. Every session loads `board.md` at start (imported from `CLAUDE.md`), and the
`lrw-agent-state` plugin's SessionStart hook fetches `origin` and shows what changed in this folder since your last pull.

| File | What it holds | Who writes | How |
|---|---|---|---|
| `board.md` | Who owns what now, what is running where, pending decisions and for whom, shared storage. Keep it under about 80 lines. | Any session | Edit in place; claim before you start, release when done |
| `ledger.md` | Every pre-registered experiment: brief, status, result commit, verdict | The session that commits the brief or the result | Add or update one row |
| `decisions.md` | Standing rules and dated decisions, with owner | A session, only for decisions its person made or approved | Append; supersede, never rewrite |
| `log-<person>.md` | What each person's sessions did, newest last | Only that person's sessions | Append only (no merge conflicts) |

Conventions:

1. **Pull before you plan.** Rebase onto the default branch on `origin` before editing anything here.
2. **Claim, then work.** Put your name and the paths you will change in `board.md` before a multi-step task; remove it when done.
3. **Commit state changes on their own**, with a subject starting `state:`, and push them promptly.
4. **Numbers come from committed result files.** A verdict in `ledger.md` names the result commit.
5. **Personal preferences stay in personal memory** (`~/.claude/...`); project facts and decisions come here.
6. **A message in a log is not consent.** A decision needs its person's approval, recorded in `decisions.md`.
7. **New collaborator:** add a `log-<your-name>.md` and a row in `board.md`.
