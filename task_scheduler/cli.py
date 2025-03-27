"""Command-line interface for the task scheduler."""

import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from task_scheduler.database import Database
from task_scheduler.scheduler import Scheduler


def display_menu(console: Console) -> None:
    """Display the main menu with styled options."""
    console.print(Panel.fit(
        "[bold cyan]Task Scheduler[/bold cyan]\n"
        "Effortlessly manage your tasks!",
        title="Welcome",
        border_style="bright_green"
    ))
    console.print("[yellow]Choose an Action:[/yellow]")
    console.print("1. [green]Add Task[/green] - Create a new task")
    console.print("2. [blue]List Tasks[/blue] - View all tasks")
    console.print("3. [magenta]Reschedule Task[/magenta] - Update a task's schedule")
    console.print("4. [red]Delete Task[/red] - Remove a task")
    console.print("5. [cyan]Run Scheduler[/cyan] - Execute pending tasks")
    console.print("6. [white]Exit[/white] - Close the program")


def list_tasks(console: Console, db: Database) -> None:
    """Show all tasks in a colorful, formatted table."""
    tasks = db.get_tasks()
    if not tasks:
        console.print("[yellow]No tasks available.[/yellow]")
        return

    table = Table(title="Your Tasks", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Priority", style="yellow", justify="right")
    table.add_column("Due Date", style="blue")
    table.add_column("Status", style="white")

    for task in tasks:
        status_style = "[green]" if task[4] == "pending" else "[red]"
        table.add_row(
            str(task[0]), task[1], str(task[2]), task[3], f"{status_style}{task[4]}[/]"
        )

    console.print(table)


def add_task(console: Console, db: Database) -> None:
    """Guide the user to add a new task."""
    console.print("[bold green]New Task Creation[/bold green]")
    name = Prompt.ask("Task Name")
    priority = IntPrompt.ask("Priority (1-10)", default=5, choices=[str(i) for i in range(1, 11)])
    due_date = Prompt.ask("Due Date (YYYY-MM-DD HH:MM)", default="2025-03-28 09:00")

    try:
        task_id = db.add_task(name, priority, due_date)
        console.print(f"[green]Success! Task added with ID: {task_id}[/green]")
    except ValueError as e:
        console.print(f"[red]Oops: {e}[/red]")


def reschedule_task(console: Console, db: Database) -> None:
    """Reschedule a task with user input."""
    console.print("[bold magenta]Reschedule Task[/bold magenta]")
    task_id = IntPrompt.ask("Task ID")
    new_due_date = Prompt.ask("New Due Date (YYYY-MM-DD HH:MM)", default="2025-03-28 11:00")

    try:
        db.reschedule_task(task_id, new_due_date)
        console.print(f"[green]Task {task_id} updated to {new_due_date}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


def delete_task(console: Console, db: Database) -> None:
    """Delete a task with confirmation."""
    console.print("[bold red]Delete a Task[/bold red]")
    task_id = IntPrompt.ask("Task ID")
    if Confirm.ask(f"Really delete task {task_id}?"):
        if db.delete_task(task_id):
            console.print(f"[green]Task {task_id} removed.[/green]")
        else:
            console.print(f"[red]Task {task_id} not found.[/red]")


def run_scheduler(console: Console, scheduler: Scheduler) -> None:
    """Execute the scheduler for pending tasks."""
    console.print("[bold cyan]Starting Scheduler[/bold cyan]")
    scheduler.run()


def main() -> None:
    """Run the interactive CLI or fallback to legacy commands."""
    console = Console()
    db = Database()
    scheduler = Scheduler()

    # Fallback to legacy CLI if arguments are provided
    if len(sys.argv) > 1:
        import argparse
        from tabulate import tabulate

        parser = argparse.ArgumentParser(description="Task Scheduler CLI")
        subparsers = parser.add_subparsers(dest="command")

        add_parser = subparsers.add_parser("add", help="Add a new task")
        add_parser.add_argument("name", help="Task name")
        add_parser.add_argument("priority", type=int, help="Priority (1-10)")
        add_parser.add_argument("due_date", help="Due date (YYYY-MM-DD HH:MM)")

        subparsers.add_parser("list", help="List all tasks")
        subparsers.add_parser("run", help="Run the scheduler")

        reschedule_parser = subparsers.add_parser("reschedule", help="Reschedule a task")
        reschedule_parser.add_argument("id", type=int, help="Task ID")
        reschedule_parser.add_argument("new_due_date", help="New due date (YYYY-MM-DD HH:MM)")

        args = parser.parse_args()

        if args.command == "add":
            try:
                task_id = db.add_task(args.name, args.priority, args.due_date)
                print(f"Task added with ID: {task_id}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif args.command == "list":
            tasks = db.get_tasks()
            if not tasks:
                print("No tasks found.")
            else:
                print(tabulate(tasks, headers=["ID", "Name", "Priority", "Due Date", "Status"], tablefmt="grid"))
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

    # Interactive menu loop
    while True:
        display_menu(console)
        choice = IntPrompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == 1:
            add_task(console, db)
        elif choice == 2:
            list_tasks(console, db)
        elif choice == 3:
            reschedule_task(console, db)
        elif choice == 4:
            delete_task(console, db)
        elif choice == 5:
            run_scheduler(console, scheduler)
        elif choice == 6:
            console.print("[bold white]See you next time![/bold white]")
            break

        console.print("\n")


if __name__ == "__main__":
    main()