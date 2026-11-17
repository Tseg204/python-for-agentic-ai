"""Checks your Session 3 exercise.

Run:  python3 lessons/session-03/check.py
(Optional: pass a different file path to check that file instead.)
"""

import ast
import contextlib
import io
import math
import runpy
import sys
from pathlib import Path

target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "exercise.py"
TOTAL = 6

# Run the exercise and catch everything it prints.
printed = io.StringIO()
try:
    with contextlib.redirect_stdout(printed):
        names = runpy.run_path(str(target), run_name="__main__")
except Exception as err:
    print("Your file stopped with an error before I could check it:")
    print(f"  {type(err).__name__}: {err}")
    print("Hint: read the error, it usually names the line. Look for a missing colon (:)")
    print("after if/else, a line that isn't indented, or = where you meant ==.")
    print(f"SCORE: 0/{TOTAL}")
    sys.exit(1)

lines = [line.rstrip() for line in printed.getvalue().splitlines()]
tree = ast.parse(target.read_text())


def assigned_from(var_name, node_types):
    """True if the variable is set from one of these kinds of expressions."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, node_types):
            if any(isinstance(t, ast.Name) and t.id == var_name for t in node.targets):
                return True
    return False


def run_with(**overrides):
    """Run the file again with some top-level variables changed. Returns printed lines."""
    new_tree = ast.parse(target.read_text())
    for node in new_tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in overrides:
                    node.value = ast.copy_location(ast.Constant(overrides[t.id]), node.value)
    ast.fix_missing_locations(new_tree)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(new_tree, str(target), "exec"), {"__name__": "__main__"})
    except Exception:
        return None
    return [line.rstrip() for line in out.getvalue().splitlines()]


has_if = any(isinstance(n, ast.If) for n in ast.walk(tree))
results = []  # (skill, passed, message)


def check(skill, passed, ok_msg, hint):
    results.append((skill, passed, ok_msg if passed else hint))


# 1. step and max_steps are numbers
step, max_steps = names.get("step"), names.get("max_steps")
nums_ok = type(step) is int and type(max_steps) is int and (step, max_steps) == (3, 5)
if "step" not in names or "max_steps" not in names:
    hint1 = "I can't find step and max_steps. Make them: step = 3 and max_steps = 5."
elif isinstance(step, str) or isinstance(max_steps, str):
    hint1 = "step and max_steps have quotes, so they're text. Numbers have no quotes: step = 3."
else:
    hint1 = "step should be 3 and max_steps should be 5."
check("numbers", nums_ok, "step is 3 and max_steps is 5, both numbers", hint1)

# 2. steps_left
steps_left = names.get("steps_left")
check("numbers",
      steps_left == 2 and assigned_from("steps_left", ast.BinOp) and "Steps left: 2" in lines,
      "steps_left is 2 and you printed 'Steps left: 2'",
      "steps_left should be max_steps - step (use the variable names, not 2). "
      "Then print(f\"Steps left: {steps_left}\").")

# 3. cost
cost = names.get("cost")
cost_ok = isinstance(cost, (int, float)) and math.isclose(cost, 2.4) and assigned_from("cost", ast.BinOp)
check("numbers", cost_ok and any(l in ("2.4", "2.40") for l in lines),
      "cost is 2.4 and you printed it",
      "cost should be tokens_used * price_per_token, then print(cost). "
      "Use the star *, and the two variable names.")

# 4. is_done
is_done = names.get("is_done")
if is_done is None:
    hint4 = "I can't find is_done. Make it: is_done = step >= max_steps"
elif not isinstance(is_done, bool):
    hint4 = f"is_done is {is_done!r}, but it should be True or False. Use a comparison like >=."
else:
    hint4 = "is_done should come from a comparison: step >= max_steps. Then print(is_done)."
check("booleans",
      is_done is False and assigned_from("is_done", ast.Compare) and "False" in lines,
      "is_done is False and you printed it",
      hint4)

# 5. if / else about steps
normal = lines
at_limit = run_with(step=5)
ok5 = (has_if and "Keep going" in normal and "Stop" not in normal
       and at_limit is not None and "Stop" in at_limit and "Keep going" not in at_limit)
if not has_if:
    hint5 = "I don't see an if yet. Start with: if step >= max_steps:"
elif "Keep going" not in normal:
    hint5 = "With step 3 and max_steps 5 it should print Keep going. Check the else part."
else:
    hint5 = ("When I set step to 5 it should print Stop (and not Keep going). "
             "Check you used >= and that the comparison uses step and max_steps.")
check("conditions", ok5, "prints Keep going at step 3 and Stop at step 5", hint5)

# 6. if / else about user_reply
replies = {"  Yes ": "Running the task", "YES": "Running the task", "yes": "Running the task",
           "no": "Cancelled", "  nope ": "Cancelled"}
bad = []
for reply, want in replies.items():
    out = normal if reply == "  Yes " else run_with(user_reply=reply)
    other = "Cancelled" if want == "Running the task" else "Running the task"
    if out is None or want not in out or other in out:
        bad.append(reply)
if not bad:
    hint6 = ""
elif "  Yes " in bad or "YES" in bad:
    hint6 = (f"When the user types {bad[0]!r} it should print Running the task. "
             "Clean it first: user_reply.strip().lower() == \"yes\"")
else:
    hint6 = f"When the user types {bad[0]!r} it should print Cancelled. Check your else."
check("conditions", not bad, "handles yes, YES, '  Yes ' and no correctly", hint6)

# Report
print(f"Checking {target.name}\n")
for i, (skill, passed, msg) in enumerate(results, 1):
    mark = "PASS" if passed else "FAIL"
    print(f"{mark}  {i}. [{skill}] {msg}")
score = sum(p for _, p, _ in results)
print(f"\nSCORE: {score}/{len(results)}")
if score == len(results):
    print("All done. Nice work!")
