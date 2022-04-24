# -*- coding: UTF-8 -*-
import unittest


from sensorsabtesting.abtest import *
import sensorsanalytics

SA_SERVER_URL = "http://10.120.240.69:8106/sa?project=customsubjectproject"

AB_URL = "http://10.120.103.57:8202/api/v2/abtest/online/results?project-key=03611F77720CB13DA4E8B726122D2EE2F95B7654"


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
        ab = SensorsABTest(AB_URL, self.sa, 0, 0, -2, 0)
        self.assertEqual(ab._event_cache_time, 1440)
        self.assertEqual(ab._event_cache_size, 4096)
        self.assertEqual(ab._experiment_cache_time, 1440)
        self.assertEqual(ab._experiment_cache_size, 4096)

    def test_async_error_params(self):
        ab = SensorsABTest(AB_URL, self.sa, enable_log=True)
        error_distinct_id = None
        error_experiment_variable_name = ""
        error_default_value = self.sa
        r = ab.async_fetch_ab_test(
            distinct_id=error_distinct_id,
            is_login_id=False,
            param_name="!!",
            default_value=1,
        )
        self.assertEqual(r.result, 1)

        r1 = ab.async_fetch_ab_test(
            distinct_id="111",
            is_login_id=False,
            param_name=error_experiment_variable_name,
            default_value=1,
        )
        self.assertEqual(r1.result, 1)

        r2 = ab.async_fetch_ab_test(
            distinct_id="111",
            is_login_id=False,
            param_name="1se",
            default_value=error_default_value,
        )
        self.assertIsInstance(r2.result, SensorsAnalytics, "类型错误")

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


if __name__ == "__main__":
    unittest.main()
