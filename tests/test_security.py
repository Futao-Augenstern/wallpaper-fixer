"""安全相关测试：路径穿越、动作白名单、PowerShell 单引号转义。"""
import unittest

from lib import fixes


class TestActionValidation(unittest.TestCase):
    def test_known_action_ok(self):
        self.assertTrue(fixes.is_known_action("set_dgpu"))
        self.assertTrue(fixes.is_known_action("run_sfc"))

    def test_rejects_path_traversal(self):
        # 关键：/api/fix/log 的 action 不能用来读任意文件
        self.assertFalse(fixes.is_known_action("../secret"))
        self.assertFalse(fixes.is_known_action("../../etc/passwd"))
        self.assertFalse(fixes.is_known_action("..\\..\\windows\\system32\\x"))

    def test_rejects_bad_chars(self):
        self.assertFalse(fixes.is_known_action("set-dgpu"))   # 连字符
        self.assertFalse(fixes.is_known_action("SET_DGPU"))   # 大写
        self.assertFalse(fixes.is_known_action("foo bar"))
        self.assertFalse(fixes.is_known_action(""))

    def test_get_fix_log_rejects_bad_id(self):
        # 不应抛异常，也不应去读越权路径
        res = fixes.get_fix_log("../../etc/passwd")
        self.assertEqual(res.get("error"), "invalid action")
        self.assertFalse(res.get("exists"))

    def test_run_fix_unknown_id(self):
        res = fixes.run_fix("../../../etc/passwd", confirm=True)
        self.assertFalse(res.get("ok"))
        self.assertIn("未知", res.get("error", ""))


class TestPsInjectionEscape(unittest.TestCase):
    def test_single_quote_is_escaped(self):
        # set_dgpu 把 exe 路径拼进 PowerShell 单引号字符串，必须转义 ' 防注入
        script = fixes.FIX_ACTIONS["set_dgpu"]["build"](
            {"exe": "C:\\weird'path\\wallpaper64.exe"})
        self.assertIn("weird''path", script)        # 转义后成对出现
        self.assertNotIn("weird'path'", script)     # 原始未转义片段不应存在


if __name__ == "__main__":
    unittest.main()
