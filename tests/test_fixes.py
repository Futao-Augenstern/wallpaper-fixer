"""修复动作执行逻辑的单元测试（guided 分支用 mock 替代真实 PowerShell）。"""
import unittest
from unittest import mock

from lib import fixes


class TestGuided(unittest.TestCase):
    def test_guided_returns_message_not_fake_completion(self):
        with mock.patch.object(
            fixes, "_run_direct",
            return_value={"ok": True, "rc": 0, "stdout": "已尝试打开 Steam", "stderr": ""},
        ):
            r = fixes.run_fix("verify_steam_files", confirm=True)
        self.assertTrue(r["ok"])
        self.assertTrue(r["guided"], "引导类动作应标记 guided，而非伪装成执行完成")
        self.assertIn("已尝试打开 Steam", r["message"])

    def test_guided_failure_surfaces_error(self):
        with mock.patch.object(
            fixes, "_run_direct",
            return_value={"ok": False, "rc": 1, "stdout": "", "stderr": "boom"},
        ):
            r = fixes.run_fix("open_graphics_settings", confirm=True)
        self.assertFalse(r["ok"])
        self.assertIn("boom", r["error"])

    def test_mutate_still_direct(self):
        with mock.patch.object(
            fixes, "_run_direct",
            return_value={"ok": True, "rc": 0, "stdout": "set .. -> high performance", "stderr": ""},
        ), mock.patch.object(fixes, "_resolve_we_exe", return_value=r"C:\x\wallpaper64.exe"):
            r = fixes.run_fix("set_dgpu", confirm=True)
        self.assertTrue(r["ok"])
        self.assertNotIn("guided", r)


class TestListActions(unittest.TestCase):
    def test_list_excludes_callables_and_has_kinds(self):
        acts = fixes.list_actions()
        self.assertTrue(any(a["id"] == "verify_steam_files" for a in acts))
        for a in acts:
            self.assertNotIn("build", a)
            self.assertNotIn("params", a)
            self.assertIn("kind", a)
            self.assertIn("needs_admin", a)


if __name__ == "__main__":
    unittest.main()
