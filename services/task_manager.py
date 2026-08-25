from asyncio import tasks
from models import Task

class TaskManager:
    def __init__(self,repository):
        self.repository = repository
        self.tasks = repository.load()

    #Get IDs increase automatically
    def get_next_id(self):
        if not self.tasks:
            return 1
        return max(task.task_id for task in self.tasks) + 1

    def add_task(self, title, description = "", duration = 0):
        new_task_id = self.get_next_id()
        new_task = Task(task_id = new_task_id, title= title, description = description, duration = duration)

        self.tasks.append(new_task)
        self.repository.save(new_task)
        return new_task


    def get_task(self,task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(self,task_id, tittle,description,duration):
        task = self.get_task(task_id)
        if task is None:
            return False
        task.title = tittle
        task.description = description
        task.duration = duration
        self.repository.save(self.task)
        return task

    def remove_task(self,task_id):
        task = self.get_task(task_id)
        self.tasks.remove(task)

    def complete_task(self,task_id):
        task = self.get_task(task_id)
        if task is None:
            return False
        task.completed()
        self.repository.save(self.task)
        return True

    def listing_all_tasks(self):
        return self.tasks.copy()

    def listing_completed_tasks(self):
        return [tasks for task in self.tasks if task.completed == True]

    def listing_failed_tasks(self):
        return [tasks for task in self.tasks if task.completed == False]




