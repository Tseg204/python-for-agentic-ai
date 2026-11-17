# Session 3 exercise: teach your agent when to stop
#
# Do each TODO below. When you're done, tell Claude "done" and it will run the checker.
# You can run this file yourself any time with:  python3 lessons/session-03/exercise.py

# These come from your agent's last AI call. Leave these lines as they are.
tokens_used = 1200          # how many tokens (small chunks of text) the AI used
price_per_token = 0.002     # dollars per token
user_reply = "  Yes "       # what the user typed when asked "Run the task?"


# TODO 1: Make two number variables (no quotes!):
#         step = 3
#         max_steps = 5
step = 3
max_steps = 5

# TODO 2: Make a variable called steps_left that is max_steps minus step.
#         Use the variables, don't just type 2.
#         Then print it with an f-string so it reads:  Steps left: 2
steps_left = max_steps - step
print(f"Steps left: {steps_left}")

# TODO 3: Make a variable called cost: tokens_used times price_per_token.
#         (Times is * in Python.) Then print cost.
cost = tokens_used * price_per_token
print(cost)

# TODO 4: Make a variable called is_done that answers the question
#         "is step bigger than or equal to max_steps?"  Use a comparison.
#         Then print is_done. (It should print False for now.)
is_done = step >= max_steps
print(is_done)

# TODO 5: Write an if / else:
#         if the agent is done (step bigger than or equal to max_steps), print:  Stop
#         otherwise print:  Keep going
#         Remember the colons and the 4-space indents.
if is_done:
    print("Stop")
else:
    print("Keep going")

# TODO 6: Write another if / else about user_reply.
#         The user might type "yes", "YES" or "  Yes " (with spaces).
#         Clean user_reply first (hint: last session's string tools!),
#         then check if it equals "yes".
#         If it does, print:  Running the task
#         Otherwise print:    Cancelled
clean_user_reply = user_reply.lower().strip()
print(clean_user_reply)
if clean_user_reply == "yes":
    print("Running the task")
else:
    print("Cancelled")