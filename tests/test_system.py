"""系统体检解析测试：直接喂样例 JSON 给 _parse_scan（纯函数，不触发 PowerShell）。"""
import json
import unittest

from lib import system_info


SAMPLE = json.dumps({
    "os": {"Caption": "Windows 11 Pro", "Version": "10.0.26200",
           "BuildNumber": "26200", "OSArchitecture": "64-bit"},
    "gpus": [
        {"Name": "Intel(R) Arc Graphics", "DriverVersion": "32.0.101.5768",
         "Status": "OK", "VideoProcessor": "", "AdapterRAM": 0},
        {"Name": "NVIDIA GeForce RTX 5060 Laptop GPU", "DriverVersion": "32.0.15.6109",
         "Status": "OK", "VideoProcessor": "", "AdapterRAM": 0},
    ],
    "hags": 2,                       # 关闭
    "procs": [
        {"Name": "wallpaper64", "Id": 1234},
        {"Name": "Windhawk", "Id": 5678},
        {"Name": "explorer", "Id": 999},
    ],
    "we_path": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Wallpaper Engine",
    "missing_dlls": ["libcef.dll", "assimp-vc140-mt32.dll"],
    "wallpaper32_present": True,
    "dxgi_events": 3,
    "errors": [],
})


class TestParseScan(unittest.TestCase):
    def test_full_sample(self):
        r = system_info._parse_scan(SAMPLE)
        # 双显卡
        self.assertTrue(r["dual_gpu"])
        # HAGS 关闭
        self.assertFalse(r["hags"]["enabled"])
        self.assertEqual(r["hags"]["note"], "关闭")
        # 冲突软件识别
        self.assertTrue(any("Windhawk" in c for c in r["conflicts"]))
        # 运行进程透传
        self.assertIn("wallpaper64", r["processes"])
        # Wallpaper Engine 安装与缺失依赖
        self.assertTrue(r["wallpaper_engine"]["installed"])
        self.assertIn("libcef.dll", r["wallpaper_engine"]["missing_x86_dlls"])
        # 事件日志错误数
        self.assertEqual(r["dxgi_event_errors"], 3)
        # 结构完整
        for k in ("os", "gpus", "hags", "processes", "wallpaper_engine",
                  "dxgi_event_errors", "conflicts", "dual_gpu", "errors"):
            self.assertIn(k, r)

    def test_hags_enabled(self):
        raw = json.dumps({**json.loads(SAMPLE), "hags": 1})
        r = system_info._parse_scan(raw)
        self.assertTrue(r["hags"]["enabled"])
        self.assertEqual(r["hags"]["note"], "开启")

    def test_hags_unknown(self):
        raw = json.dumps({**json.loads(SAMPLE), "hags": "unknown"})
        r = system_info._parse_scan(raw)
        self.assertIsNone(r["hags"]["enabled"])

    def test_single_gpu_not_dual(self):
        gpus = [{"Name": "NVIDIA GeForce RTX 5060", "Status": "OK"}]
        raw = json.dumps({**json.loads(SAMPLE), "gpus": gpus})
        r = system_info._parse_scan(raw)
        self.assertFalse(r["dual_gpu"])

    def test_malformed_json_safe(self):
        # 损坏的 JSON 不应抛异常，应返回带 errors 的合法结构
        r = system_info._parse_scan("{not valid json")
        self.assertIn("errors", r)
        self.assertFalse(r["dual_gpu"])
        self.assertEqual(r["gpus"], [])

    def test_we_not_installed(self):
        raw = json.dumps({**json.loads(SAMPLE),
                          "we_path": None, "missing_dlls": [], "wallpaper32_present": None})
        r = system_info._parse_scan(raw)
        self.assertFalse(r["wallpaper_engine"]["installed"])


if __name__ == "__main__":
    unittest.main()
