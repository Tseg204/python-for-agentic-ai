"""Checks your Session 4 exercise.

Run:  python3 lessons/session-04/check.py
(Optional: pass a different file path to check that file instead.)
"""

import ast
import contextlib
import io
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
    print("Hint: read the error, it usually names the line. IndexError means you asked for")
    print("a position that isn't there. AttributeError on None usually means x = x.append(...).")
    print(f"SCORE: 0/{TOTAL}")
    sys.exit(1)

lines = [line.rstrip() for line in printed.getvalue().splitlines()]
tree = ast.parse(target.read_text())
START = ["search the web", "read the page", "write a summary"]


def method_calls(obj, method):
    """How many times obj.method(...) is called in the file."""
    count = 0
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == method and isinstance(node.func.value, ast.Name)
                and node.func.value.id == obj):
            count += 1
    return count


def list_literal(var_name):
    """The first list written straight into var_name, as Python values (or None)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            if any(isinstance(t, ast.Name) and t.id == var_name for t in node.targets):
                try:
                    return ast.literal_eval(node.value)
                except ValueError:
                    return None
    return None


def uses_negative_index(obj):
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == obj:
            s = node.slice
            if isinstance(s, ast.UnaryOp) and isinstance(s.op, ast.USub):
                return True
            if isinstance(s, ast.Constant) and isinstance(s.value, int) and s.value < 0:
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


results = []  # (skill, passed, message)


def check(skill, passed, ok_msg, hint):
    results.append((skill, passed, ok_msg if passed else hint))


# 1. tasks list made and its length printed
made = list_literal("tasks")
if made is None:
    hint1 = ('I can\'t find tasks = [ ... ]. Make it with square brackets and commas: '
             'tasks = ["search the web", "read the page", "write a summary"]')
elif made != START:
    hint1 = f"tasks starts as {made!r}. Check the spelling, order and commas of the three items."
else:
    hint1 = "Now print how many items it has: print(len(tasks))"
check("lists", made == START and "3" in lines[:3],
      "tasks has the 3 items and you printed 3", hint1)

# 2. first and last
first_ok = "First: search the web" in lines
last_ok = "Last: write a summary" in lines
if not (first_ok and last_ok):
    hint2 = ('Print them like this: print(f"First: {tasks[0]}"). Remember the first item is [0]. '
             'Check the exact words too, with a capital F and L and a space after the colon.')
elif not uses_negative_index("tasks"):
    hint2 = "Right output! But use the count-from-the-end trick for the last one: tasks[-1]."
else:
    hint2 = ""
check("lists", first_ok and last_ok and uses_negative_index("tasks"),
      "printed the first item and used tasks[-1] for the last", hint2)

# 3. append + print the list
full = "['search the web', 'read the page', 'write a summary', 'send the email']"
if method_calls("tasks", "append") == 0:
    hint3 = 'Add it with tasks.append("send the email"), then print(tasks).'
elif full not in lines:
    hint3 = "After the append, print the whole list: print(tasks). Check the spelling of \"send the email\"."
else:
    hint3 = ""
check("lists", method_calls("tasks", "append") >= 1 and full in lines,
      "appended 'send the email' and printed all 4 tasks", hint3)

# 4. history
history = names.get("history")
hist_lit = list_literal("history")
want_hist = ["user: hi", "agent: hello! how can I help?"]
if hist_lit is None:
    hint4 = "Start with an empty list: history = []"
elif hist_lit != []:
    hint4 = "Make history empty first (history = []), then add each message with history.append(...)."
elif method_calls("history", "append") < 2:
    hint4 = "Add both messages with history.append(...), one line each."
elif history != want_hist:
    hint4 = f"history is {history!r}. Check the spelling of both messages, they must match exactly."
else:
    hint4 = 'Now print it with len inside an f-string: print(f"Messages: {len(history)}")'
check("lists", hist_lit == [] and method_calls("history", "append") >= 2
      and history == want_hist and "Messages: 2" in lines,
      "history started empty, got 2 messages, and you printed Messages: 2", hint4)

# 5. pop the first task
done = names.get("done")
tasks = names.get("tasks")
if method_calls("tasks", "pop") == 0:
    hint5 = "Take the first task off with done = tasks.pop(0)  (0 means the front)."
elif done != "search the web":
    hint5 = f"done is {done!r}. pop(0) takes from the front; pop() with nothing takes from the end."
elif "Done: search the web" not in lines or "Left: 3" not in lines:
    hint5 = 'Print both lines: print(f"Done: {done}") and print(f"Left: {len(tasks)}")'
else:
    hint5 = ""
check("lists", method_calls("tasks", "pop") >= 1 and done == "search the web"
      and tasks == START[1:] + ["send the email"]
      and "Done: search the web" in lines and "Left: 3" in lines,
      "popped the first task into done and printed Done and Left", hint5)

# 6. in + if/else
has_if = any(isinstance(n, ast.If) for n in ast.walk(tree))
uses_in = any(isinstance(n, ast.Compare) and any(isinstance(o, ast.In) for o in n.ops) for n in ast.walk(tree))
cases = {"send_money": "Blocked", "delete_files": "Blocked", "search": "Allowed"}
bad = []
for req, want in cases.items():
    out = lines if req == "send_money" else run_with(tool_request=req)
    other = "Allowed" if want == "Blocked" else "Blocked"
    if out is None or want not in out or other in out:
        bad.append((req, want))
if not has_if or not uses_in:
    hint6 = "Use in with an if: if tool_request in blocked_tools:"
elif bad:
    hint6 = f"When tool_request is {bad[0][0]!r} it should print {bad[0][1]}. Check your if and else."
else:
    hint6 = ""
check("conditions", has_if and uses_in and not bad,
      "Blocked for blocked tools, Allowed for others", hint6)

# Report
print(f"Checking {target.name}\n")
for i, (skill, passed, msg) in enumerate(results, 1):
    mark = "PASS" if passed else "FAIL"
    print(f"{mark}  {i}. [{skill}] {msg}")
score = sum(p for _, p, _ in results)
print(f"\nSCORE: {score}/{len(results)}")
if score == len(results):
    print("All done. Nice work!")
