import threading
import time
import heapq
from typing import Any


class TTLDictionary:
    """
    A dictionary-like object where each key-value pair has a time-to-live (TTL).
    The key-value pairs are automatically removed from the dictionary when their TTL expires.

    Attributes:
        lock (threading.RLock): A lock for thread-safe operations.
        data (dict): The underlying data store.
        expiry_times (list): A heap of (expiry_time, key) tuples.
        daemon_sleep_time (int): The time in seconds the daemon thread sleeps before cleaning up expired key-value pairs.
        collect_thread (threading.Thread): A daemon thread that cleans up expired key-value pairs.
        _stop_thread (bool): A flag to signal the daemon thread to stop.
    """

    def __init__(self, daemon_sleep_time: int = 1):
        """
        Initialize the TTLDictionary.

        Args:
            daemon_sleep_time (int, optional): The time in seconds the daemon thread sleeps before
                                               cleaning up expired key-value pairs. Defaults to 1.
        """
        self._stop_thread = False
        self.lock = threading.RLock()
        self.data = {}
        self.expiry_times = []
        self.daemon_sleep_time = daemon_sleep_time
        self.collect_thread = threading.Thread(
            target=self._collect_expired, daemon=True
        )
        self.collect_thread.start()

    def _collect_expired(self):
        """
        Continuously collect and remove expired key-value pairs.
        """
        while not self._stop_thread:
            with self.lock:
                self._clean_expired_unsafe()
            time.sleep(self.daemon_sleep_time)

    def _clean_expired_unsafe(self):
        """
        Remove all expired key-value pairs.
        """
        with self.lock:
            now = time.time()
            while self.expiry_times and self.expiry_times[0][0] <= now:
                _, key = heapq.heappop(self.expiry_times)
                try:
                    del self.data[key]
                except KeyError:
                    pass

    def __setitem__(self, key: Any, value_and_ttl: tuple[Any, int] | Any):
        """
        Set a key-value pair with a TTL.

        Args:
            key (Any): The key.
            value_and_ttl (tuple[Any, int] | Any): A tuple of the value and the TTL in seconds.
                                                   If no TTL is provided, the key-value pair will not expire.
        """
        if isinstance(value_and_ttl, tuple):
            value, ttl_seconds = value_and_ttl
            if ttl_seconds is None:
                expiry_time = float("inf")
            else:
                expiry_time = time.time() + ttl_seconds
        else:
            value = value_and_ttl
            expiry_time = float("inf")

        with self.lock:
            if key in self.data:
                self.expiry_times = [
                    (expiry_time, k) for expiry_time, k in self.expiry_times if k != key
                ]

            self.data[key] = value
            heapq.heappush(self.expiry_times, (expiry_time, key))

    def __getitem__(self, key):
        """
        Get the value associated with a key.

        Args:
            key (Any): The key.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key is not found in the dictionary.
        """
        with self.lock:
            self._clean_expired_unsafe()
            try:
                return self.data[key]
            except KeyError:
                raise KeyError(f"Key {key} not found in the dictionary.")

    def __delitem__(self, key: Any) -> None:
        """
        Remove a key-value pair.

        Args:
            key (Any): The key to remove.

        Raises:
            KeyError: If the key is not found in the dictionary.
        """
        with self.lock:
            try:
                del self.data[key]
            except KeyError:
                raise KeyError(f"Key {key} not found in the dictionary.")
            self.expiry_times = [
                (expiry_time, k) for expiry_time, k in self.expiry_times if k != key
            ]

    def __contains__(self, key: Any) -> bool:
        """
        Check if a key is in the dictionary.

        Args:
            key (Any): The key to check.

        Returns:
            bool: True if the key is in the dictionary, False otherwise.
        """
        with self.lock:
            return key in self.data

    def __len__(self):
        """
        Get the number of key-value pairs in the dictionary.

        Returns:
            int: The number of key-value pairs in the dictionary.
        """
        with self.lock:
            return len(self.data)

    def __del__(self):
        """
        Destructor method to stop the daemon thread when the TTLDictionary is deleted.
        """
        self._stop_thread = True
        self.collect_thread.join()

    def keys(self) -> list:
        """
        Get a list of all keys in the dictionary.

        Returns:
            list: A list of all keys in the dictionary.
        """
        with self.lock:
            return list(self.data.keys())

    def values(self) -> list:
        """
        Get a list of all values in the dictionary.

        Returns:
            list: A list of all values in the dictionary.
        """
        with self.lock:
            return list(self.data.values())

    def items(self) -> list:
        """
        Get a list of all key-value pairs in the dictionary.

        Returns:
            list: A list of all key-value pairs in the dictionary.
        """
        with self.lock:
            return list(self.data.items())

    def get(self, key, default=None):
        """
        Get the value associated with a key, or a default value if the key is not in the dictionary.

        Args:
            key (Any): The key.
            default (Any, optional): The default value to return if the key is not in the dictionary. Defaults to None.

        Returns:
            Any: The value associated with the key, or the default value if the key is not in the dictionary.
        """
        with self.lock:
            self._clean_expired_unsafe()
            return self.data.get(key, default)
