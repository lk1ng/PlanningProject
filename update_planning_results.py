#!/usr/bin/env python3
"""Update the planning results CSV and LaTeX table from Fast Downward logs."""

import csv
import io
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "planning_results.csv"
TEX_PATH = ROOT / "planning_results.tex"

INSTANCES = ("small", "medium", "large", "large-1drone")
DOMAINS = ("A", "B")
CSV_FIELDS = (
    "Instance",
    "Domain model",
    "Planner",
    "Solved",
    "Runtime(s)",
    "Plan length",
    "Plan cost",
    "Expanded states",
)
INSTANCE_ALIASES = {
    "all": INSTANCES,
    "small": ("small",),
    "medium": ("medium",),
    "large": ("large",),
    "large-1drone": ("large-1drone",),
}

PLAN_LENGTH_RE = re.compile(
    r"\[t=([0-9.]+)s,.*?\]\s+Plan length: (\d+) step\(s\)\."
)
PLAN_COST_RE = re.compile(r"Plan cost: (\d+)")
EXPANDED_RE = re.compile(r"Expanded (\d+) state\(s\)\.")


class ResultsError(Exception):
    """Raised when an experiment log cannot be converted into a result row."""


def read_plan_summaries(log_path):
    """Return plan records, including expansion totals through each plan."""
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ResultsError("Cannot read planner log {}: {}".format(log_path, exc))

    expanded_so_far = 0
    summaries = []
    for line_number, line in enumerate(lines):
        expanded_match = EXPANDED_RE.search(line)
        if expanded_match:
            expanded_so_far += int(expanded_match.group(1))

        plan_match = PLAN_LENGTH_RE.search(line)
        if not plan_match:
            continue

        plan_cost = None
        plan_expanded = None
        plan_expanded_total = None
        # Fast Downward prints the cost and expanded count immediately after
        # each plan length summary. Search a few lines to tolerate log spacing.
        expansions_through_plan = 0
        for following_line in lines[line_number + 1 : line_number + 5]:
            cost_match = PLAN_COST_RE.search(following_line)
            if cost_match and plan_cost is None:
                plan_cost = int(cost_match.group(1))

            following_expanded = EXPANDED_RE.search(following_line)
            if following_expanded:
                plan_expanded = int(following_expanded.group(1))
                expansions_through_plan += plan_expanded
                plan_expanded_total = expanded_so_far + expansions_through_plan
                break

        if plan_cost is None or plan_expanded is None:
            raise ResultsError(
                "Incomplete plan summary in {} near line {}".format(
                    log_path, line_number + 1
                )
            )

        summaries.append(
            {
                "runtime": plan_match.group(1),
                "length": int(plan_match.group(2)),
                "cost": plan_cost,
                "expanded": plan_expanded_total,
            }
        )
    if not summaries:
        raise ResultsError("No plan summary found in {}".format(log_path))
    return summaries


def make_row(instance, domain, planner, summary):
    return {
        "Instance": instance,
        "Domain model": domain,
        "Planner": planner,
        "Solved": "Yes",
        "Runtime(s)": summary["runtime"],
        "Plan length": str(summary["length"]),
        "Plan cost": str(summary["cost"]),
        "Expanded states": str(summary["expanded"]),
    }


def collect_rows(instances):
    rows = []
    for instance in instances:
        for domain in DOMAINS:
            for strategy, planner_name in (
                ("astar-lmcut", "A* LM-cut"),
                ("lama", "LAMA"),
            ):
                log_path = ROOT / "planner_outputs" / (
                    "domain-{}_problem-{}_{}.txt".format(domain, instance, strategy)
                )
                summaries = read_plan_summaries(log_path)

                if strategy == "astar-lmcut":
                    if len(summaries) != 1:
                        raise ResultsError(
                            "Expected one A* plan summary in {}, found {}".format(
                                log_path, len(summaries)
                            )
                        )
                    rows.append(make_row(instance, domain, planner_name, summaries[0]))
                    continue

                rows.append(make_row(instance, domain, "LAMA 1", summaries[0]))
                if len(summaries) > 1:
                    rows.append(
                        make_row(instance, domain, "LAMA final", summaries[-1])
                    )
    return rows


