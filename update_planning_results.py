#!/usr/bin/env python3
"""Update the planning results CSV and LaTeX table from Fast Downward logs."""

import csv
import io
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "planning_results.csv"
TOTAL_CSV_PATH = ROOT / "planning_totals.csv"
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
TOTAL_CSV_FIELDS = (
    "Instance",
    "Domain model",
    "Planner",
    "Total Runtime (s)",
    "Total Expanded States",
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
TOTAL_TIME_RE = re.compile(r"Total time: ([0-9.]+)s")
PLANNER_TIME_RE = re.compile(r"INFO\s+Planner time: ([0-9.]+)s")
CUMULATIVE_RE = re.compile(r"Cumulative statistics:")
PROGRESS_EXPANDED_RE = re.compile(
    r"\bg=.*?,\s*\d+ evaluated,\s*(\d+) expanded"
)


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


def read_total_summary(log_path, strategy):
    """Return whole-run runtime and expansions, if the log reports them."""
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ResultsError("Cannot read planner log {}: {}".format(log_path, exc))

    planner_time = None
    search_time = None
    cumulative_expanded = None
    expanded_values = []
    phase_expanded_values = []
    progress_expanded_values = []
    in_cumulative_stats = False

    for line in lines:
        planner_match = PLANNER_TIME_RE.search(line)
        if planner_match:
            planner_time = planner_match.group(1)

        total_match = TOTAL_TIME_RE.search(line)
        if total_match:
            search_time = total_match.group(1)

        if CUMULATIVE_RE.search(line):
            in_cumulative_stats = True
            continue

        expanded_match = EXPANDED_RE.search(line)
        if expanded_match:
            expanded_values.append(int(expanded_match.group(1)))
            if in_cumulative_stats and cumulative_expanded is None:
                cumulative_expanded = int(expanded_match.group(1))
                in_cumulative_stats = False
            elif not in_cumulative_stats:
                phase_expanded_values.append(int(expanded_match.group(1)))

        progress_match = PROGRESS_EXPANDED_RE.search(line)
        if progress_match:
            progress_expanded_values.append(int(progress_match.group(1)))

    # Prefer Fast Downward's high-precision search total. A search interrupted
    # externally may not print it, so fall back to the wrapper's planner time.
    total_runtime = search_time or planner_time
    if total_runtime is None:
        raise ResultsError("No total runtime found in {}".format(log_path))
    if search_time is None:
        total_runtime += "*"

    if strategy == "lama":
        # A finished iterated search prints its aggregate explicitly. When
        # interrupted, sum completed phases and the latest progress checkpoint
        # as a lower bound; the interrupted phase has no final summary.
        if cumulative_expanded is not None:
            total_expanded = str(cumulative_expanded)
        else:
            known_expanded = sum(phase_expanded_values)
            if progress_expanded_values:
                known_expanded += progress_expanded_values[-1]
            total_expanded = "At least {}".format(known_expanded)
    else:
        total_expanded = str(expanded_values[-1]) if expanded_values else None

    return {
        "runtime": total_runtime,
        "expanded": total_expanded if total_expanded is not None else "Unavailable",
    }


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


def collect_total_rows(instances):
    rows = []
    for instance in instances:
        for domain in DOMAINS:
            strategy = "lama"
            log_path = ROOT / "planner_outputs" / (
                "domain-{}_problem-{}_{}.txt".format(domain, instance, strategy)
            )
            summary = read_total_summary(log_path, strategy)
            rows.append(
                {
                    "Instance": instance,
                    "Domain model": domain,
                    "Planner": "LAMA",
                    "Total Runtime (s)": summary["runtime"],
                    "Total Expanded States": summary["expanded"],
                }
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


def load_existing_total_rows():
    if not TOTAL_CSV_PATH.exists():
        return []
    try:
        with TOTAL_CSV_PATH.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames != list(TOTAL_CSV_FIELDS):
                raise ResultsError(
                    "Unexpected columns in {}: {}".format(
                        TOTAL_CSV_PATH, reader.fieldnames
                    )
                )
            return list(reader)
    except OSError as exc:
        raise ResultsError("Cannot read {}: {}".format(TOTAL_CSV_PATH, exc))


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


def merge_total_rows(existing_rows, updated_rows, selected_instances):
    selected = set(selected_instances)
    merged = [row for row in existing_rows if row["Instance"] not in selected]
    merged.extend(updated_rows)
    planner_order = {"LAMA": 0}
    try:
        return sorted(
            merged,
            key=lambda row: (
                INSTANCES.index(row["Instance"]),
                DOMAINS.index(row["Domain model"]),
                planner_order[row["Planner"]],
            ),
        )
    except (KeyError, ValueError) as exc:
        raise ResultsError("Unexpected row in total CSV: {}".format(exc))


def render_csv_with_fields(rows, fields):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def render_csv(rows):
    return render_csv_with_fields(rows, CSV_FIELDS)


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


def render_total_tex(rows):
    tex_lines = [
        "% Requires \\usepackage{graphicx}",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{lllrr}",
        "\\hline",
        "Instance & Domain model & Planner & Total Runtime (s) & Total Expanded States \\\\",
        "\\hline",
    ]
    for row in rows:
        planner = row["Planner"].replace("A*", "A$\\ast$")
        tex_lines.append(
            "{} & {} & {} & {} & {} \\\\".format(
                row["Instance"],
                row["Domain model"],
                planner,
                row["Total Runtime (s)"],
                row["Total Expanded States"],
            )
        )
    tex_lines.extend(
        [
            "\\hline",
            "\\end{tabular}}",
            "\\caption{Total LAMA search runtime and expanded states at run termination. Compare these whole-run totals with the final-plan rows in the companion table to see the extra search after the final plan was found. Runtime is Fast Downward's total search time; * marks the wrapper planner time used when an externally interrupted search did not report its own total. For interrupted runs, expanded states are lower bounds from completed phase summaries and the latest progress checkpoint.}",
            "\\label{tab:planning-totals}",
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
    updated_total_rows = collect_total_rows(instances)
    existing_rows = load_existing_rows()
    if selection != "all" and not existing_rows:
        raise ResultsError(
            "Cannot update only {!r}: {} does not exist yet".format(selection, CSV_PATH)
        )

    rows = merge_rows(existing_rows, updated_rows, instances)
    existing_total_rows = load_existing_total_rows()
    if selection != "all" and not existing_total_rows:
        raise ResultsError(
            "Cannot update only {!r}: {} does not exist yet".format(
                selection, TOTAL_CSV_PATH
            )
        )
    total_rows = merge_total_rows(
        existing_total_rows, updated_total_rows, instances
    )
    csv_contents = render_csv(rows)
    tex_contents = render_tex(rows) + "\n" + render_total_tex(total_rows)
    write_text(CSV_PATH, csv_contents)
    write_text(TOTAL_CSV_PATH, render_csv_with_fields(total_rows, TOTAL_CSV_FIELDS))
    write_text(TEX_PATH, tex_contents)
    print(
        "Updated {} with {} plan row(s) and {} total row(s) in {}, {}, and {}.".format(
            selection,
            len(updated_rows),
            len(updated_total_rows),
            CSV_PATH.name,
            TOTAL_CSV_PATH.name,
            TEX_PATH.name,
        )
    )


if __name__ == "__main__":
    try:
        main(sys.argv)
    except ResultsError as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        sys.exit(1)
