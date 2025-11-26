"""
Rate Limiter for API token usage
Implements sliding window rate limiting for TPM (tokens per minute)
"""
import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Token-based rate limiter using sliding window algorithm

    Tracks token usage over a 60-second window and applies delays
    to stay within the configured TPM (tokens per minute) limit.
    """

    def __init__(self, tokens_per_minute: int, buffer_percent: float = 0.9):
        """
        Initialize rate limiter

        Args:
            tokens_per_minute: Maximum tokens allowed per minute
            buffer_percent: Safety buffer (0.9 = use 90% of limit)
        """
        self.tpm_limit = tokens_per_minute
        self.buffer_percent = buffer_percent
        self.effective_limit = int(tokens_per_minute * buffer_percent)

        # Sliding window: stores (timestamp, tokens) tuples
        self.usage_window = deque()

        print(f"[RateLimiter] Initialized: {tokens_per_minute:,} TPM (effective: {self.effective_limit:,})")

    def _clean_old_entries(self):
        """Remove entries older than 60 seconds from the window"""
        current_time = time.time()
        cutoff_time = current_time - 60  # 60 seconds ago

        # Remove old entries from the front of the deque
        while self.usage_window and self.usage_window[0][0] < cutoff_time:
            self.usage_window.popleft()

    def _get_current_usage(self) -> int:
        """Calculate total tokens used in the last 60 seconds"""
        self._clean_old_entries()
        return sum(tokens for _, tokens in self.usage_window)

    def _get_available_capacity(self) -> int:
        """Get remaining token capacity in current window"""
        current_usage = self._get_current_usage()
        return max(0, self.effective_limit - current_usage)

    def _calculate_wait_time(self, required_tokens: int) -> float:
        """
        Calculate how long to wait before we have capacity

        Args:
            required_tokens: Number of tokens needed

        Returns:
            Seconds to wait (0 if capacity available now)
        """
        current_usage = self._get_current_usage()

        if current_usage + required_tokens <= self.effective_limit:
            return 0.0  # We have capacity now

        # Find when the oldest entry will expire
        if not self.usage_window:
            return 0.0

        # Calculate when we'll have enough capacity
        oldest_timestamp = self.usage_window[0][0]
        time_until_oldest_expires = max(0, 60 - (time.time() - oldest_timestamp))

        # Conservative estimate: wait until the oldest entry expires
        return time_until_oldest_expires + 1  # +1 second safety margin

    def wait_if_needed(self, estimated_tokens: int = 500):
        """
        Wait if necessary to stay within rate limit

        Args:
            estimated_tokens: Estimated tokens for next request
        """
        wait_time = self._calculate_wait_time(estimated_tokens)

        if wait_time > 0:
            current_usage = self._get_current_usage()
            print(f"\n[RateLimiter] Approaching limit: {current_usage:,}/{self.effective_limit:,} tokens used")
            print(f"[RateLimiter] Waiting {wait_time:.1f}s before next request...")
            time.sleep(wait_time)
            print(f"[RateLimiter] Resumed")

    def record_usage(self, tokens_used: int):
        """
        Record tokens used in a request

        Args:
            tokens_used: Actual tokens used in the request
        """
        current_time = time.time()
        self.usage_window.append((current_time, tokens_used))

        # Clean old entries periodically
        self._clean_old_entries()

    def get_stats(self) -> dict:
        """Get current rate limiter statistics"""
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
        """Reset the rate limiter (clear all usage history)"""
        self.usage_window.clear()
        print(f"[RateLimiter] Reset")