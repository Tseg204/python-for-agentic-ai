# Session 2 exercise: build your agent's first prompt
#
# Do each TODO below. When you're done, tell Claude "done" and it will run the checker.
# You can run this file yourself any time with:  python3 lessons/session-02/exercise.py

# This is what a user typed into your agent. Messy, right? Leave this line as it is.
messy_input = "   Book a TABLE for two   "


# TODO 1: Make a variable called user_name with a name in quotes.
#         Example idea: "Sam"
user_name = "Sam"

# TODO 2: Make a variable called greeting by gluing three strings with +:
#         "Hello, "   then   user_name   then   "!"
#         So for Sam it would be:  Hello, Sam!
#         Then print greeting.
greeting = "Hello, " + user_name + "!"
print(greeting)

# TODO 3: Make a variable called clean_input.
#         Use .strip() on messy_input to cut off the spaces at both ends.
clean_input = messy_input.strip()

# TODO 4: Make a variable called quiet_input.
#         Use .lower() on clean_input so it's all small letters.
quiet_input = clean_input.lower()

# TODO 5: Make a variable called prompt using an f-string (don't forget the f!).
#         It should read exactly like this, with your variables filled in:
#             Help <user_name> with this task: <quiet_input>
#         Then print prompt.
prompt = f"Help {user_name} with this task: {quiet_input}"
print(prompt)

# TODO 6: Make step = 2 and max_steps = 5 (numbers, no quotes).
#         Then make a variable called status with an f-string so it reads:
#             Step 2 of 5
#         Then print status.
step = 2
max_steps = 5
status = f"Step {step} of {max_steps}"
print(status)