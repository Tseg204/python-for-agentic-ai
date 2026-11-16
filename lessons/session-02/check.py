"""Checks your Session 2 exercise.

Run:  python3 lessons/session-02/check.py
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
    print("Hint: read the error, it usually names the line. Look for a missing quote,")
    print("a missing bracket, or gluing a number to text with +.")
    print(f"SCORE: 0/{TOTAL}")
    sys.exit(1)

output = printed.getvalue()
lines = [line.rstrip() for line in output.splitlines()]


def uses_fstring(var_name):
    """True if the variable is set from an f-string somewhere in the file."""
    tree = ast.parse(target.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.JoinedStr):
            if any(isinstance(t, ast.Name) and t.id == var_name for t in node.targets):
                return True
    return False


results = []  # (skill, passed, message)


def check(skill, passed, ok_msg, hint):
    results.append((skill, passed, ok_msg if passed else hint))


# 1. user_name
name = names.get("user_name")
name_ok = isinstance(name, str) and name.strip() != ""
check("strings", name_ok,
      f"user_name is {name!r}",
      "I can't find user_name as text. Make it like: user_name = \"Sam\" (with quotes).")

# 2. greeting with +
greeting = names.get("greeting")
want = f"Hello, {name}!" if name_ok else None
check("strings", want is not None and greeting == want and want in lines,
      f"greeting is {greeting!r} and was printed",
      "greeting should be \"Hello, \" + user_name + \"!\" (note the space after the comma), "
      "and then print(greeting).")

# 3. strip
clean = names.get("clean_input")
check("strings", clean == "Book a TABLE for two",
      "clean_input has no spaces at the ends",
      "clean_input should be messy_input.strip(). The brackets () at the end matter.")

# 4. lower
quiet = names.get("quiet_input")
check("strings", quiet == "book a table for two",
      "quiet_input is all small letters",
      "quiet_input should be clean_input.lower(). Use clean_input, not messy_input, "
      "or the spaces come back.")

# 5. prompt f-string
prompt = names.get("prompt")
want_prompt = f"Help {name} with this task: {quiet}" if name_ok and quiet else None
prompt_ok = want_prompt is not None and prompt == want_prompt and uses_fstring("prompt")
if prompt is not None and "{" in str(prompt):
    hint5 = "Your prompt still has { } in it. That means the f before the quote is missing."
elif prompt is not None and not uses_fstring("prompt"):
    hint5 = "prompt has the right idea, but build it with an f-string: f\"Help {user_name} ...\""
else:
    hint5 = ("prompt should read exactly: Help <user_name> with this task: <quiet_input>. "
             "Check spaces and the colon, and print(prompt).")
check("f-strings", prompt_ok and want_prompt in lines,
      f"prompt is {prompt!r} and was printed",
      hint5)

# 6. status with numbers
step = names.get("step")
max_steps = names.get("max_steps")
status = names.get("status")
nums_ok = type(step) is int and type(max_steps) is int
if not nums_ok:
    hint6 = "step and max_steps should be numbers with no quotes: step = 2 and max_steps = 5."
elif status is not None and "{" in str(status):
    hint6 = "status still has { } in it. Add the f before the opening quote."
else:
    hint6 = "status should be f\"Step {step} of {max_steps}\" and then print(status)."
check("f-strings",
      nums_ok and status == f"Step {step} of {max_steps}" == "Step 2 of 5"
      and uses_fstring("status") and status in lines,
      "status reads 'Step 2 of 5' and was printed",
      hint6)

# Report
print(f"Checking {target.name}\n")
for i, (skill, passed, msg) in enumerate(results, 1):
    mark = "PASS" if passed else "FAIL"
    print(f"{mark}  {i}. [{skill}] {msg}")
score = sum(p for _, p, _ in results)
print(f"\nSCORE: {score}/{len(results)}")
if score == len(results):
    print("All done. Nice work!")
