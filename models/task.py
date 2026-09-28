"""The task entity and its input rules."""

from dataclasses import dataclass, replace


@dataclass
class Task:
    task_id: int
    title: str
    duration: int = 0
    category: str = "general"
    description: str = ""
    priority: int = 0
    is_completed: bool = False

    def __post_init__(self):
        if isinstance(self.task_id, bool) or not isinstance(self.task_id, int) or self.task_id < 1:
            raise ValueError("Task ID must be a positive integer")
        self.title = self.validate_title(self.title)
        self.duration = self.validate_duration(self.duration)
        self.category = self.validate_category(self.category)
        self.description = self.validate_description(self.description)
        self.priority = self.validate_priority(self.priority)
        if not isinstance(self.is_completed, bool):
            raise ValueError("Completion status must be true or false")

    @staticmethod
    def validate_title(value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task title cannot be empty")
        return value.strip()

    @staticmethod
    def validate_duration(value):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("Task duration must be a non-negative integer")
        return value

    @staticmethod
    def validate_category(value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task category cannot be empty")
        return value.strip()

    @staticmethod
    def validate_description(value):
        if not isinstance(value, str):
            raise ValueError("Task description must be text")
        return value

    @staticmethod
    def validate_priority(value):
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 5:
            raise ValueError("Task priority must be an integer from 0 to 5")
        return value

    def copy(self, **changes):
        return replace(self, **changes)

    def change_title(self, value):
        self.title = self.validate_title(value)

    def change_duration(self, value):
        self.duration = self.validate_duration(value)

    def change_description(self, value):
        self.description = self.validate_description(value)

    def change_priority(self, value):
        self.priority = self.validate_priority(value)

    def completed(self):
        self.is_completed = True

    def uncompleted(self):
        self.is_completed = False
