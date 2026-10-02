"""High-level connector: `connector.py <harness> [--name N] [--cwd DIR] < prompt`.

Runs the harness (an entry in params.json) interactively via wrappers/tmux.py, in
tmux (attachable with `tmux attach -t <prefix>-<harness>-<name>`) and prints
the final answer to stdout.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("harness")
    ap.add_argument("--name", default="default")
    ap.add_argument("--cwd", default=os.getcwd())
    a = ap.parse_args()
    params = json.load(open(os.path.join(HERE, "params.json")))
    from wrappers import tmux
    out = tmux.run(a.harness, sys.stdin.read() + params["report_instruction"], a.name, a.cwd, params)
    print(report(out, params))


def report(out, p):
    """Only the final report reaches the caller; the full transcript stays in tmux."""
    lines = [l.strip() for l in out.splitlines()]
    if p["report_close"] in lines:
        end = len(lines) - 1 - lines[::-1].index(p["report_close"])
        if p["report_open"] in lines[:end]:
            start = end - 1 - lines[:end][::-1].index(p["report_open"])
            return "\n".join(lines[start + 1:end]).strip()
    return out[-p["fallback_chars"]:].strip()


if __name__ == "__main__":
    main()
