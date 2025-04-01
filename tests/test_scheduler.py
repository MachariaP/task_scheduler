"""Unit tests for the task scheduler."""

import os
import unittest
from datetime import datetime, timedelta
from task_scheduler.database import Database


class TestScheduler(unittest.TestCase):
    """Test cases for the scheduler and database."""

    def setUp(self) -> None:
        """Set up a test database before each test."""
        self.db_path = "test_tasks.db"
        self.db = Database(self.db_path)
        self.db.add_task(
            "Test Task",
            1,
            (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"),
            "general",
        )

    def tearDown(self) -> None:
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_task(self) -> None:
        """Test adding a valid task."""
        task_id = self.db.add_task("New Task", 5, "2025-12-31 23:59", "work")
        tasks = self.db.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[-1][0], task_id)
        self.assertEqual(tasks[-1][5], "work")

    def test_invalid_priority(self) -> None:
        """Test adding a task with invalid priority."""
        with self.assertRaises(ValueError):
            self.db.add_task("Invalid", 11, "2025-12-31 23:59", "general")

    def test_reschedule(self) -> None:
        """Test rescheduling a task."""
        tasks = self.db.get_tasks()
        task_id = tasks[0][0]
        new_date = "2025-12-01 12:00"
        self.db.reschedule_task(task_id, new_date)
        updated_task = self.db.get_task_by_id(task_id)
        self.assertEqual(updated_task["due_date"], new_date)

    def test_delete_task(self) -> None:
        """Test deleting a task."""
        tasks = self.db.get_tasks()
        task_id = tasks[0][0]
        self.assertTrue(self.db.delete_task(task_id))
        self.assertIsNone(self.db.get_task_by_id(task_id))


if __name__ == "__main__":
    unittest.main()