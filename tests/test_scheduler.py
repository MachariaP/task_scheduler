"""Unit tests for the task scheduler."""

import os
import unittest
from datetime import datetime, timedelta

from task_scheduler.database import Database


class TestScheduler(unittest.TestCase):
    """Test cases for the scheduler."""

    def setUp(self):
        """Set up a test database."""
        self.db_path = "test_tasks.db"
        self.db = Database(self.db_path)
        self.db.add_task("Test Task", 1, (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"))

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_task(self):
        """Test adding a task."""
        task_id = self.db.add_task("New Task", 5, "2025-12-31 23:59")
        tasks = self.db.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[-1][0], task_id)

    def test_invalid_priority(self):
        """Test adding a task with invalid priority."""
        with self.assertRaises(ValueError):
            self.db.add_task("Invalid", 11, "2025-12-31 23:59")

    def test_reschedule(self):
        """Test rescheduling a task."""
        tasks = self.db.get_tasks()
        task_id = tasks[0][0]
        new_date = "2025-12-01 12:00"
        self.db.reschedule_task(task_id, new_date)
        updated_task = self.db.get_tasks()[0]
        self.assertEqual(updated_task[3], new_date)


if __name__ == "__main__":
    unittest.main()