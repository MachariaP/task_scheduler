"""Database module for task persistence."""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


class Database:
    """SQLite database handler for tasks."""

    def __init__(self, db_path: str = "tasks.db") -> None:
        """Initialize database and ensure schema compatibility.

        Args:
            db_path: Path to SQLite database file. Defaults to 'tasks.db'.
        """
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self) -> None:
        """Create the tasks table with constraints if it doesn’t exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 10),
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'failed')),
                    category TEXT DEFAULT 'general' CHECK(category IN ('general', 'work', 'personal'))
                )
            """)
            conn.commit()

    def add_task(self, name: str, priority: int, due_date: str, category: str = "general") -> int:
        """Add a task to the database.

        Args:
            name: Task name.
            priority: Priority level (1-10, lower is higher priority).
            due_date: Due date in 'YYYY-MM-DD HH:MM' format.
            category: Task category ('general', 'work', 'personal'). Defaults to 'general'.

        Returns:
            int: ID of the newly inserted task.

        Raises:
            ValueError: If inputs are invalid.
            sqlite3.Error: If database operation fails.
        """
        try:
            datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            if not 1 <= priority <= 10:
                raise ValueError("Priority must be between 1 and 10")
            if not name.strip():
                raise ValueError("Task name cannot be empty")
            if category not in ("general", "work", "personal"):
                raise ValueError("Category must be 'general', 'work', or 'personal'")
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}") from e

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (name, priority, due_date, category) VALUES (?, ?, ?, ?)",
                (name, priority, due_date, category),
            )
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, status: Optional[str] = None) -> List[Tuple[int, str, int, str, str, str]]:
        """Retrieve tasks from the database.

        Args:
            status: Filter by status ('pending', 'completed', 'failed'). Defaults to None.

        Returns:
            List of tuples containing task details (id, name, priority, due_date, status, category).
        """
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT id, name, priority, due_date, status, category FROM tasks"
            params: List[str] = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += " ORDER BY priority ASC, due_date ASC"
            return conn.execute(query, params).fetchall()

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a task by its ID.

        Args:
            task_id: Task ID to retrieve.

        Returns:
            Dictionary of task details or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            return cursor.fetchone()

    def update_task_status(self, task_id: int, status: str) -> None:
        """Update the status of a task.

        Args:
            task_id: Task ID to update.
            status: New status ('pending', 'completed', 'failed').

        Raises:
            ValueError: If status is invalid.
        """
        if status not in ("pending", "completed", "failed"):
            raise ValueError("Status must be 'pending', 'completed', or 'failed'")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            conn.commit()

    def reschedule_task(self, task_id: int, new_due_date: str) -> None:
        """Reschedule a task to a new due date.

        Args:
            task_id: Task ID to reschedule.
            new_due_date: New due date in 'YYYY-MM-DD HH:MM' format.

        Raises:
            ValueError: If date format is invalid or task not found.
        """
        try:
            datetime.strptime(new_due_date, "%Y-%m-%d %H:%M")
        except ValueError as e:
            raise ValueError("Invalid due date format") from e

        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "UPDATE tasks SET due_date = ? WHERE id = ?", (new_due_date, task_id)
            )
            conn.commit()
            if result.rowcount == 0:
                raise ValueError(f"Task ID {task_id} not found")

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID.

        Args:
            task_id: Task ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0