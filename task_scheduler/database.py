"""Database module for task persistence."""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional


class Database:
    """SQLite database handler for tasks."""

    def __init__(self, db_path: str = "tasks.db") -> None:
        """Initialize database connection and create tables if they don't exist.

        Args:
            db_path (str): Path to the SQLite database file. Defaults to 'tasks.db'.
        """
        self.db_path = db_path
        self._create_tables()

        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 10),
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'failed'))
                    category TEXT DEFAULT 'general' CHECK(category IN ('general', 'work', 'personal'))
                )
            """)

    def _create_tables(self) -> None:
        """Create the tasks table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 10),
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'failed'))
                )
            """)
            conn.commit()

    def add_task(self, name: str, priority: int, due_date: str) -> int:
        """
        Add a task to the database.

        Args:
            name (str): Task name.
            priority (int): Priority (1-10, lower is higher priority).
            due_date (str): Due date in 'YYYY-MM-DD HH:MM' format.

        Returns:
            int: The inserted task ID.

        Raises:
            ValueError: If inputs are invalid (e.g., bad date format, priority out of range).
            sqlite3.Error: If database operation fails.
        """
        try:
            datetime.strptime(due_date, "%Y-%m-%d %H:%M")  # Validate date format
            if not 1 <= priority <= 10:
                raise ValueError("Priority must be between 1 and 10")
            if not name.strip():
                raise ValueError("Task name cannot be empty")
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}") from e

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (name, priority, due_date) VALUES (?, ?, ?)",
                (name, priority, due_date),
            )
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, status: Optional[str] = None) -> List[Tuple]:
        """
        Fetch tasks from the database.

        Args:
            status (Optional[str]): Filter by status ('pending', 'completed', 'failed'). Defaults to None.

        Returns:
            List[Tuple]: List of tasks as (id, name, priority, due_date, status).
        """
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT id, name, priority, due_date, category FROM tasks"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += " ORDER BY priority ASC, due_date ASC"
            return conn.execute(query, params).fetchall()
        
    def get_task_by_id(self, task_id: int) -> tuple:
        """
        Fetch a task by its ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            return cursor.fetchone()

    def update_task_status(self, task_id: int, status: str) -> None:
        """
        Update the status of a task.

        Args:
            task_id (int): The task ID to update.
            status (str): New status ('pending', 'completed', 'failed').
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status, task_id),
            )
            conn.commit()

    def reschedule_task(self, task_id: int, new_due_date: str) -> None:
        """
        Reschedule a task to a new due date.

        Args:
            task_id (int): The task ID to reschedule.
            new_due_date (str): New due date in 'YYYY-MM-DD HH:MM' format.

        Raises:
            ValueError: If date format is invalid or task not found.
            sqlite3.Error: If database operation fails.
        """
        try:
            datetime.strptime(new_due_date, "%Y-%m-%d %H:%M")
        except ValueError as e:
            raise ValueError("Invalid due date format") from e

        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "UPDATE tasks SET due_date = ? WHERE id = ?",
                (new_due_date, task_id),
            )
            conn.commit()
            if result.rowcount == 0:
                raise ValueError(f"Task ID {task_id} not found")
            

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id (int): The ID of the task to delete.

        Returns:
            bool: True if the task was deleted, False if not found.
        """
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0