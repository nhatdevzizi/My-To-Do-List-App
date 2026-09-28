"""Interactive command-line interface for task management."""

from pathlib import Path

from repositories.task_repository import TaskRepository
from services.task_manager import TaskManager
from storages.json_storage import JsonStorage


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tasks.json"


def _integer(raw, label, default=None):
    if not raw.strip() and default is not None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{label} phải là số nguyên") from exc


def _show_task(task, output_fn):
    status = "Hoàn thành" if task.is_completed else "Đang làm"
    output_fn(
        f"#{task.task_id} | {task.title} | {status} | "
        f"{task.duration} phút | {task.category} | ưu tiên {task.priority}"
    )
    if task.description:
        output_fn(f"  {task.description}")


def _show_tasks(tasks, output_fn):
    if not tasks:
        output_fn("Không có công việc nào.")
    for task in tasks:
        _show_task(task, output_fn)


def _task_id(input_fn):
    return _integer(input_fn("ID công việc: "), "ID")


def run_cli(manager, input_fn=input, output_fn=print):
    menu = (
        "\n1. Thêm  2. Xem  3. Liệt kê  4. Sửa  5. Xóa\n"
        "6. Hoàn thành  7. Mở lại  8. Lọc  9. Sắp xếp  0. Thoát"
    )
    while True:
        output_fn(menu)
        try:
            choice = input_fn("Chọn: ").strip()
            if choice == "0":
                return 0
            if choice == "1":
                title = input_fn("Tiêu đề: ")
                description = input_fn("Mô tả (tùy chọn): ")
                duration = _integer(input_fn("Thời lượng phút (mặc định 0): "), "Thời lượng", 0)
                category = input_fn("Danh mục (mặc định general): ").strip() or "general"
                priority = _integer(input_fn("Ưu tiên 0-5 (mặc định 0): "), "Ưu tiên", 0)
                task = manager.add_task(title, description, duration, category, priority)
                output_fn(f"Đã thêm công việc #{task.task_id}.")
            elif choice == "2":
                task = manager.get_task(_task_id(input_fn))
                if task is None:
                    output_fn("Không tìm thấy công việc.")
                else:
                    _show_task(task, output_fn)
            elif choice == "3":
                _show_tasks(manager.list_all_tasks(), output_fn)
            elif choice == "4":
                task_id = _task_id(input_fn)
                if manager.get_task(task_id) is None:
                    output_fn("Không tìm thấy công việc.")
                    continue
                output_fn("Để trống để giữ nguyên; nhập - ở mô tả để xóa mô tả.")
                title = input_fn("Tiêu đề mới: ")
                description = input_fn("Mô tả mới: ")
                duration = input_fn("Thời lượng mới: ")
                category = input_fn("Danh mục mới: ")
                priority = input_fn("Ưu tiên mới: ")
                changes = {}
                if title:
                    changes["title"] = title
                if description:
                    changes["description"] = "" if description == "-" else description
                if duration:
                    changes["duration"] = _integer(duration, "Thời lượng")
                if category:
                    changes["category"] = category
                if priority:
                    changes["priority"] = _integer(priority, "Ưu tiên")
                manager.update_task(task_id, **changes)
                output_fn("Đã cập nhật công việc.")
            elif choice == "5":
                output_fn("Đã xóa công việc." if manager.remove_task(_task_id(input_fn))
                          else "Không tìm thấy công việc.")
            elif choice == "6":
                output_fn("Đã hoàn thành công việc." if manager.complete_task(_task_id(input_fn))
                          else "Không tìm thấy công việc.")
            elif choice == "7":
                output_fn("Đã mở lại công việc." if manager.reopen_task(_task_id(input_fn))
                          else "Không tìm thấy công việc.")
            elif choice == "8":
                status = input_fn("Trạng thái (tất cả/chưa xong/đã xong): ").strip().lower()
                if status not in ("", "tất cả", "chưa xong", "đã xong"):
                    raise ValueError("Trạng thái lọc không hợp lệ")
                completed = None if status in ("", "tất cả") else status == "đã xong"
                category = input_fn("Danh mục (trống = tất cả): ").strip() or None
                priority = input_fn("Ưu tiên (trống = tất cả): ").strip()
                _show_tasks(manager.filter_tasks(
                    category=category, completed=completed,
                    priority=_integer(priority, "Ưu tiên") if priority else None,
                ), output_fn)
            elif choice == "9":
                criterion = input_fn("Sắp xếp theo (creation/priority/duration/title): ").strip() or "creation"
                descending = input_fn("Giảm dần? (y/N): ").strip().lower() == "y"
                _show_tasks(manager.sort_tasks(criterion, descending), output_fn)
            else:
                output_fn("Lựa chọn không hợp lệ.")
        except (EOFError, KeyboardInterrupt, StopIteration):
            output_fn("\nTạm biệt.")
            return 0
        except (ValueError, OSError) as exc:
            output_fn(f"Lỗi: {exc}")


def main():
    try:
        manager = TaskManager(TaskRepository(JsonStorage(DATA_FILE)))
    except (ValueError, OSError) as exc:
        print(f"Lỗi khi nạp dữ liệu: {exc}")
        return 1
    return run_cli(manager)
