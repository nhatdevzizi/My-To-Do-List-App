class Task:
    def __init__(self,task_id: int, tittle: str, duration: int, category: str, description: str = "", priority: int = 0):
        self.task_id = task_id
        self.title = tittle
        self.duration = duration #minutes
        self.category = category
        self.description = description
        self.is_completed = False

    #Task behaviors
    def change_priority(self, new_priority: int):
        self.priority = new_priority

    def change_duration(self,new_duration: int):
        try:
            self.duration = new_duration
        except new_duration < 0:
            self.duration = 0

    def change_description(self, new_description: str):
        self.description = new_description

    def completed(self):
        self.is_completed = True

    def uncompleted(self):
        self.is_completed = False

    def change_tittle(self):
        default_tittle = "f'Task {self.task_id}'"
        try:
            username_tittle = input("Tittle: ")
        except NameError:
            username_tittle = default_tittle

