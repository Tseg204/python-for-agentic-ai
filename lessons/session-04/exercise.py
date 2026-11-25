# Session 4 exercise: give your agent a to-do list and a memory
#
# Do each TODO below. When you're done, tell Claude "done" and it will run the checker.
# You can run this file yourself any time with:  python3 lessons/session-04/exercise.py

# Your agent's safety settings. Leave these lines as they are.
blocked_tools = ["delete_files", "send_money"]   # tools the agent must never use
tool_request = "send_money"                      # the tool the AI just asked to use


# TODO 1: Make a list called tasks with these three items, in this order:
#         "search the web", "read the page", "write a summary"
#         Then print how many items are in it (hint: len). It should print 3.
tasks = ["search the web", "read the page", "write a summary"]
print(len(tasks))

# TODO 2: Print the first task and the last task with f-strings, so it reads:
#         First: search the web
#         Last: write a summary
#         For the last one, use the "count from the end" trick, not [2].
print(f"First: {tasks[0]}\nLast: {tasks[-1]}")  

# TODO 3: A new job came in. Add "send the email" to the end of tasks.
#         Then print the whole list.
tasks.append("send the email")
print(tasks)

# TODO 4: Start the agent's memory: make an EMPTY list called history.
#         Add two messages to it, one at a time:
#         "user: hi"   and then   "agent: hello! how can I help?"
#         Then print:  Messages: 2   (use len inside an f-string, don't just type 2)
history = []
history.append('user: hi')
history.append('agent: hello! how can I help?')
print(f'Messages: {len(history)}')

# TODO 5: The agent finished the first task. Take it off the front of tasks
#         and save it in a variable called done. Then print these two lines:
#         Done: search the web
#         Left: 3          (use len again)
done = tasks.pop(0)
print(f'Done: {done}\nLeft: {len(tasks)}')

# TODO 6: Safety check. Write an if / else:
#         if tool_request is in blocked_tools, print:  Blocked
#         otherwise print:  Allowed
if tool_request in blocked_tools:
    print('Blocked')
else:
    print('Allowed')