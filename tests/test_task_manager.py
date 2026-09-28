import unittest
import os
import tempfile
import json
from services.task_manager import TaskManager
from repositories.task_repository import TaskRepository
from storages.json_storage import JsonStorage
from models.task import Task

class TestTaskManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # Initialize storage, repository and task manager
        self.storage = JsonStorage(self.temp_file.name)
        self.repository = TaskRepository(self.storage)
        self.task_manager = TaskManager(self.repository)
        
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_task(self):
        """Test adding a new task."""
        task = self.task_manager.add_task(
            title="Test Task",
            description="This is a test task",
            duration=60,
            category="work",
            priority=2
        )
        
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.duration, 60)
        self.assertEqual(task.category, "work")
        self.assertEqual(task.priority, 2)
        self.assertFalse(task.is_completed)
        
        # Check that task is persisted
        loaded_tasks = self.task_manager.list_all_tasks()
        self.assertEqual(len(loaded_tasks), 1)
        self.assertEqual(loaded_tasks[0].title, "Test Task")
    
    def test_get_task(self):
        """Test getting a specific task."""
        # Add a task first
        task1 = self.task_manager.add_task(title="Task 1")
        task2 = self.task_manager.add_task(title="Task 2")
        
        # Retrieve task by ID
        retrieved_task = self.task_manager.get_task(task1.task_id)
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.title, "Task 1")
        
        # Try to get non-existent task
        retrieved_task = self.task_manager.get_task(999)
        self.assertIsNone(retrieved_task)
    
    def test_update_task(self):
        """Test updating a task."""
        # Add a task first
        task = self.task_manager.add_task(title="Original Task")
        
        # Update the task
        success = self.task_manager.update_task(
            task_id=task.task_id,
            title="Updated Task",
            description="Updated description",
            duration=120,
            category="personal",
            priority=3
        )
        
        self.assertTrue(success)
        
        # Verify update
        updated_task = self.task_manager.get_task(task.task_id)
        self.assertEqual(updated_task.title, "Updated Task")
        self.assertEqual(updated_task.description, "Updated description")
        self.assertEqual(updated_task.duration, 120)
        self.assertEqual(updated_task.category, "personal")
        self.assertEqual(updated_task.priority, 3)
        
    def test_remove_task(self):
        """Test removing a task."""
        # Add two tasks first
        task1 = self.task_manager.add_task(title="Task 1")
        task2 = self.task_manager.add_task(title="Task 2")
        
        # Remove one task
        success = self.task_manager.remove_task(task1.task_id)
        self.assertTrue(success)
        
        # Check that only one task remains
        all_tasks = self.task_manager.list_all_tasks()
        self.assertEqual(len(all_tasks), 1)
        self.assertEqual(all_tasks[0].title, "Task 2")
        
    def test_complete_task(self):
        """Test completing a task."""
        # Add a task first
        task = self.task_manager.add_task(title="Task to Complete")
        
        # Complete the task
        success = self.task_manager.complete_task(task.task_id)
        self.assertTrue(success)
        
        # Check that task is completed
        completed_task = self.task_manager.get_task(task.task_id)
        self.assertTrue(completed_task.is_completed)
        
    def test_reopen_task(self):
        """Test reopening a completed task."""
        # Add and complete a task first
        task = self.task_manager.add_task(title="Task to Reopen")
        self.task_manager.complete_task(task.task_id)
        
        # Reopen the task
        success = self.task_manager.reopen_task(task.task_id)
        self.assertTrue(success)
        
        # Check that task is not completed anymore
        reopened_task = self.task_manager.get_task(task.task_id)
        self.assertFalse(reopened_task.is_completed)
    
    def test_filter_tasks(self):
        """Test filtering tasks."""
        # Add some tasks with different categories
        task1 = self.task_manager.add_task(title="Work Task", category="work")
        task2 = self.task_manager.add_task(title="Personal Task", category="personal")
        task3 = self.task_manager.add_task(title="Work Task 2", category="work")
        
        # Filter by category
        work_tasks = self.task_manager.filter_tasks(category="work")
        self.assertEqual(len(work_tasks), 2)
        
        # Filter by completion status (all are pending initially)
        pending_tasks = self.task_manager.filter_tasks(completed=False)
        self.assertEqual(len(pending_tasks), 3)
        
    def test_sort_tasks(self):
        """Test sorting tasks."""
        # Add some tasks with different priorities
        task1 = self.task_manager.add_task(title="Low Priority Task", priority=1)
        task2 = self.task_manager.add_task(title="High Priority Task", priority=5)
        task3 = self.task_manager.add_task(title="Medium Priority Task", priority=3)
        
        # Sort by priority ascending
        sorted_tasks_asc = self.task_manager.sort_tasks(by="priority", reverse=False)
        self.assertEqual(sorted_tasks_asc[0].priority, 1)
        self.assertEqual(sorted_tasks_asc[1].priority, 3)
        self.assertEqual(sorted_tasks_asc[2].priority, 5)
        
        # Sort by priority descending
        sorted_tasks_desc = self.task_manager.sort_tasks(by="priority", reverse=True)
        self.assertEqual(sorted_tasks_desc[0].priority, 5)
        self.assertEqual(sorted_tasks_desc[1].priority, 3)
        self.assertEqual(sorted_tasks_desc[2].priority, 1)

if __name__ == '__main__':
    unittest.main()