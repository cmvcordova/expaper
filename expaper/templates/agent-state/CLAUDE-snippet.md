## Shared agent state

Several people's Claude sessions work in this repo, and they share state only through git: `docs/agent-state/`
(conventions in its `README.md`). The `lrw-agent-state` plugin's SessionStart hook shows what changed there on `origin`.
Claim work in the board before a multi-step task, append to your person's log when done, commit state changes with a
`state:` subject, and fetch and rebase onto `origin` before every push. The current board:

@docs/agent-state/board.md
