# Commands run in planning experiments

```sh
python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-A_problem-small_lama domain-A.pddl problem-small.pddl > planner_outputs/domain-A_problem-small_lama.txt
Validate -v domain-A.pddl problem-small.pddl plans/domain-A_problem-small_lama.1 > validations/domain-A_problem-small_lama_first.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-A_problem-small_astar-lmcut domain-A.pddl problem-small.pddl --search 'astar(lmcut())' > planner_outputs/domain-A_problem-small_astar-lmcut.txt
Validate -v domain-A.pddl problem-small.pddl plans/domain-A_problem-small_astar-lmcut > validations/domain-A_problem-small_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-A_problem-medium_lama domain-A.pddl problem-medium.pddl > planner_outputs/domain-A_problem-medium_lama.txt
Validate -v domain-A.pddl problem-medium.pddl plans/domain-A_problem-medium_lama.1 > validations/domain-A_problem-medium_lama_first.txt 2>&1
Validate -v domain-A.pddl problem-medium.pddl plans/domain-A_problem-medium_lama.7 > validations/domain-A_problem-medium_lama_last.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-A_problem-medium_astar-lmcut domain-A.pddl problem-medium.pddl --search 'astar(lmcut())' > planner_outputs/domain-A_problem-medium_astar-lmcut.txt
Validate -v domain-A.pddl problem-medium.pddl plans/domain-A_problem-medium_astar-lmcut > validations/domain-A_problem-medium_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-A_problem-large_lama domain-A.pddl problem-large.pddl > planner_outputs/domain-A_problem-large_lama.txt
Validate -v domain-A.pddl problem-large.pddl plans/domain-A_problem-large_lama.1 > validations/domain-A_problem-large_lama_first.txt 2>&1
Validate -v domain-A.pddl problem-large.pddl plans/domain-A_problem-large_lama.4 > validations/domain-A_problem-large_lama_last.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-A_problem-large_astar-lmcut domain-A.pddl problem-large.pddl --search 'astar(lmcut())' > planner_outputs/domain-A_problem-large_astar-lmcut.txt
Validate -v domain-A.pddl problem-large.pddl plans/domain-A_problem-large_astar-lmcut > validations/domain-A_problem-large_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-A_problem-large-1drone_lama domain-A.pddl problem-large-1drone.pddl > planner_outputs/domain-A_problem-large-1drone_lama.txt
Validate -v domain-A.pddl problem-large-1drone.pddl plans/domain-A_problem-large-1drone_lama.1 > validations/domain-A_problem-large-1drone_lama_first.txt 2>&1
Validate -v domain-A.pddl problem-large-1drone.pddl plans/domain-A_problem-large-1drone_lama.3 > validations/domain-A_problem-large-1drone_lama_last.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-A_problem-large-1drone_astar-lmcut domain-A.pddl problem-large-1drone.pddl --search 'astar(lmcut())' > planner_outputs/domain-A_problem-large-1drone_astar-lmcut.txt
Validate -v domain-A.pddl problem-large-1drone.pddl plans/domain-A_problem-large-1drone_astar-lmcut > validations/domain-A_problem-large-1drone_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-B_problem-small_lama domain-B.pddl problem-small.pddl > planner_outputs/domain-B_problem-small_lama.txt
Validate -v domain-B.pddl problem-small.pddl plans/domain-B_problem-small_lama.1 > validations/domain-B_problem-small_lama_first.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-B_problem-small_astar-lmcut domain-B.pddl problem-small.pddl --search 'astar(lmcut())' > planner_outputs/domain-B_problem-small_astar-lmcut.txt
Validate -v domain-B.pddl problem-small.pddl plans/domain-B_problem-small_astar-lmcut > validations/domain-B_problem-small_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-B_problem-medium_lama domain-B.pddl problem-medium.pddl > planner_outputs/domain-B_problem-medium_lama.txt
Validate -v domain-B.pddl problem-medium.pddl plans/domain-B_problem-medium_lama.1 > validations/domain-B_problem-medium_lama_first.txt 2>&1
Validate -v domain-B.pddl problem-medium.pddl plans/domain-B_problem-medium_lama.3 > validations/domain-B_problem-medium_lama_last.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-B_problem-medium_astar-lmcut domain-B.pddl problem-medium.pddl --search 'astar(lmcut())' > planner_outputs/domain-B_problem-medium_astar-lmcut.txt
Validate -v domain-B.pddl problem-medium.pddl plans/domain-B_problem-medium_astar-lmcut > validations/domain-B_problem-medium_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-B_problem-large_lama domain-B.pddl problem-large.pddl > planner_outputs/domain-B_problem-large_lama.txt
Validate -v domain-B.pddl problem-large.pddl plans/domain-B_problem-large_lama.1 > validations/domain-B_problem-large_lama_first.txt 2>&1
Validate -v domain-B.pddl problem-large.pddl plans/domain-B_problem-large_lama.2 > validations/domain-B_problem-large_lama_last.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-B_problem-large_astar-lmcut domain-B.pddl problem-large.pddl --search 'astar(lmcut())' > planner_outputs/domain-B_problem-large_astar-lmcut.txt
Validate -v domain-B.pddl problem-large.pddl plans/domain-B_problem-large_astar-lmcut > validations/domain-B_problem-large_astar-lmcut.txt 2>&1

python3 fast-downward-26.6/fast-downward.py --alias lama --overall-time-limit 5m --plan-file plans/domain-B_problem-large-1drone_lama domain-B.pddl problem-large-1drone.pddl > planner_outputs/domain-B_problem-large-1drone_lama.txt
Validate -v domain-B.pddl problem-large-1drone.pddl plans/domain-B_problem-large-1drone_lama.1 > validations/domain-B_problem-large-1drone_lama_first.txt 2>&1
Validate -v domain-B.pddl problem-large-1drone.pddl plans/domain-B_problem-large-1drone_lama.3 > validations/domain-B_problem-large-1drone_lama_last.txt 2>&1
python3 fast-downward-26.6/fast-downward.py --overall-time-limit 5m --plan-file plans/domain-B_problem-large-1drone_astar-lmcut domain-B.pddl problem-large-1drone.pddl --search 'astar(lmcut())' > planner_outputs/domain-B_problem-large-1drone_astar-lmcut.txt
Validate -v domain-B.pddl problem-large-1drone.pddl plans/domain-B_problem-large-1drone_astar-lmcut > validations/domain-B_problem-large-1drone_astar-lmcut.txt 2>&1
```

The LAMA final-plan numbers shown above are from the recorded run; they can
change when the planner produces a different number of plans.
