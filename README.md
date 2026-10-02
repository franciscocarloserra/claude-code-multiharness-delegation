# claude-code-multiharness-delegation

Delegate any subtask (writing code, tests, reviews, research, running commands) from Claude Code to whichever harness you want: Codex, Antigravity, opencode, a local model through pi, or any other TUI agent you add in one config line. Claude Code stays the orchestrator; each delegate runs on its own subscription, or for free on your GPU.

```
                 ┌──────────────────────────────┐
   you ────────▶ │  Claude Code (orchestrator)  │  plans, splits work, reads reports
                 └──────────────┬───────────────┘
                                │  Agent({ subagent_type: "multiharness-delegation:<harness>" })
                                ▼
                 ┌──────────────────────────────┐
                 │  mod: intercepts the call    │  adds "end with a report" to the prompt
                 └──────────────┬───────────────┘
          ┌───────────────┬─────┴─────────┬───────────────┐
          ▼               ▼               ▼               ▼
     ┌─────────┐     ┌─────────┐     ┌──────────┐    ┌──────────┐
     │  codex  │     │   agy   │     │ opencode │    │    pi    │   each one live in tmux:
     │ ChatGPT │     │ Google  │     │ any API  │    │ local GPU│   tmux attach -t bridge-<harness>-<name>
     └────┬────┘     └────┬────┘     └────┬─────┘    └────┬─────┘
          └───────────────┴───────┬───────┴───────────────┘
                                  ▼
                 only the final report goes back to Claude
                 (reasoning and tool calls stay in tmux)
```

**Why it matters**

- **Save Claude quota.** A normal Claude subagent spends Claude quota. With this mod, Claude only plans and delegates; the heavy lifting runs on your ChatGPT plan (codex), your Google plan (agy), any provider (opencode), or a local model (pi) that costs nothing.
- **Nothing new to learn.** Claude delegates with the same `Agent` call it already uses for its own subagents. No extra tools, no wrapper scripts in the prompt.
- **Claude's context stays clean.** Only the subagent's final report comes back, not its reasoning or tool calls, the same as a native subagent.
- **You stay in control.** Each delegate runs in a real interactive session, not a headless background process. You can open it anytime, watch it work, correct it or take over by hand.

Plugin name: `multiharness-delegation` (Claude Code reserves names starting with `claude-`).

## Usage

```
Agent({ subagent_type: "multiharness-delegation:pi", description: "...", prompt: "..." })
```

The mod catches that call and starts the harness for real, interactively, inside tmux. It pastes in the prompt and waits for the answer. Only the final report goes back to Claude; the full conversation stays in tmux, and you can jump in anytime:

```
tmux attach -t bridge-<harness>-<name>
```

Calls that use the same `name` land in the same session, so the conversation continues there.

## How it works

1. `hooks/register.ts` intercepts `Agent` calls whose type starts with `multiharness-delegation:` and runs the connector.
2. `bridge/connector.py` appends a short instruction to the prompt: close with a report between `<<<REPORT` and `REPORT>>>`. Only that part is returned.
3. `bridge/wrappers/tmux.py` opens the harness in tmux, pastes the prompt and reads the pane until a new `REPORT>>>` shows up. It never reads session files from disk.

## Add a harness

Add an entry under `harnesses` in `bridge/params.json` (`bin`, `args`) and a file `agents/<harness>.md` so Claude sees it in its list of agent types. Timeouts, markers and polling intervals all live in `params.json` too.

## Status

Proof of concept. pi with gemma 4 (local llama-server) has been tested. codex, agy and opencode are wired up but untested. The `SendMessage` hint Claude Code shows after each call does not work; to continue, call `Agent` again with the same `name`.
