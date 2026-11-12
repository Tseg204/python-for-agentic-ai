# Session 1 exercise: set up your first agent's settings
#
# Do each TODO below. Delete the "# TODO" line once you've done it if you like.
# When you're done, tell Claude "done" and it will run the checker.
# You can run this file yourself any time with:  python3 lessons/session-01/exercise.py


# TODO 1: Print the exact text:  Hello, agent!
print("Hello, agent!")

# TODO 2: Make a variable called agent_name and give it a name in quotes.
#         Example idea: "Scout"
agent_name = "Scout"

# TODO 3: Make a variable called max_steps and set it to the number 5 (no quotes!).
max_steps = 5

# TODO 4: Make a variable called task with a short job for the agent, in quotes.
#         Example idea: "Find three good pizza places"
task = "Help me learn python for agentic AI work flow."

# TODO 5: Print one line that uses agent_name and max_steps, using commas, like:
#         print("Agent", agent_name, "can take", max_steps, "steps")
print("Agent", agent_name, "completed", max_steps, "tasks.")

# TODO 6: Make a variable called steps_used and set it to 0.
#         On the next line, add 1 to it:  steps_used = steps_used + 1
#         Then print steps_used.
steps_used = 0
steps_used = steps_used + 1
print(steps_used)