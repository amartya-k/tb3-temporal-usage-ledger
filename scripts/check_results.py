"""Reject absent rewards and infrastructure errors before interpreting scores."""
import argparse
import json
from pathlib import Path


def check(root, expected, count=1):
    trials = []
    for path in sorted(Path(root).rglob("result.json")):
        value = json.loads(path.read_text())
        if "trial_name" in value:
            trials.append((path, value))
    if len(trials) != count:
        raise ValueError(f"Expected {count} trial results, found {len(trials)}")
    for path, result in trials:
        if result.get("exception_info") or any(
            step.get("exception_info") for step in result.get("step_results") or []
        ):
            raise ValueError(f"Execution error, not a model failure: {path}")
        if not result.get("finished_at") or not (result.get("verifier") or {}).get("finished_at"):
            raise ValueError(f"Incomplete trial or verifier: {path}")
        rewards = (result.get("verifier_result") or {}).get("rewards")
        if not isinstance(rewards, dict) or rewards != {"reward": expected}:
            raise ValueError(f"Expected reward {expected}, observed {rewards}: {path}")
        print(f"{path}: reward={expected}, no Harbor exception")
    return trials


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected", type=float, required=True)
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()
    check(args.root, args.expected, args.count)
