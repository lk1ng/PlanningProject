#!/bin/bash
# VS Code sends: fd_wrapper.sh [options] domain.pddl problem.pddl

# 1. Extract the positional PDDL arguments from the end
PROBLEM="${@: -1}"
DOMAIN="${@: -2:1}"

# 2. Extract all the options provided by the extension prompt
ALL_OPTIONS="${@:1:$#-2}"

# 3. Separate options into pre-file (global/alias) and post-file (search) arrays
PRE_FILES=()
POST_FILES=()

# Loop through options to sort them dynamically
while [[ $# -gt 2 ]]; do
    case "$1" in
        --alias)
            PRE_FILES+=("$1" "$2")
            shift 2
            ;;
        --search)
            POST_FILES+=("$1" "$2")
            shift 2
            ;;
        *)
            # Default fallback for any other flags
            PRE_FILES+=("$1")
            shift 1
            ;;
    esac
done

# 4. Execute Fast Downward in the mathematically perfect sequence
# Order: fast-downward.py [alias/global flags] domain.pddl problem.pddl [search flags]
python3 ./fast-downward-26.6/fast-downward.py "${PRE_FILES[@]}" "$DOMAIN" "$PROBLEM" "${POST_FILES[@]}"
