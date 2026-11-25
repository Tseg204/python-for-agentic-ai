"""Checks your Session 5 exercise.

Run:  python3 lessons/session-05/check.py
(Optional: pass a different file path to check that file instead.)
"""

import ast
import contextlib
import io
import signal
import sys
from pathlib import Path

target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "exercise.py"
TOTAL = 6
source = target.read_text()
tree = ast.parse(source)


class Stuck(Exception):
    pass


def _alarm(signum, frame):
    raise Stuck()


signal.signal(signal.SIGALRM, _alarm)


def run_with(**overrides):
    """Run the file, optionally with some top-level variables changed.
    Returns (printed lines, variables) or raises."""
    new_tree = ast.parse(source)
    for node in new_tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in overrides:
                    node.value = ast.copy_location(
                        ast.parse(repr(overrides[t.id]), mode="eval").body, node.value)
    ast.fix_missing_locations(new_tree)
    out = io.StringIO()
    names = {"__name__": "__main__"}
    signal.alarm(3)
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(new_tree, str(target), "exec"), names)
    finally:
        signal.alarm(0)
    return [line.rstrip() for line in out.getvalue().splitlines()], names


def safe_run(**overrides):
    try:
        return run_with(**overrides)[0]
    except BaseException:
        return None


# Run the exercise as it is.
try:
    lines, names = run_with()
except Stuck:
    print("Your file never finished. That's almost always a while loop that runs forever.")
    print("Hint: inside the while loop, make sure you add 1 to steps (steps += 1).")
    print(f"SCORE: 0/{TOTAL}")
    sys.exit(1)
except Exception as err:
    print("Your file stopped with an error before I could check it:")
    print(f"  {type(err).__name__}: {err}")
    print("Hint: read the error, it usually names the line. IndentationError means the lines")
    print("inside a loop need 4 spaces. SyntaxError often means a missing colon after for/while/if.")
    print(f"SCORE: 0/{TOTAL}")
    sys.exit(1)


def loops_of(kind):
    return [n for n in ast.walk(tree) if isinstance(n, kind)]


def for_over(name):
    """for loops that go through the variable `name`."""
    return [n for n in loops_of(ast.For) if isinstance(n.iter, ast.Name) and n.iter.id == name]


def for_range():
    return [n for n in loops_of(ast.For) if isinstance(n.iter, ast.Call)
            and isinstance(n.iter.func, ast.Name) and n.iter.func.id == "range"]


def has_break(node):
    return any(isinstance(n, ast.Break) for n in ast.walk(node))


results_list = []  # (skill, passed, message)


def check(skill, passed, ok_msg, hint):
    passed = bool(passed)
    results_list.append((skill, passed, ok_msg if passed else hint))


# 1. for loop over tasks
want1 = ["Working on: search the web", "Working on: read the page", "Working on: write a summary"]
if not for_over("tasks"):
    hint1 = "Loop through the list: for task in tasks:  then print inside it (indented 4 spaces)."
elif not all(w in lines for w in want1):
    hint1 = 'Inside the loop print with an f-string: print(f"Working on: {task}"). Check the exact words.'
else:
    hint1 = ""
check("loops", bool(for_over("tasks")) and all(w in lines for w in want1),
      "looped through tasks and printed each one", hint1)

# 2. range
want2 = ["Try 1", "Try 2", "Try 3"]
ok2 = bool(for_range()) and all(w in lines for w in want2) and "Try 0" not in lines and "Try 4" not in lines
if not for_range():
    hint2 = "Use for i in range(3):  and print inside it."
elif "Try 0" in lines:
    hint2 = 'range starts at 0, so add 1 when you print: print(f"Try {i + 1}")'
elif not all(w in lines for w in want2) or "Try 4" in lines:
    hint2 = "It should print Try 1, Try 2, Try 3 exactly. Check the number inside range()."
else:
    hint2 = ""
check("loops", ok2, "used range to print Try 1 to 3", hint2)

# 3. counting errors
errors = names.get("errors")
counts_in_loop = any(
    isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == "errors"
    or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "errors" for t in n.targets)
    for loop in for_over("results") for n in ast.walk(loop))
