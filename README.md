# Multi-harness delegation for Claude Code

A Claude Code mod: Claude Code orchestrates, and Codex, Antigravity, opencode or a local model do the subtasks.

```
            Claude Code
                 │  Agent({ subagent_type: "multiharness-delegation:codex", prompt })
                 ▼
   ┌───────┬─────┴──┬──────────┐
 codex    agy    opencode      pi        each one in its own tmux
   └───────┴─────┬──┴──────────┘
                 ▼
          final report only
```

- Uses the other tools' quota, or your GPU, instead of Claude's.
- Same `Agent` call as a normal subagent.
- Only the final report comes back.
- You can jump in anytime: `tmux attach -t bridge-<harness>-<name>`

## Add a harness

One entry in `bridge/params.json` plus `agents/<harness>.md`.

## Status

Proof of concept. Tested: pi + local gemma. Plugin name is `multiharness-delegation` (`claude-*` names are reserved).
