"""Command-line interface for the Task Scheduler."""

import sys
import argparse
from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.progress import Progress
from tabulate import tabulate
from dotenv import load_dotenv
from task_scheduler.database import Database
from task_scheduler.scheduler import Scheduler

# Load environment variables
load_dotenv()

console = Console()


def display_menu() -> None:
    """Display the main menu with styled options."""
    console.print(
        Panel.fit(
            "[bold cyan]Task Scheduler[/bold cyan]\nEffortlessly manage your tasks!",
            title="Welcome",
            border_style="bright_green",
        )
    )
    console.print("[yellow]Choose an Action:[/yellow]")
    console.print("1. [green]Add Task[/green] - Create a new task")
    console.print("2. [blue]List Tasks[/blue] - View all tasks")
    console.print("3. [magenta]Reschedule Task[/magenta] - Update a task's schedule")
    console.print("4. [red]Delete Task[/red] - Remove a task")
    console.print("5. [blue]View Task Details[/blue] - See task info")
    console.print("6. [cyan]Run Scheduler[/cyan] - Execute pending tasks")
    console.print("7. [white]Exit[/white] - Close the program")


def list_tasks(db: Database) -> None:
    """Display tasks with filtering and sorting options.

    Args:
        db: Database instance to query tasks from.
    """
    tasks: List[Tuple] = db.get_tasks()
    if not tasks:
        console.print("[yellow]No tasks available.[/yellow]")
        return

    console.print("[blue]List Options:[/blue]")
    filter_choice = Prompt.ask(
        "Filter by status (all, pending, completed, failed)", default="all"
    )
    sort_choice = Prompt.ask("Sort by (id, priority, due_date)", default="id")

    if filter_choice != "all":
        tasks = [task for task in tasks if task[4] == filter_choice]

    if sort_choice == "priority":
        tasks.sort(key=lambda x: x[2])
    elif sort_choice == "due_date":
        tasks.sort(key=lambda x: x[3])

    table = Table(title="Your Tasks", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Priority", style="yellow", justify="right")
    table.add_column("Due Date", style="blue")
    table.add_column("Category", style="bright_cyan")
    table.add_column("Status", style="white")

    for task in tasks:
        status_style = "[green]" if task[4] == "pending" else "[red]"
        table.add_row(
            str(task[0]),
            task[1],
            str(task[2]),
            task[3],
            task[5],
            f"{status_style}{task[4]}[/]",
        )
    console.print(table)


def add_task(db: Database) -> None:
    """Guide the user to add a new task interactively.

    Args:
        db: Database instance to store the task.
    """
    console.print("[bold green]New Task Creation[/bold green]")
    name = Prompt.ask("Task Name")
    priority = IntPrompt.ask(
        "Priority (1-10)", default=5, choices=[str(i) for i in range(1, 11)]
    )
    due_date = Prompt.ask("Due Date (YYYY-MM-DD HH:MM)", default="2025-03-28 09:00")
    category = Prompt.ask("Category (general, work, personal)", default="general")

    try:
        task_id = db.add_task(name, priority, due_date, category)
        console.print(f"[green]Success! Task added with ID: {task_id}[/green]")
    except ValueError as e:
        console.print(f"[red]Oops: {e}[/red]")


def reschedule_task(db: Database) -> None:
    """Reschedule a task with user input.

    Args:
        db: Database instance to update the task.
    """
    console.print("[bold magenta]Reschedule Task[/bold magenta]")
    task_id = IntPrompt.ask("Task ID")
    new_due_date = Prompt.ask("New Due Date (YYYY-MM-DD HH:MM)", default="2025-03-28 11:00")

    try:
        db.reschedule_task(task_id, new_due_date)
        console.print(f"[green]Task {task_id} updated to {new_due_date}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


def delete_task(db: Database) -> None:
    """Delete a task with confirmation.

    Args:
        db: Database instance to remove the task from.
    """
    console.print("[bold red]Delete a Task[/bold red]")
    task_id = IntPrompt.ask("Task ID")
    if Confirm.ask(f"Really delete task {task_id}?"):
        if db.delete_task(task_id):
            console.print(f"[green]Task {task_id} removed.[/green]")
        else:
            console.print(f"[red]Task {task_id} not found.[/red]")


def view_task_details(db: Database) -> None:
    """Display detailed info for a single task.

    Args:
        db: Database instance to query the task from.
    """
    console.print("[bold blue]View Task Details[/bold blue]")
    task_id = IntPrompt.ask("Task ID")
    task = db.get_task_by_id(task_id)

    if not task:
        console.print(f"[red]Task {task_id} not found.[/red]")
        return

    panel = Panel(
        f"[cyan]ID:[/cyan] {task['id']}\n"
        f"[green]Name:[/green] {task['name']}\n"
        f"[yellow]Priority:[/yellow] {task['priority']}\n"
        f"[blue]Due Date:[/blue] {task['due_date']}\n"
        f"[bright_cyan]Category:[/bright_cyan] {task['category']}\n"
        f"[white]Status:[/white] {task['status']}",
        title=f"Task {task_id}",
        border_style="bright_blue",
    )
    console.print(panel)


def run_scheduler(scheduler: Scheduler) -> None:
    """Execute the scheduler with a progress bar.

    Args:
        scheduler: Scheduler instance to run tasks.
    """
    console.print("[bold cyan]Starting Scheduler[/bold cyan]")
    queue = scheduler.build_queue()
    if not queue:
        console.print("[yellow]No pending tasks.[/yellow]")
        return

    with Progress() as progress:
        task_bar = progress.add_task("[cyan]Processing tasks...", total=len(queue))
        while queue:
            priority, due_ts, task_id = queue.pop(0)
            name = scheduler.db.get_task_by_id(task_id)["name"]
            scheduler._execute_task(task_id, name)
            progress.update(task_bar, advance=1)


def main() -> None:
    """Run the interactive CLI or handle legacy commands."""
    db = Database()
    scheduler = Scheduler(max_workers=int(os.getenv("MAX_WORKERS", 3)))

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Task Scheduler CLI")
        subparsers = parser.add_subparsers(dest="command")

        add_parser = subparsers.add_parser("add", help="Add a new task")
        add_parser.add_argument("name", help="Task name")
        add_parser.add_argument("priority", type=int, help="Priority (1-10)")
        add_parser.add_argument("due_date", help="Due date (YYYY-MM-DD HH:MM)")
        add_parser.add_argument("--category", default="general", help="Task category")

        subparsers.add_parser("list", help="List all tasks")
        subparsers.add_parser("run", help="Run the scheduler")

        reschedule_parser = subparsers.add_parser("reschedule", help="Reschedule a task")
        reschedule_parser.add_argument("id", type=int, help="Task ID")
        reschedule_parser.add_argument("new_due_date", help="New due date (YYYY-MM-DD HH:MM)")

        args = parser.parse_args()

        if args.command == "add":
            try:
                task_id = db.add_task(args.name, args.priority, args.due_date, args.category)
                print(f"Task added with ID: {task_id}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif args.command == "list":
            tasks = db.get_tasks()
            if not tasks:
                print("No tasks found.")
            else:
                print(
                    tabulate(
                        tasks,
                        headers=["ID", "Name", "Priority", "Due Date", "Status", "Category"],
                        tablefmt="grid",
                    )
                )
        elif args.command == "run":
            scheduler.run()
        elif args.command == "reschedule":
            try:
                db.reschedule_task(args.id, args.new_due_date)
                print(f"Task {args.id} rescheduled to {args.new_due_date}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            parser.print_help()
        return

    while True:
        display_menu()
        choice = IntPrompt.ask("Select an option", choices=[str(i) for i in range(1, 8)], default="1")
        if choice == 1:
            add_task(db)
        elif choice == 2:
            list_tasks(db)
        elif choice == 3:
            reschedule_task(db)
        elif choice == 4:
            delete_task(db)
        elif choice == 5:
            view_task_details(db)
        elif choice == 6:
            run_scheduler(scheduler)
        elif choice == 7:
            console.print("[bold white]See you next time![/bold white]")
            break
        console.print("\n")


if __name__ == "__main__":
    main()