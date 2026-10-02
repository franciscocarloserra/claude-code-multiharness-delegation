# AGENTS.md

Delegate to an external harness: call `Agent` with `subagent_type: "multiharness-delegation:<harness>"`, where `<harness>` is a key of `harnesses` in `bridge/params.json`.

Rules:
- Same `name`, same tmux session (`bridge-<harness>-<name>`): use it to continue a conversation.
- The answer is only the text between `<<<REPORT` and `REPORT>>>`. If the markers are missing you get the tail of the pane: say so, don't make up the rest.
- On timeout, report the tmux session to the user; do not retry on your own.
- Never kill a `bridge-*` tmux session: the user may be inside it.

Files (all short, read them before changing anything):
- `hooks/register.ts`: intercepts the call and runs the connector.
- `bridge/connector.py`: adds the report instruction and filters the output.
- `bridge/wrappers/tmux.py`: drives the TUI in tmux.
- `bridge/params.json`: every tunable value. Nothing numeric is hardcoded in the code.

Manual test without Claude Code:
`echo "What is 2+2?" | python3 bridge/connector.py pi --name test`
