# Task Scheduler with Priority Queue

A Python-based task scheduler that manages tasks with priorities and deadlines, executing them concurrently using a priority queue.

## Features
- Add tasks with name, priority (1-10), and due date.
- Execute up to 3 tasks concurrently with simulated delays.
- Persist tasks in SQLite with status tracking.
- CLI commands: `add`, `list`, `run`, `reschedule`.
- Logging for debugging and audit trails.

## Setup
1. Clone the repository: `git clone <repo-url>`
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the scheduler: `python -m task_scheduler.cli`

## Usage
- Add a task: `python -m task_scheduler.cli add "Backup DB" 1 "2025-03-25 10:00"`
- List tasks: `python -m task_scheduler.cli list`
- Run scheduler: `python -m task_scheduler.cli run`
- Reschedule: `python -m task_scheduler.cli reschedule 1 "2025-03-26 12:00"`

## Testing
Run tests: `python -m unittest discover tests`

## Requirements
- Python 3.9+
- SQLite (built-in)
- tabulate (for CLI tables)
