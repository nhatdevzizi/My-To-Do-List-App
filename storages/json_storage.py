"""Atomic JSON storage for the complete task collection."""

import json
import os
import tempfile
from pathlib import Path

from models import Task


class JsonStorage:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.next_id = 1

    def load(self):
        if not self.file_path.exists():
            self.next_id = 1
            return []
        try:
            content = self.file_path.read_text(encoding="utf-8")
            if not content.strip():
                self.next_id = 1
                return []
            document = json.loads(content)
            if isinstance(document, list):  # Earlier versions stored a bare list.
                records = document
                next_id = None
            elif isinstance(document, dict):
                records = document["tasks"]
                next_id = document.get("next_id")
            else:
                raise ValueError("Task file must contain a task list")
            if not isinstance(records, list):
                raise ValueError("Task file must contain a task list")
            tasks = [Task(**record) for record in records]
            ids = [task.task_id for task in tasks]
            if len(ids) != len(set(ids)):
                raise ValueError("Task file contains duplicate IDs")
            minimum_next_id = max(ids, default=0) + 1
            if next_id is None:
                next_id = minimum_next_id
            if isinstance(next_id, bool) or not isinstance(next_id, int) or next_id < minimum_next_id:
                raise ValueError("Task file contains an invalid next ID")
            self.next_id = next_id
            return tasks
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError(f"Cannot load tasks from {self.file_path}: {exc}") from exc

    def save(self, tasks, next_id=None):
        if next_id is None:
            next_id = max((task.task_id for task in tasks), default=0) + 1
        payload = {
            "next_id": next_id,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "duration": task.duration,
                    "category": task.category,
                    "description": task.description,
                    "priority": task.priority,
                    "is_completed": task.is_completed,
                }
                for task in tasks
            ],
        }
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.", suffix=".tmp", delete=False,
            ) as stream:
                temp_path = Path(stream.name)
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, self.file_path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
        self.next_id = next_id
