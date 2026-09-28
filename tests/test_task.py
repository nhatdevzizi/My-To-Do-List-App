import unittest
import os
import json
from models.task import Task

class TestTask(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.task = Task(
            task_id=1,
            title="Test Task",
            duration=60,
            category="work",
            description="This is a test task",
            priority=2
        )
        
    def test_task_creation(self):
        """Test that a task can be created with all required fields."""
        self.assertEqual(self.task.task_id, 1)
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.duration, 60)
        self.assertEqual(self.task.category, "work")
        self.assertEqual(self.task.description, "This is a test task")
        self.assertEqual(self.task.priority, 2)
        self.assertFalse(self.task.is_completed)
        
    def test_change_priority(self):
        """Test changing task priority."""
        self.task.change_priority(5)
        self.assertEqual(self.task.priority, 5)
        
    def test_change_duration(self):
        """Test changing task duration."""
        self.task.change_duration(90)
        self.assertEqual(self.task.duration, 90)
        
    def test_change_description(self):
        """Test changing task description."""
        self.task.change_description("Updated description")
        self.assertEqual(self.task.description, "Updated description")
        
    def test_complete_task(self):
        """Test completing a task."""
        self.task.completed()
        self.assertTrue(self.task.is_completed)
        
    def test_reopen_task(self):
        """Test reopening a completed task."""
        self.task.completed()
        self.assertTrue(self.task.is_completed)
        self.task.uncompleted()
        self.assertFalse(self.task.is_completed)
        
    def test_change_title(self):
        """Test changing task title."""
        self.task.change_title("Updated Task Title")
        self.assertEqual(self.task.title, "Updated Task Title")

if __name__ == '__main__':
    unittest.main()