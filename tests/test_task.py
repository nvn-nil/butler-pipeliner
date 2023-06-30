import unittest
import os

from unittest.mock import patch

from core.models.task import Task
from tests._base import BaseTestCase

class TestTask(BaseTestCase):
    def test_parse_task_file(self):
        task = Task(os.path.join(self.path, "task_files", "line_thinner.yml"))

        kwargs = {
            "param_values": {
                "input": "D:\personal\pipeliner\dist\sample\TouristAreas.txt"
            }
        }
        task.run(**kwargs)
        # with patch("core.models.task.os.system") as mocked_system:
        #     mocked_system.call_count = 1
        #     mocked_system.assert_called_once_with("shell command")

    def test_multi_step_task(self):
        task = Task(os.path.join(self.path, "task_files", "thin_line_and_reduce_points.yml"))

        kwargs = {
            "param_values": {
                "input": "D:\personal\pipeliner\dist\sample\TouristAreas.txt",
                "suffix": "_output"
            }
        }
        task.run(**kwargs)


if __name__ == '__main__':
    unittest.main()