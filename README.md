# Python for Agentic AI

I'm learning Python from scratch, with Claude as my teacher, aiming to build AI agents. This repo is the whole course: the lessons, the exercises, the checkers, and my actual answers as I go.

## How it works

- 20 sessions, 30 minutes each, about 3-4 a week.
- Each session: a quick warm-up on weak spots, a visual lesson page, a hands-on exercise that a script checks, and a 5-question quiz.
- Lessons are made one session at a time, so this repo grows as I go. One commit per session.
- Scores are tracked per skill, and at the end I get a report on what to work on. (My own scores stay private.)

See [curriculum.md](curriculum.md) for all 20 sessions, from `print` to a working AI agent.

## Take the course yourself

You need [Claude Code](https://claude.com/claude-code) and Python 3.

1. Clone this repo and open the folder in Claude Code.
2. Copy `progress/progress.example.json` to `progress/progress.json`.
3. Say **"start session"**. Claude reads [CLAUDE.md](CLAUDE.md), which holds the teaching rules, and picks up where you left off.
4. Say **"show my progress"** any time for your dashboard.

Heads up: the `exercise.py` files contain my answers. To start fresh, clear the code under each TODO, or delete the `lessons/` folder and Claude will make new lessons as you go.

From session 13 you'll need an Anthropic API key. Put it in a `.env` file as `ANTHROPIC_API_KEY=...` (this file is git-ignored). Never commit it.

## Layout

- `lessons/session-NN/`: `lesson.html` (open in a browser), `exercise.py`, `check.py`
- `progress/build_dashboard.py`: turns your `progress.json` into a dashboard
- `capstone/`: the final project

License: MIT
