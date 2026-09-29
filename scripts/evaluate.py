"""Run one evaluation per Docker runner, using pinned upstream CI settings."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

import yaml
from check_results import check

ROOT = Path(__file__).resolve().parents[1]
TASK = "tasks/temporal-usage-ledger"
UPSTREAM = ROOT / "tb3"


def matrix(kind, configuration, selected_agent="all"):
    defaults = yaml.safe_load((UPSTREAM / ".github/harbor-run-defaults.yml").read_text())
    if kind == "review":
        return [{"id": "review", "kind": kind, "agent": defaults["review_agent"],
                 "model": defaults["review_model"], "kwargs": {}, "env": {}}]
    agents = []
    if configuration in ("ci", "both"):
        agents.extend(dict(agent, source="ci") for agent in defaults["agents"])
    if configuration in ("assignment", "both"):
        for agent, model in [("codex", "openai/gpt-6-sol"),
                             ("claude-code", "anthropic/claude-opus-5.5")]:
            inherited = next(item for item in defaults["agents"] if item["agent"] == agent)
            agents.append(dict(inherited, model=model, source="assignment"))
    entries = []
    for agent in agents:
        if selected_agent != "all" and agent["agent"] != selected_agent:
            continue
        for attempt in range(1, (defaults["trials"] if kind == "standard" else 1) + 1):
            entries.append(dict(agent, kind=kind,
                                id=f"{kind}-{agent['source']}-{agent['agent']}-{attempt}"))
    return entries


def run(entry):
    agent = entry["agent"]
    if agent == "claude-code":
        if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
            raise SystemExit("Missing CLAUDE_CODE_OAUTH_TOKEN subscription secret")
        os.environ["CLAUDE_FORCE_OAUTH"] = "1"
    elif agent == "codex":
        auth = os.environ.get("CODEX_AUTH_JSON")
        if not auth:
            raise SystemExit("Missing CODEX_AUTH_JSON subscription secret")
        decoded = json.loads(auth)
        if decoded.get("auth_mode") != "chatgpt" or not decoded.get("tokens"):
            raise SystemExit("CODEX_AUTH_JSON must contain a subscription login")
        auth_path = Path(os.environ["RUNNER_TEMP"]) / "evaluation-codex-auth.json"
        fd = os.open(auth_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(auth)
        os.environ["CODEX_AUTH_JSON_PATH"] = str(auth_path)
        os.environ["CODEX_FORCE_AUTH_JSON"] = "1"
    else:
        raise SystemExit(f"Subscription workflow does not support agent {agent!r}")
    # Keep subscription runs from falling back to paid API credentials.
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        os.environ.pop(name, None)
    os.environ.update({key: str(value) for key, value in entry.get("env", {}).items()})
    output = ROOT / "evaluation" / entry["id"]
    output.mkdir(parents=True, exist_ok=False)
    (output / "selection.json").write_text(json.dumps(entry, indent=2))
    task_path = ROOT / TASK
    if entry["kind"] == "review":
        task_path = ROOT / "review-task"
        subprocess.run([
            sys.executable, str(UPSTREAM / "scripts/review/stage_task.py"),
            "--repository", os.environ["GITHUB_REPOSITORY"],
            "--commit", os.environ["GITHUB_SHA"], "--task-path", TASK,
            str(task_path),
        ], check=True)
    command = ["harbor", "run", "-p", str(task_path), "--agent", agent,
               "--model", entry["model"], "--env", "docker", "--yes",
               "--n-attempts", "1", "--jobs-dir", str(output / "jobs")]
    for key, value in entry.get("kwargs", {}).items():
        command.extend(["--ak", f"{key}={value}"])
    if entry["kind"] == "cheat":
        command.extend(["--extra-instruction-path", str(UPSTREAM / "docs/prompts/hack-trial-prompt.md")])
    (output / "command.json").write_text(json.dumps(command, indent=2))
    try:
        subprocess.run(command, check=True)
        trials = check(output / "jobs", 1 if entry["kind"] == "review" else 0)
        if entry["kind"] == "review":
            paths = list(trials[0][0].parent.glob("artifacts/**/verdicts.json"))
            if len(paths) != 1:
                raise ValueError("Missing or ambiguous rubric verdicts artifact")
            verdicts = json.loads(paths[0].read_text())["checks"]
            rubric = tomllib.loads((UPSTREAM / "docs/prompts/task-implementation.toml").read_text())
            if set(verdicts) != {item["name"] for item in rubric["criteria"]}:
                raise ValueError("Rubric verdicts do not cover every criterion")
            failures = [key for key, value in verdicts.items()
                        if value.get("outcome") not in ("pass", "not_applicable")
                        or not str(value.get("explanation", "")).strip()]
            if failures:
                raise ValueError(f"Rubric criteria failed: {failures}")
        else:
            print("Reward gate met. Trajectory review is still required to classify the failure.")
    finally:
        if agent == "codex":
            auth_path.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", choices=("review", "standard", "cheat"))
    parser.add_argument("--configuration", choices=("ci", "assignment", "both"), default="both")
    parser.add_argument("--entry")
    parser.add_argument("--selected-agent", choices=("all", "codex", "claude-code"), default="all")
    args = parser.parse_args()
    if args.matrix:
        print(json.dumps({"include": matrix(args.matrix, args.configuration, args.selected_agent)}))
    elif args.entry:
        run(json.loads(args.entry))
    else:
        parser.error("Supply --matrix or --entry")