def load_existing_rows():
    if not CSV_PATH.exists():
        return []
    try:
        with CSV_PATH.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames != list(CSV_FIELDS):
                raise ResultsError(
                    "Unexpected columns in {}: {}".format(CSV_PATH, reader.fieldnames)
                )
            return list(reader)
    except OSError as exc:
        raise ResultsError("Cannot read {}: {}".format(CSV_PATH, exc))


def sort_key(row):
    planner_order = {"A* LM-cut": 0, "LAMA 1": 1, "LAMA final": 2}
    return (
        INSTANCES.index(row["Instance"]),
        DOMAINS.index(row["Domain model"]),
        planner_order[row["Planner"]],
    )


def merge_rows(existing_rows, updated_rows, selected_instances):
    selected = set(selected_instances)
    merged = [row for row in existing_rows if row["Instance"] not in selected]
    merged.extend(updated_rows)
    try:
        return sorted(merged, key=sort_key)
    except (KeyError, ValueError) as exc:
        raise ResultsError("Unexpected row in existing CSV: {}".format(exc))


def render_csv(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def render_tex(rows):
    tex_lines = [
        "% Requires \\usepackage{graphicx}",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{lllcrrrr}",
        "\\hline",
        "Instance & Domain model & Planner & Solved & Runtime (s) & Plan length & Plan cost & Expanded states \\\\",
        "\\hline",
    ]
    for row in rows:
        planner = row["Planner"].replace("A*", "A$\\ast$")
        tex_lines.append(
            "{} & {} & {} & {} & {} & {} & {} & {} \\\\".format(
                row["Instance"],
                row["Domain model"],
                planner,
                row["Solved"],
                row["Runtime(s)"],
                row["Plan length"],
                row["Plan cost"],
                row["Expanded states"],
            )
        )
    tex_lines.extend(
        [
            "\\hline",
            "\\end{tabular}}",
            "\\caption{Planning experiment results. LAMA reports its first plan and, when distinct, its final plan found before stopping. The final plan is the best found in that run; the planner had a five-minute time limit. Runtime is elapsed time at plan discovery; expanded states for LAMA are cumulative through that plan.}",
            "\\label{tab:planning-results}",
            "\\end{table}",
        ]
    )
    return "\n".join(tex_lines) + "\n"


def write_text(path, contents):
    try:
        with path.open("w", encoding="utf-8", newline="") as output_file:
            output_file.write(contents)
    except OSError as exc:
        raise ResultsError("Cannot write {}: {}".format(path, exc))


def main(argv):
    if len(argv) > 2:
        raise ResultsError(
            "Usage: {} [all|small|medium|large|large-1drone]".format(argv[0])
        )
    selection = argv[1] if len(argv) == 2 else "all"
    if selection not in INSTANCE_ALIASES:
        raise ResultsError(
            "Unknown selection {!r}. Usage: {} [all|small|medium|large|large-1drone]".format(
                selection, argv[0]
            )
        )

    instances = INSTANCE_ALIASES[selection]
    updated_rows = collect_rows(instances)
    existing_rows = load_existing_rows()
    if selection != "all" and not existing_rows:
        raise ResultsError(
            "Cannot update only {!r}: {} does not exist yet".format(selection, CSV_PATH)
        )

    rows = merge_rows(existing_rows, updated_rows, instances)
    csv_contents = render_csv(rows)
    tex_contents = render_tex(rows)
    write_text(CSV_PATH, csv_contents)
    write_text(TEX_PATH, tex_contents)
    print(
        "Updated {} with {} result row(s) in {} and {}.".format(
            selection, len(updated_rows), CSV_PATH.name, TEX_PATH.name
        )
    )


if __name__ == "__main__":
    try:
        main(sys.argv)
    except ResultsError as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        sys.exit(1)
