# Task Scheduler with Priority Queue

A Python-based task scheduler that manages tasks with priorities and deadlines, executing them concurrently using a priority queue.

## Features
- Add tasks with name, priority (1-10), due date, and category (general, work, personal).
- Execute up to 3 tasks concurrently with simulated delays and email notifications.
- Persist tasks in SQLite with status tracking (pending, completed, failed).
- Interactive CLI with rich UI and legacy commands: `add`, `list`, `run`, `reschedule`.
- Logging for debugging and audit trails.

## Setup
1. Clone the repository: `git clone https://github.com/MachariaP/task_scheduler.git`
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure `config.json` with email settings (optional).
6. Run the scheduler: `python -m task_scheduler.cli`

## Usage
### Interactive Mode
Launch without arguments: `python -m task_scheduler.cli`
- Use the menu to add, list, reschedule, delete, view details, or run tasks.

### CLI Commands
- Add a task: `python -m task_scheduler.cli add "Backup DB" 1 "2025-03-25 10:00" --category work`
- List tasks: `python -m task_scheduler.cli list`
- Run scheduler: `python -m task_scheduler.cli run`
- Reschedule: `python -m task_scheduler.cli reschedule 1 "2025-03-26 12:00"`

## Testing
Run tests: `python -m unittest discover tests`

## Requirements
- Python 3.9+
- SQLite (built-in)
- `rich` (for enhanced UI)
- `tabulate` (for CLI tables)
- `pyperclip` (optional, for README generation)

## Configuration
Edit `config.json` for concurrency and email:
```json
{
    "max_workers": 3,
    "smtp_host": "smtp.example.com",
    "smtp_user": "your_email@example.com",
    "smtp_pass": "your_password"
}