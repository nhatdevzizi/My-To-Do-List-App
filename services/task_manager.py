"""Validated task operations with commit-after-save semantics."""

from models import Task


class TaskManager:
    def __init__(self, repository):
        self.repository = repository
        self.tasks = repository.load()
        self.next_id = repository.next_id

    def get_next_id(self):
        return self.next_id

    def _commit(self, tasks, next_id=None):
        if next_id is None:
            next_id = self.next_id
        self.repository.save(tasks, next_id)
        self.tasks = tasks
        self.next_id = next_id

    def _find_index(self, task_id):
        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
            raise ValueError("Task ID must be a positive integer")
        for index, task in enumerate(self.tasks):
            if task.task_id == task_id:
                return index
        return None

    def add_task(self, title, description="", duration=0, category="general", priority=0):
        task = Task(self.next_id, title, duration, category, description, priority)
        self._commit([*self.tasks, task], self.next_id + 1)
        return task.copy()

    def get_task(self, task_id):
        index = self._find_index(task_id)
        return self.tasks[index].copy() if index is not None else None

    def update_task(self, task_id, title=None, description=None, duration=None,
                    category=None, priority=None):
        index = self._find_index(task_id)
        if index is None:
            return False
        changes = {}
        if title is not None:
            changes["title"] = title
        if description is not None:
            changes["description"] = description
        if duration is not None:
            changes["duration"] = duration
        if category is not None:
            changes["category"] = category
        if priority is not None:
            changes["priority"] = priority
        if not changes:
            return True
        updated = self.tasks[index].copy(**changes)  # Validates the whole update first.
        candidates = self.tasks.copy()
        candidates[index] = updated
        self._commit(candidates)
        return True

    def remove_task(self, task_id):
        index = self._find_index(task_id)
        if index is None:
            return False
        self._commit(self.tasks[:index] + self.tasks[index + 1:])
        return True

    def _set_completion(self, task_id, completed):
        index = self._find_index(task_id)
        if index is None:
            return False
        if self.tasks[index].is_completed == completed:
            return True
        candidates = self.tasks.copy()
        candidates[index] = self.tasks[index].copy(is_completed=completed)
        self._commit(candidates)
        return True

    def complete_task(self, task_id):
        return self._set_completion(task_id, True)

    def reopen_task(self, task_id):
        return self._set_completion(task_id, False)

    def list_all_tasks(self):
        return [task.copy() for task in self.tasks]

    def list_completed_tasks(self):
        return self.filter_tasks(completed=True)

    def list_incomplete_tasks(self):
        return self.filter_tasks(completed=False)

    def filter_tasks(self, category=None, completed=None, priority=None):
        if category is not None:
            category = Task.validate_category(category)
        if completed is not None and not isinstance(completed, bool):
            raise ValueError("Completion filter must be true or false")
        if priority is not None:
            priority = Task.validate_priority(priority)
        return [
            task.copy() for task in self.tasks
            if (category is None or task.category == category)
            and (completed is None or task.is_completed == completed)
            and (priority is None or task.priority == priority)
        ]

    def sort_tasks(self, by="id", reverse=False):
        keys = {
            "id": lambda task: task.task_id,
            "creation": lambda task: task.task_id,
            "title": lambda task: task.title.casefold(),
            "duration": lambda task: task.duration,
            "priority": lambda task: task.priority,
            "category": lambda task: task.category.casefold(),
            "is_completed": lambda task: task.is_completed,
        }
        if by not in keys:
            raise ValueError(f"Invalid sort criterion: {by}")
        if not isinstance(reverse, bool):
            raise ValueError("Reverse flag must be true or false")
        # Stable sorting retains creation order for equal keys.
        return [task.copy() for task in sorted(self.tasks, key=keys[by], reverse=reverse)]
