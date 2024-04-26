import threading
import time
import unittest

from ttl_dictionary import TTLDictionary


class TTLDictionaryTests(unittest.TestCase):
    def setUp(self):
        self.ttl_dict = TTLDictionary()

    def test_ttl_dict_stores_and_retrieves_items(self):
        self.ttl_dict["key"] = ("value", 5)
        self.assertEqual(self.ttl_dict["key"], "value")

    def test_ttl_dict_removes_expired_items(self):
        self.ttl_dict["key"] = ("value", 1)
        time.sleep(2)
        self.assertNotIn("key", self.ttl_dict)

    def test_ttl_dict_supports_infinite_ttl(self):
        self.ttl_dict["key"] = "value"
        time.sleep(2)
        self.assertIn("key", self.ttl_dict)

    def test_ttl_dict_supports_item_deletion(self):
        self.ttl_dict["key"] = ("value", 5)
        del self.ttl_dict["key"]
        self.assertNotIn("key", self.ttl_dict)

    def test_ttl_dict_returns_correct_length(self):
        self.ttl_dict["key1"] = ("value1", 5)
        self.ttl_dict["key2"] = ("value2", 5)
        self.assertEqual(len(self.ttl_dict), 2)

    def test_ttl_dict_returns_all_keys(self):
        self.ttl_dict["key1"] = ("value1", 5)
        self.ttl_dict["key2"] = ("value2", 5)
        self.assertCountEqual(self.ttl_dict.keys(), ["key1", "key2"])

    def test_ttl_dict_returns_all_values(self):
        self.ttl_dict["key1"] = ("value1", 5)
        self.ttl_dict["key2"] = ("value2", 5)
        self.assertCountEqual(self.ttl_dict.values(), ["value1", "value2"])

    def test_ttl_dict_returns_all_items(self):
        self.ttl_dict["key1"] = ("value1", 5)
        self.ttl_dict["key2"] = ("value2", 5)
        self.assertCountEqual(
            self.ttl_dict.items(), [("key1", "value1"), ("key2", "value2")]
        )

    def test_ttl_dict_get_method_returns_default_for_missing_key(self):
        self.assertEqual(self.ttl_dict.get("missing_key", "default"), "default")

    def test_multiple_keys_with_different_ttl(self):
        self.ttl_dict["key1"] = ("value1", 1)
        self.ttl_dict["key2"] = ("value2", 2)
        time.sleep(1.5)
        self.assertNotIn("key1", self.ttl_dict)
        self.assertIn("key2", self.ttl_dict)

    def test_multiple_keys_with_infinite_ttl(self):
        self.ttl_dict["key1"] = "value1"
        self.ttl_dict["key2"] = "value2"
        time.sleep(2)
        self.assertIn("key1", self.ttl_dict)
        self.assertIn("key2", self.ttl_dict)

    def test_multiple_keys_with_mixed_ttl(self):
        self.ttl_dict["key1"] = ("value1", 1)
        self.ttl_dict["key2"] = "value2"
        time.sleep(2)
        self.assertNotIn("key1", self.ttl_dict)
        self.assertIn("key2", self.ttl_dict)

    def test_concurrent_access_with_multiple_keys(self):
        exceptions = []

        def worker():
            try:
                for i in range(1000):
                    key = f"key{i}"
                    self.ttl_dict[key] = ("value", 5)
                    _ = self.ttl_dict[key]
                    del self.ttl_dict[key]
            except Exception as e:
                exceptions.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(self.ttl_dict), 0)
        self.assertEqual(
            len(exceptions), 0, f"Exceptions occurred in worker threads: {exceptions}"
        )

    def test_no_deadlock_under_concurrent_access(self):
        exceptions = []

        def worker():
            try:
                for _ in range(1000):
                    self.ttl_dict["key"] = ("value", 5)
                    _ = self.ttl_dict["key"]
                    del self.ttl_dict["key"]
            except Exception as e:
                exceptions.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(self.ttl_dict), 0)
        self.assertEqual(
            len(exceptions), 0, f"Exceptions occurred in worker threads: {exceptions}"
        )

    def test_concurrent_access_with_multiple_keys_and_ttl(self):
        exceptions = []

        def worker():
            try:
                for i in range(1000):
                    key = f"key{i}"
                    self.ttl_dict[key] = ("value", i % 5)
                    time.sleep(0.001)
                    if self.ttl_dict.get(key, None) is not None:
                        del self.ttl_dict[key]

            except Exception as e:
                exceptions.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(self.ttl_dict), 0)
        self.assertEqual(
            len(exceptions), 0, f"Exceptions occurred in worker threads: {exceptions}"
        )


if __name__ == "__main__":
    unittest.main()
