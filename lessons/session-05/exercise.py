# Session 5 exercise: give your agent its loop
#
# Do each TODO below. When you're done, tell Claude "done" and it will run the checker.
# You can run this file yourself any time with:  python3 lessons/session-05/exercise.py
# If it ever gets stuck and keeps running, press Ctrl + C to stop it.

# Your agent's data. Leave these lines as they are.
tasks = ["search the web", "read the page", "write a summary"]
results = ["ok", "error", "ok", "ok", "error"]   # what each tool call returned
inbox = ["hi", "what's the weather?", "STOP", "are you there?"]
max_steps = 5                                     # safety limit for the agent


# TODO 1: Use a for loop to go through tasks and print each one like this:
#         Working on: search the web
#         Working on: read the page
#         Working on: write a summary
for task in tasks:
    print(f'Working on: {task}')

# TODO 2: Use a for loop with range to print:
#         Try 1
#         Try 2
#         Try 3
#         (Hint: range(3) gives 0, 1, 2. What do you add to get 1, 2, 3?)
for i in range(3):
    print(f'Try {i + 1}')

# TODO 3: Count the failed tool calls. Make a variable called errors that starts at 0.
#         Loop through results, and add 1 to errors each time a result is "error".
#         After the loop, print:  Errors: 2
#         (Use the variable in an f-string, don't just type 2.)
errors = 0
for result in results:
    if result == "error":
        errors += 1
print(f'Errors: {errors}')
    

# TODO 4: The agent loop! Make a variable called steps that starts at 0.
#         Use a while loop that keeps going while steps is less than max_steps.
#         Inside: add 1 to steps, then print  Step 1, Step 2, ... and so on.
#         After the loop, print:  Stopped after 5 steps
#         (Use max_steps or steps in the f-string, don't just type 5.)
steps = 0
while steps < max_steps:
    steps += 1
    print(f'Step {steps}')
print(f'Stopped after {steps} steps')

# TODO 5: Read the inbox. Loop through inbox and print each message like this:
#         Reading: hi
#         But if the message is "STOP", print  Got STOP, stopping.  and use break
#         so the agent never reads the messages after it.
for msg in inbox:
    if msg == "STOP":
        print(f'Got {msg}, stopping.')
        break
    print(f'Reading: {msg}')
    
