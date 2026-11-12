"""Checks your Session 1 exercise.

Run:  python3 lessons/session-01/check.py
(Optional: pass a different file path to check that file instead.)
"""

import contextlib
import io
import runpy
import sys
from pathlib import Path

target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "exercise.py"

# Run the exercise and catch everything it prints.
printed = io.StringIO()
try:
    with contextlib.redirect_stdout(printed):
        names = runpy.run_path(str(target), run_name="__main__")
except Exception as err:
    print("Your file stopped with an error before I could check it:")
    print(f"  {type(err).__name__}: {err}")
    print("Hint: read the error, it usually names the line. Look for a missing quote or bracket.")
    print("SCORE: 0/6")
    sys.exit(1)

output = printed.getvalue()
lines = output.splitlines()
results = []  # (skill, passed, message)


def check(skill, passed, ok_msg, hint):
    results.append((skill, passed, ok_msg if passed else hint))


# 1. print
check("print", "Hello, agent!" in output,
      'Printed "Hello, agent!"',
      'I didn\'t see "Hello, agent!" printed. Check the spelling, the comma and the ! mark.')

# 2. agent_name
name = names.get("agent_name")
check("variables", isinstance(name, str) and name.strip() != "",
      f"agent_name is {name!r}",
      "I can't find agent_name as text. Make it like: agent_name = \"Scout\" (with quotes).")

# 3. max_steps
steps = names.get("max_steps")
check("variables", type(steps) is int and steps == 5,
      "max_steps is the number 5",
      "max_steps should be the number 5 with no quotes. \"5\" in quotes is text, not a number.")

# 4. task
task = names.get("task")
check("variables", isinstance(task, str) and task.strip() != "",
      f"task is {task!r}",
      "I can't find task as text. Make it like: task = \"Find three good pizza places\".")

# 5. status line using both variables
status_ok = isinstance(name, str) and name and any(
    name in line and str(steps) in line for line in lines
)
check("print", bool(status_ok),
      "Printed a line with the agent name and step count",
      "Print one line that includes agent_name and max_steps, like: "
      "print(\"Agent\", agent_name, \"can take\", max_steps, \"steps\")")

# 6. steps_used reassignment
used = names.get("steps_used")
check("variables", used == 1 and "1" in lines,
      "steps_used went from 0 to 1 and was printed",
      "Set steps_used = 0, then steps_used = steps_used + 1, then print(steps_used). It should print 1.")

# Report
print(f"Checking {target.name}\n")
for i, (skill, passed, msg) in enumerate(results, 1):
    mark = "PASS" if passed else "FAIL"
    print(f"{mark}  {i}. [{skill}] {msg}")
score = sum(p for _, p, _ in results)
print(f"\nSCORE: {score}/{len(results)}")
if score == len(results):
    print("All done. Nice work!")
