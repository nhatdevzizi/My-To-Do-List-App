"""State and CLI tests spanning several operations."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repositories.task_repository import TaskRepository
from services.task_manager import TaskManager
from storages.json_storage import JsonStorage
from ui.cli import run_cli


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "tasks.json"
        self.manager = self.reload()

    def reload(self):
        return TaskManager(TaskRepository(JsonStorage(self.path)))

    def test_invalid_update_changes_neither_memory_nor_disk(self):
        task = self.manager.add_task("Original", duration=10, priority=2)
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.manager.update_task(task.task_id, title="Changed", duration=-1)
        self.assertEqual(self.manager.get_task(task.task_id).title, "Original")
        self.assertEqual(self.manager.get_task(task.task_id).duration, 10)
        self.assertEqual(self.path.read_bytes(), before)
        for invalid in ("", "  ", None):
            with self.assertRaises(ValueError):
                self.manager.add_task(invalid)
        with self.assertRaises(ValueError):
            self.manager.update_task(task.task_id, priority=6)
        self.assertEqual(self.path.read_bytes(), before)

    def test_failed_save_keeps_memory_file_and_next_id(self):
        first = self.manager.add_task("First")
        before = self.path.read_bytes()
        with patch("storages.json_storage.os.replace", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                self.manager.update_task(first.task_id, title="Changed")
            with self.assertRaisesRegex(OSError, "disk full"):
                self.manager.add_task("Second")
            with self.assertRaisesRegex(OSError, "disk full"):
                self.manager.remove_task(first.task_id)
            with self.assertRaisesRegex(OSError, "disk full"):
                self.manager.complete_task(first.task_id)
        self.assertEqual(self.manager.get_task(first.task_id).title, "First")
        self.assertFalse(self.manager.get_task(first.task_id).is_completed)
        self.assertEqual(self.manager.get_next_id(), 2)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])
        self.assertEqual(self.manager.add_task("Second").task_id, 2)

    def test_ids_and_completion_survive_delete_and_reload(self):
        first = self.manager.add_task("First", category="work", priority=3)
        second = self.manager.add_task("Second", category="home", priority=1)
        self.assertTrue(self.manager.complete_task(first.task_id))
        self.assertTrue(self.manager.complete_task(first.task_id))
        self.assertEqual([t.task_id for t in self.manager.filter_tasks(completed=True)], [1])
        self.assertEqual([t.task_id for t in self.manager.filter_tasks(completed=False)], [2])
        self.assertTrue(self.manager.remove_task(second.task_id))
        self.assertFalse(self.manager.remove_task(999))
        self.manager = self.reload()
        self.assertTrue(self.manager.get_task(first.task_id).is_completed)
        self.assertEqual(self.manager.add_task("Third").task_id, 3)
        self.assertTrue(self.manager.reopen_task(first.task_id))
        self.assertFalse(self.reload().get_task(first.task_id).is_completed)

    def test_legacy_and_corrupt_files(self):
        self.path.write_text("", encoding="utf-8")
        self.assertEqual(self.reload().list_all_tasks(), [])
        self.path.write_text("[]", encoding="utf-8")
        self.assertEqual(self.reload().get_next_id(), 1)
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Cannot load tasks"):
            self.reload()

    def test_full_cli_workflow(self):
        answers = iter([
            "1", "Alpha", "details", "30", "work", "2",
            "1", "Beta", "", "10", "home", "5",
            "4", "1", "", "-", "45", "", "",
            "6", "1", "8", "đã xong", "", "",
            "9", "priority", "y", "7", "1", "5", "2",
            "3", "0",
        ])
        output = []
        result = run_cli(self.manager, input_fn=lambda _: next(answers), output_fn=output.append)
        self.assertEqual(result, 0)
        self.assertTrue(any("Đã thêm công việc #1" in line for line in output))
        self.assertTrue(any("Đã cập nhật" in line for line in output))
        self.assertTrue(any("Đã xóa" in line for line in output))
        self.assertEqual(len(self.reload().list_all_tasks()), 1)
        task = self.reload().get_task(1)
        self.assertEqual((task.title, task.description, task.duration, task.is_completed),
                         ("Alpha", "", 45, False))
        self.assertEqual(self.reload().get_next_id(), 3)

    def test_cli_reports_errors_and_continues(self):
        answers = iter(["1", "", "", "0", "", "0", "1", "Valid", "", "0", "", "0", "0"])
        output = []
        run_cli(self.manager, input_fn=lambda _: next(answers), output_fn=output.append)
        self.assertTrue(any("Lỗi:" in line for line in output))
        self.assertEqual([task.title for task in self.reload().list_all_tasks()], ["Valid"])

    def test_main_starts_with_legacy_windows_output_encoding(self):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        project_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(project_root / "main.py")],
            input=b"0\n", capture_output=True, cwd=project_root, env=env, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertIn("Thêm".encode("utf-8"), result.stdout)


if __name__ == "__main__":
    unittest.main()
