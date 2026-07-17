"""
parser 单元测试 —— 重点覆盖边界场景：
- 空输入 / 纯空白
- 特殊字符（中文全角标点、emoji、替换字符等）
- 超长文本（性能与稳定性）
- 各类典型故障信号 + 无问题情况
"""

import json
import time
import unittest

from lib import parser


def titles(res):
    return {f.id for f in res.findings}


class TestBoundary(unittest.TestCase):
    def test_empty_input(self):
        res = parser.parse_diagnostic("")
        self.assertTrue(any(f.id == "no_issue" for f in res.findings))
        # 结果必须可 JSON 序列化（空输入也应稳定）
        json.dumps(res.to_dict())

    def test_whitespace_only(self):
        res = parser.parse_diagnostic("   \n\t  ")
        self.assertTrue(any(f.id == "no_issue" for f in res.findings))

    def test_special_chars_no_crash(self):
        text = (
            "诊断信息 ★🔧🚀 ＤＸＧＩ device lost in render loop．"
            "（全角标点）\ufffd 替换字符 <script>alert(1)</script>\n"
            "DXGI failed init: 8876017c at 0\n"
        )
        res = parser.parse_diagnostic(text)
        self.assertIn("dxgi_device_lost", titles(res))
        # 特殊字符不应破坏序列化
        blob = json.dumps(res.to_dict(), ensure_ascii=False)
        self.assertIn("dxgi_device_lost", blob)

    def test_very_long_text_performance(self):
        base = "2026-07-13T15:15:22Z  DXGI device lost in render loop.\n"
        text = base * 200_000  # 约 12MB 重复日志
        start = time.time()
        res = parser.parse_diagnostic(text)
        elapsed = time.time() - start
        self.assertIn("dxgi_device_lost", titles(res))
        # 解析应在合理时间内完成（预编译正则 + 线性扫描）
        self.assertLess(elapsed, 5.0, f"解析过慢：{elapsed:.2f}s")


class TestDetections(unittest.TestCase):
    def test_minimal_dxgi(self):
        res = parser.parse_diagnostic("DXGI device lost in render loop.\nDXGI failed init: 8876017c")
        self.assertIn("dxgi_device_lost", titles(res))
        f = next(f for f in res.findings if f.id == "dxgi_device_lost")
        self.assertEqual(f.severity, "critical")
        self.assertEqual(f.fix_actions, ["set_dgpu", "disable_hags", "reinstall_driver", "run_dism"])

    def test_deps_missing_x86(self):
        text = ("deps errors x86:\n"
                "  Error module: libcef.dll,  loaded: 0\n"
                "  Error module: assimp-vc140-mt32.dll,   loaded: 0\n")
        res = parser.parse_diagnostic(text)
        self.assertIn("deps_missing_x86", titles(res))
        f = next(f for f in res.findings if f.id == "deps_missing_x86")
        self.assertEqual(f.severity, "warning")
        self.assertIn("libcef.dll", f.evidence[0])

    def test_tray_error(self):
        res = parser.parse_diagnostic("icon create err: -2147467259.")
        self.assertIn("tray_icon_fail", titles(res))
        f = next(f for f in res.findings if f.id == "tray_icon_fail")
        self.assertIn("E_FAIL", f.detail)

    def test_web_script_error(self):
        res = parser.parse_diagnostic("Uncaught ReferenceError: scene is not defined (line 2)")
        self.assertIn("web_script_error", titles(res))

    def test_no_issue(self):
        res = parser.parse_diagnostic("Wallpaper Engine 运行正常，无任何错误日志。")
        self.assertTrue(any(f.id == "no_issue" for f in res.findings))
        self.assertEqual(res.summary, "未发现严重问题。")

    def test_meta_extraction(self):
        text = "Wallpaper Engine v2.8.42 on Windows 11 Build 26200 with NVIDIA GeForce RTX 5060"
        res = parser.parse_diagnostic(text)
        self.assertEqual(res.meta.get("we_version"), "2.8.42")
        self.assertIn("gpu_detected", res.meta)


if __name__ == "__main__":
    unittest.main(verbosity=2)
