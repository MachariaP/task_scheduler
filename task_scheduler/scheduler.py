"""Task scheduling logic with priority queue and concurrency."""

import heapq
import logging
import random
import time
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Tuple

from task_scheduler.database import Database

# Configure logging
logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Scheduler:
    """Task scheduler using a priority queue and threading."""

    def __init__(self, db_path: str = "tasks.db", max_workers: int = 3) -> None:
        """Initialize scheduler with database and worker limit."""
        self.db = Database(db_path)
        self.max_workers = max_workers


    def _execute_task(self, task_id: int, name: str) -> None:
        logging.info(f"Starting task {task_id}: {name}")
        try:
            time.sleep(random.uniform(1, 5))
            self.db.update_task_status(task_id, "completed")
            logging.info(f"Completed task {task_id}: {name}")
            self.send_email(f"Task {name} completed", "Success!")
        except Exception as e:
            self.db.update_task_status(task_id, "failed")
            logging.error(f"Failed task {task_id}: {name} - {e}")
            self.send_email(f"Task {name} failed", f"Error: {e}")

    def send_email(subject: str, body: str) -> None:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "your_email@example.com"
        msg["To"] = "your_email@example.com"
        with smtplib.SMTP("smtp.example.com") as server:
            server.login("username", "password")
            server.send_message(msg)

    def build_queue(self) -> List[Tuple[int, float, int]]:
        """Build priority queue from pending tasks."""
        tasks = self.db.get_tasks(status="pending")
        queue = []
        for task in tasks:
            task_id, name, priority, due_date, _ = task
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
                name = self.db.get_tasks()[0][1]  # Fetch name (inefficient, optimize later)
                executor.submit(self._execute_task, task_id, name)