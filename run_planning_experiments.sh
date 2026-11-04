#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PLANNER="${FAST_DOWNWARD_BIN:-$SCRIPT_DIR/fast-downward-26.6/fast-downward.py}"
VALIDATOR="${VALIDATE_BIN:-Validate}"

domains=(domain-A.pddl domain-B.pddl)
problems=(
    problem-small.pddl
    problem-medium.pddl
    problem-large.pddl
    problem-large-1drone.pddl
)

selection="${1:-all}"
if (($# > 1)); then
    printf 'Usage: %s [all|small|medium|large|large-1drone]\n' "$0" >&2
    exit 2
fi

case "$selection" in
    all) ;;
    small) problems=(problem-small.pddl) ;;
    medium) problems=(problem-medium.pddl) ;;
    large) problems=(problem-large.pddl) ;;
    large-1drone) problems=(problem-large-1drone.pddl) ;;
    *)
        printf 'Unknown problem selection: %s\nUsage: %s [all|small|medium|large|large-1drone]\n' \
            "$selection" "$0" >&2
        exit 2
        ;;
esac

if [[ ! -f "$PLANNER" ]]; then
    printf 'Fast Downward not found: %s\n' "$PLANNER" >&2
    exit 1
fi
if ! command -v "$VALIDATOR" >/dev/null 2>&1; then
    printf 'Validator not found on PATH: %s\n' "$VALIDATOR" >&2
    exit 1
fi

for domain in "${domains[@]}"; do
    if [[ ! -f "$domain" ]]; then
        printf 'Domain file not found: %s\n' "$domain" >&2
        exit 1
    fi
done
for problem in "${problems[@]}"; do
    if [[ ! -f "$problem" ]]; then
        printf 'Problem file not found: %s\n' "$problem" >&2
        exit 1
    fi
done

mkdir -p plans validations planner_outputs
failures=0

for domain in "${domains[@]}"; do
    domain_name="${domain%.pddl}"
    for problem in "${problems[@]}"; do
        problem_name="${problem%.pddl}"
        for strategy in lama astar-lmcut; do
            run_name="${domain_name}_${problem_name}_${strategy}"
            plan_prefix="plans/${run_name}"
            planner_output="planner_outputs/${run_name}.txt"

            printf '\n=== %s ===\n' "$run_name"
            if [[ "$strategy" == "lama" ]]; then
                python3 "$PLANNER" \
                    --alias lama \
                    --overall-time-limit 5m \
                    --plan-file "$plan_prefix" \
                    "$domain" "$problem" >"$planner_output"
                planner_status=$?
            else
                python3 "$PLANNER" \
                    --overall-time-limit 5m \
                    --plan-file "$plan_prefix" \
                    "$domain" "$problem" \
                    --search 'astar(lmcut())' >"$planner_output"
                planner_status=$?
            fi

            printf 'Planner stdout: %s\n' "$planner_output"
            plans_to_validate=()
            if [[ "$strategy" == "lama" ]]; then
                first_plan="${plan_prefix}.1"
                last_plan=""
                plan_number=1
                while [[ -s "${plan_prefix}.${plan_number}" ]]; do
                    last_plan="${plan_prefix}.${plan_number}"
                    plan_number=$((plan_number + 1))
                done

                if [[ -n "$last_plan" ]]; then
                    plans_to_validate+=("$first_plan")
                    if [[ "$last_plan" != "$first_plan" ]]; then
                        plans_to_validate+=("$last_plan")
                    fi
                    # Keep the first and final incumbent plans from this run.
                    for ((number = 2; number < plan_number - 1; number++)); do
                        rm -f -- "${plan_prefix}.${number}"
                    done
                fi
            else
                if [[ -s "$plan_prefix" ]]; then
                    plans_to_validate+=("$plan_prefix")
                fi
            fi

            if ((${#plans_to_validate[@]} == 0)); then
                validation_file="validations/${run_name}.txt"
                printf 'No plan was produced (planner exit %s); validation skipped. See %s for planner output.\n' \
                    "$planner_status" "$planner_output" >"$validation_file"
                printf 'No plan produced; note saved to %s\n' "$validation_file"
                failures=$((failures + 1))
                continue
            fi

            for plan_file in "${plans_to_validate[@]}"; do
                validation_suffix=""
                if [[ "$strategy" == "lama" ]]; then
                    if [[ "$plan_file" == "$first_plan" ]]; then
                        validation_suffix="_first"
                    else
                        validation_suffix="_last"
                    fi
                fi
                validation_file="validations/${run_name}${validation_suffix}.txt"
                if "$VALIDATOR" -v "$domain" "$problem" "$plan_file" >"$validation_file" 2>&1; then
                    printf 'Validated %s; output: %s\n' "$plan_file" "$validation_file"
                else
                    validator_status=$?
                    printf 'Validation failed for %s (exit %s); output: %s\n' \
                        "$plan_file" "$validator_status" "$validation_file" >&2
                    failures=$((failures + 1))
                fi
            done
        done
    done
done

if (( failures > 0 )); then
    printf '\nFinished with %s run(s) missing a plan or failing validation.\n' "$failures" >&2
    exit 1
fi

if ! python3 "$SCRIPT_DIR/update_planning_results.py" "$selection"; then
    printf 'Failed to update planning result tables.\n' >&2
    exit 1
fi

run_count=$((${#domains[@]} * ${#problems[@]} * 2))
printf '\nAll %s runs produced plans that passed validation.\n' "$run_count"
