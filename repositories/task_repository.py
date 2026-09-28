"""Repository boundary for task persistence."""


class TaskRepository:
    def __init__(self, storage):
        self.storage = storage

    @property
    def next_id(self):
        return self.storage.next_id

    def load(self):
        return self.storage.load()

    def save(self, tasks, next_id):
        self.storage.save(tasks, next_id)
