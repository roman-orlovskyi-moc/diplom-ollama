import time
from collections import deque
from typing import Optional


class RateLimiter:

    def __init__(self, tokens_per_minute: int, buffer_percent: float = 0.9):
        self.tpm_limit = tokens_per_minute
        self.buffer_percent = buffer_percent
        self.effective_limit = int(tokens_per_minute * buffer_percent)

        self.usage_window = deque()

        print(f"[RateLimiter] Initialized: {tokens_per_minute:,} TPM (effective: {self.effective_limit:,})")

    def _clean_old_entries(self):
        current_time = time.time()
        cutoff_time = current_time - 60

        while self.usage_window and self.usage_window[0][0] < cutoff_time:
            self.usage_window.popleft()

    def _get_current_usage(self) -> int:
        self._clean_old_entries()
        return sum(tokens for _, tokens in self.usage_window)

    def _get_available_capacity(self) -> int:
        current_usage = self._get_current_usage()
        return max(0, self.effective_limit - current_usage)

    def _calculate_wait_time(self, required_tokens: int) -> float:
        current_usage = self._get_current_usage()

        if current_usage + required_tokens <= self.effective_limit:
            return 0.0

        if not self.usage_window:
            return 0.0

        oldest_timestamp = self.usage_window[0][0]
        time_until_oldest_expires = max(0, 60 - (time.time() - oldest_timestamp))

        return time_until_oldest_expires + 1

    def wait_if_needed(self, estimated_tokens: int = 500):
        wait_time = self._calculate_wait_time(estimated_tokens)

        if wait_time > 0:
            current_usage = self._get_current_usage()
            print(f"\n[RateLimiter] Approaching limit: {current_usage:,}/{self.effective_limit:,} tokens used")
            print(f"[RateLimiter] Waiting {wait_time:.1f}s before next request...")
            time.sleep(wait_time)
            print(f"[RateLimiter] Resumed")

    def record_usage(self, tokens_used: int):
        current_time = time.time()
        self.usage_window.append((current_time, tokens_used))

        self._clean_old_entries()

    def get_stats(self) -> dict:
        current_usage = self._get_current_usage()
        available = self._get_available_capacity()

        return {
            'current_usage': current_usage,
            'limit': self.effective_limit,
            'available': available,
            'utilization_percent': (current_usage / self.effective_limit * 100) if self.effective_limit > 0 else 0,
            'window_size': len(self.usage_window)
        }

    def reset(self):
        self.usage_window.clear()
        print(f"[RateLimiter] Reset")