"""Generic wrapper: harness TUI in tmux; prompt pasted in; done when a new report-close marker shows up."""
import re, subprocess, time


def tmux(*args, **kw):
    return subprocess.run(["tmux", *args], capture_output=True, text=True, **kw)


def pane(s):
    return tmux("capture-pane", "-p", "-J", "-S", "-", "-t", s).stdout


def clean(line):
    """Strip TUI decoration (box chars, bullets, indentation) around a line."""
    return re.sub(r"^[^\w<]+", "", line).rstrip(" │┃|")


def closes(text, p):
    return sum(clean(l) == p["report_close"] for l in text.splitlines())


def submit(s, prompt, p):
    tmux("load-buffer", "-b", s, "-", input=prompt)
    tmux("paste-buffer", "-p", "-d", "-b", s, "-t", s)
    time.sleep(p["paste_settle_s"])
    tmux("send-keys", "-t", s, "Enter")


def run(harness, prompt, name, cwd, p):
    h = p["harnesses"][harness]
    s = f'{p["tmux_prefix"]}-{harness}-{name}'
    if tmux("has-session", "-t", s).returncode:
        tmux("new-session", "-d", "-s", s, "-x", "200", "-y", "50", "-c", cwd, h["bin"], *h["args"])
        time.sleep(h.get("startup_s", p["startup_s"]))

    seen = closes(pane(s), p)
    # A first-run dialog (e.g. "trust this folder?") or a slow TUI can eat the paste:
    # resend while the prompt's first line has not shown up once more in the pane.
    probe = next((l.strip() for l in prompt.splitlines() if l.strip()), "")[:p["echo_probe_chars"]]
    for _ in range(1 + p["submit_retries"]):
        before = pane(s).count(probe)
        submit(s, prompt, p)
        time.sleep(p["submit_check_s"])
        if pane(s).count(probe) > before:
            break

    deadline = time.time() + p["timeout_s"]
    while time.time() < deadline:
        time.sleep(p["poll_s"])
        text = pane(s)
        if closes(text, p) > seen:
            time.sleep(p["stable_s"])
            return "\n".join(clean(l) for l in pane(s).splitlines())
    return f"[{harness} timeout after {p['timeout_s']}s; attach: tmux attach -t {s}]\n" + pane(s)[-p["fallback_chars"]:]
