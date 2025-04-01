"""Task scheduling logic with priority queue and concurrency."""

import sqlite3
import heapq
import logging
import random
import time
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv
import os
from task_scheduler.database import Database

# Load environment variables
load_dotenv()

# Configuration from environment variables
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 3))
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Scheduler:
    """Task scheduler using a priority queue and threading."""

    def __init__(self, db_path: str = "tasks.db", max_workers: int = MAX_WORKERS) -> None:
        """Initialize scheduler with database and worker limit.

        Args:
            db_path: Path to SQLite database file. Defaults to 'tasks.db'.
            max_workers: Maximum concurrent workers. Defaults to MAX_WORKERS from env.
        """
        self.db = Database(db_path)
        self.max_workers = max_workers

    def _execute_task(self, task_id: int, name: str) -> None:
        """Execute a single task and send email notification.

        Args:
            task_id: Task ID to execute.
            name: Task name for logging and notification.
        """
        logging.info(f"Starting task {task_id}: {name}")
        try:
            time.sleep(random.uniform(1, 5))  # Simulate work
            self.db.update_task_status(task_id, "completed")
            logging.info(f"Completed task {task_id}: {name}")
            self._send_email(f"Task {name} Completed", "Success!")
        except Exception as e:
            self.db.update_task_status(task_id, "failed")
            logging.error(f"Failed task {task_id}: {name} - {e}")
            self._send_email(f"Task {name} Failed", f"Error: {e}")

    def _send_email(self, subject: str, body: str) -> None:
        """Send an email notification using SMTP settings from environment variables.

        Args:
            subject: Email subject.
            body: Email body.

        Raises:
            Exception: If email sending fails.
        """
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER  # Self-email
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            logging.info(f"Email sent: {subject}")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")

    def build_queue(self) -> List[Tuple[int, float, int]]:
        """Build a priority queue from pending tasks.

        Returns:
            List of tuples (priority, due_ts, task_id) sorted by priority and due date.
        """
        tasks = self.db.get_tasks(status="pending")
        queue = []
        for task in tasks:
            task_id, _, priority, due_date, _, _ = task
            due_ts = datetime.strptime(due_date, "%Y-%m-%d %H:%M").timestamp()
            heapq.heappush(queue, (priority, due_ts, task_id))
        return queue

    def run(self) -> None:
        """Execute tasks from the queue with concurrency."""
        queue = self.build_queue()
        if not queue:
            logging.info("No pending tasks to execute")
            print("No tasks to run.")
            return

        logging.info(f"Starting scheduler with {len(queue)} tasks")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while queue:
                priority, due_ts, task_id = heapq.heappop(queue)
                task = self.db.get_task_by_id(task_id)
                if task:
                    executor.submit(self._execute_task, task_id, task["name"])