other3 = safe_run(results=["error", "error", "error", "ok"])
if not for_over("results"):
    hint3 = "Start with errors = 0, then loop: for r in results:  and use an if inside."
elif not counts_in_loop:
    hint3 = 'Inside the loop: if r == "error":  then add one with errors += 1'
elif errors != 2 or "Errors: 2" not in lines:
    hint3 = f'errors ended up as {errors!r}. After the loop (not indented) print(f"Errors: {{errors}}")'
elif other3 is None or "Errors: 3" not in other3:
    hint3 = "Works for this list, but make sure you're counting with the loop, not typing the number."
else:
    hint3 = ""
check("loops", for_over("results") and counts_in_loop and errors == 2 and "Errors: 2" in lines
      and other3 is not None and "Errors: 3" in other3,
      "counted the errors with a loop: Errors: 2", hint3)

# 4. while loop with max_steps
want4 = [f"Step {i}" for i in range(1, 6)] + ["Stopped after 5 steps"]
other4 = safe_run(max_steps=3)
want4b = ["Step 1", "Step 2", "Step 3", "Stopped after 3 steps"]
has_while = bool(loops_of(ast.While))
in_order = [l for l in lines if l.startswith("Step ") or l.startswith("Stopped after")]
if not has_while:
    hint4 = "Start with steps = 0, then: while steps < max_steps:"
elif in_order != want4:
    if "Step 0" in lines:
        hint4 = "Add 1 to steps BEFORE you print, so it starts at Step 1."
    elif "Stopped after 5 steps" not in lines:
        hint4 = 'After the loop (not indented), print(f"Stopped after {steps} steps")'
    else:
        hint4 = f"I saw {in_order}. It should be Step 1 to Step 5, then Stopped after 5 steps (once)."
elif other4 is None or [l for l in other4 if l.startswith("Step ") or l.startswith("Stopped after")] != want4b:
    hint4 = "Use max_steps in the while condition and the f-string, not the number 5."
else:
    hint4 = ""
check("loops", has_while and in_order == want4 and other4 is not None
      and [l for l in other4 if l.startswith("Step ") or l.startswith("Stopped after")] == want4b,
      "while loop ran 5 steps and stopped at max_steps", hint4)

# 5. inbox with break
inbox_loops = for_over("inbox")
reading = [l for l in lines if l.startswith("Reading:") or l == "Got STOP, stopping."]
want5 = ["Reading: hi", "Reading: what's the weather?", "Got STOP, stopping."]
other5 = safe_run(inbox=["a", "STOP", "b", "c"])
want5b = ["Reading: a", "Got STOP, stopping."]
if not inbox_loops:
    hint5 = "Loop through it: for msg in inbox:"
elif not any(has_break(l) for l in inbox_loops):
    hint5 = 'Inside the loop: if msg == "STOP":  print the stop line, then break'
elif reading != want5:
    hint5 = (f"I saw {reading}. Check the order inside the loop: first check for STOP "
             "(print + break), then print Reading: for normal messages.")
elif other5 is None or [l for l in other5 if l.startswith("Reading:") or l == "Got STOP, stopping."] != want5b:
    hint5 = 'Use msg == "STOP" in your if, not a position number.'
else:
    hint5 = ""
check("loops", bool(inbox_loops) and any(has_break(l) for l in inbox_loops) and reading == want5
      and other5 is not None
      and [l for l in other5 if l.startswith("Reading:") or l == "Got STOP, stopping."] == want5b,
      "read the inbox and stopped at STOP with break", hint5)

# 6. never read past STOP
check("conditions", "Reading: are you there?" not in lines and "Reading: STOP" not in lines
      and "Got STOP, stopping." in lines,
      "the agent never read STOP or anything after it",
      "The agent shouldn't print Reading: STOP or anything after it. Put the STOP check first, with break.")

# Report
print(f"Checking {target.name}\n")
for i, (skill, passed, msg) in enumerate(results_list, 1):
    mark = "PASS" if passed else "FAIL"
    print(f"{mark}  {i}. [{skill}] {msg}")
score = sum(p for _, p, _ in results_list)
print(f"\nSCORE: {score}/{len(results_list)}")
if score == len(results_list):
    print("All done. Nice work!")
