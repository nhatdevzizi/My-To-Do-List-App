import unittest
import os
import tempfile
import json
from storages.json_storage import JsonStorage
from models.task import Task

class TestJsonStorage(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.storage = JsonStorage(self.temp_file.name)
        
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_save_and_load_empty_tasks(self):
        """Test saving and loading empty list of tasks."""
        tasks = []
        self.storage.save(tasks)
        
        loaded_tasks = self.storage.load()
        self.assertEqual(len(loaded_tasks), 0)
        
    def test_save_and_load_tasks(self):
        """Test saving and loading tasks with data."""
        # Create some test tasks
        task1 = Task(1, "Task 1", 60, "work", "Description 1", 2)
        task1.completed()
        
        task2 = Task(2, "Task 2", 30, "personal", "Description 2", 1)
        
        tasks = [task1, task2]
        self.storage.save(tasks)
        
        loaded_tasks = self.storage.load()
        self.assertEqual(len(loaded_tasks), 2)
        
        # Check that loaded tasks have correct data
        self.assertEqual(loaded_tasks[0].task_id, 1)
        self.assertEqual(loaded_tasks[0].title, "Task 1")
        self.assertEqual(loaded_tasks[0].duration, 60)
        self.assertEqual(loaded_tasks[0].category, "work")
        self.assertEqual(loaded_tasks[0].description, "Description 1")
        self.assertEqual(loaded_tasks[0].priority, 2)
        self.assertTrue(loaded_tasks[0].is_completed)
        
        self.assertEqual(loaded_tasks[1].task_id, 2)
        self.assertEqual(loaded_tasks[1].title, "Task 2")
        self.assertEqual(loaded_tasks[1].duration, 30)
        self.assertEqual(loaded_tasks[1].category, "personal")
        self.assertEqual(loaded_tasks[1].description, "Description 2")
        self.assertEqual(loaded_tasks[1].priority, 1)
        self.assertFalse(loaded_tasks[1].is_completed)
        

if __name__ == '__main__':
    unittest.main()