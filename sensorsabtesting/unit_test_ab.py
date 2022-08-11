# -*- coding: UTF-8 -*-
import time
import unittest

from datetime import datetime
from sensorsabtesting.abtest import *
import sensorsanalytics

SA_SERVER_URL = "https://sdkdebugtest.datasink.sensorsdata.cn/sa?project=default&token=cfb8b60e42e0ae9b"

AB_URL = "http://10.129.128.84:8202/api/v2/abtest/online/results?project-key=F58146ECC1B9CD7524DCF3157E9480AB97CBC632"
ERROR_AB_URL = "http://10.1291.128.84:8202/api/v2/abtest/online/results?project-key=F58146ECC1B9CD7524DCF3157E9480AB97CBC632"

class NormalTest(unittest.TestCase):
    def setUp(self):
        # 发送数据的超时时间，单位毫秒
        SA_REQUEST_TIMEOUT = 100000

        # 初始化 DefaultConsumer
        consumer = sensorsanalytics.DebugConsumer(SA_SERVER_URL, SA_REQUEST_TIMEOUT)

        # 使用 Consumer 来构造 SensorsAnalytics 对象
        self.sa = sensorsanalytics.SensorsAnalytics(consumer)

    def test_init_sa_error(self):
        with self.assertRaises(SensorsABIllegalArgumentsException):
            SensorsABTest(AB_URL, 1)

    def test_init_url_error(self):
        with self.assertRaises(SensorsABIllegalArgumentsException):
            SensorsABTest(None, self.sa)

    def test_init(self):
        ab = SensorsABTest(AB_URL, sa=self.sa, enable_log=True)
        self.assertIsInstance(ab, SensorsABTest)

    def test_cache(self):
        ab = SensorsABTest(base_url=AB_URL, sa=self.sa, enable_log=True)
        self.assertEqual(ab._event_cache_time, 1440)
        self.assertEqual(ab._event_cache_size, 4096)
        self.assertEqual(ab._experiment_cache_time, 1440)
        self.assertEqual(ab._experiment_cache_size, 4096)

    def test_event_cache_zero(self):
        ab = SensorsABTest(AB_URL, self.sa, -1, -1, -2, -1)
        self.assertEqual(ab._event_cache_time, 1440)
        self.assertEqual(ab._event_cache_size, 4096)
        self.assertEqual(ab._experiment_cache_time, 1440)
        self.assertEqual(ab._experiment_cache_size, 4096)

    def test_async_error_custom_ids(self):
        ids1 = {"": "b"}
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        r1 = ab.async_fetch_ab_test(
            distinct_id="111",
            is_login_id=False,
            param_name="!!",
            default_value=1,
            custom_ids=ids1,
        )
        self.assertEqual(r1.result, 1)
        ids2 = {"distinct_id": "b"}

        r2 = ab.async_fetch_ab_test(
            distinct_id="111",
            is_login_id=False,
            param_name="!!",
            default_value=1,
            custom_ids=ids2,
        )
        self.assertEqual(r2.result, 1)

    def test_default_value(self):
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        r1 = ab.async_fetch_ab_test(
            distinct_id="a123",
            is_login_id=True,
            param_name="int_experiment",
            default_value=-1,
        )
        self.assertEqual(r1.result, -1)

        r2 = ab.async_fetch_ab_test(
            distinct_id="111",
            is_login_id=False,
            param_name="abiefne",
            default_value=1,
        )
        self.assertEqual(r2.result, 1)

    def test_async_fetch_ab_test(self):
        """
        测试正常情况下的请求结果
        :return:
        """
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        # 默认情况
        result = ab.async_fetch_ab_test("AB1123456211", True, "num_test", 100, enable_auto_track_event=True)
        self.assertIn(result.result, [111, 222])
        result = ab.async_fetch_ab_test("AB1123456211", True, "string_test", "unknown", enable_auto_track_event=True)
        self.assertIn(result.result, ["hello", "world"])

    def test_fast_fetch_ab_test(self):
        """
        测试正常情况下的请求结果
        :return:
        """
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        result = ab.fast_fetch_ab_test("AB1123456211", True, "num_test", 100, enable_auto_track_event=True)
        self.assertIn(result.result, [111, 222])
        result = ab.fast_fetch_ab_test("AB1123456211", True, "string_test", "unknown", enable_auto_track_event=True)
        self.assertIn(result.result, ["hello", "world"])

    def test_fast_fetch_ab_test_work(self):
        """
        验证两次 fast 请求之间的时间间隔
        :return:
        """
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        start_time = time.time()
        result = ab.fast_fetch_ab_test("AB1123456211", True, "num_test", 100, enable_auto_track_event=True)
        self.assertIn(result.result, [111, 222])
        middle_time = time.time() - start_time
        start_time = time.time()
        result = ab.fast_fetch_ab_test("AB1123456211", True, "string_test", "unknown", enable_auto_track_event=True)
        end_time = time.time()
        self.assertIn(result.result, ["hello", "world"])
        self.assertLess((end_time - start_time), middle_time / 3, "Does the cache is enabled?")
        ab.close()

    def test_timeout(self):
        """
        验证 timeout 超时情况
        """
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        result = ab.async_fetch_ab_test("AB1123456211", True, "string_test", "unknown",
                                        enable_auto_track_event=False, timeout_seconds=0.01)
        self.assertIn(result.result, "unknown")

        result = ab.async_fetch_ab_test("AB1123456211", True, "string_test", "unknown",
                                        enable_auto_track_event=False,
                                        timeout_seconds=urllib3.Timeout(connect=2, read=2))
        self.assertIn(result.result, ["hello", "world"])

        result = ab.async_fetch_ab_test("AB1123456211", True, "string_test", "unknown",
                                        enable_auto_track_event=False,
                                        timeout_seconds=urllib3.Timeout(connect=1, read=0.01))
        self.assertIn(result.result, "unknown")

        ab.close()

    def test_error_server_url(self):
        """
        验证 server url 出现出去的场景
        :return:
        """
        ab = SensorsABTest(ERROR_AB_URL, self.sa, enable_log=True)
        result = ab.fast_fetch_ab_test("AB1123456211", True, "num_test", 100, enable_auto_track_event=True)
        self.assertEqual(result.result, 100)
        result = ab.async_fetch_ab_test("AB1123456211", True, "string_test", "unknown", enable_auto_track_event=True)
        self.assertEqual(result.result, "unknown")
        ab.close()




if __name__ == "__main__":
    unittest.main()
