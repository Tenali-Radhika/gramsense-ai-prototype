"""
Rate limiting middleware for API protection.

Implements a simple token bucket algorithm for rate limiting requests.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time


class RateLimiter:
    """Simple token bucket rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per IP
            requests_per_hour: Maximum requests per hour per IP
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Storage: {ip: {"minute": [(timestamp, count)], "hour": [(timestamp, count)]}}
        self._storage: Dict[str, Dict[str, list]] = {}
        
        # Last cleanup time
        self._last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory bloat."""
        current_time = time.time()
        
        # Cleanup every 5 minutes
        if current_time - self._last_cleanup < 300:
            return
        
        self._last_cleanup = current_time
        cutoff_time = current_time - 3600  # Keep last hour
        
        # Remove old IPs
        ips_to_remove = []
        for ip, data in self._storage.items():
            # Remove old minute entries
            data["minute"] = [
                (ts, count) for ts, count in data["minute"]
                if current_time - ts < 60
            ]
            # Remove old hour entries
            data["hour"] = [
                (ts, count) for ts, count in data["hour"]
                if current_time - ts < 3600
            ]
            
            # Mark IP for removal if no recent activity
            if not data["minute"] and not data["hour"]:
                ips_to_remove.append(ip)
        
        for ip in ips_to_remove:
            del self._storage[ip]
    
    def _get_request_count(self, ip: str, window: str) -> int:
        """Get request count for an IP in a time window."""
        if ip not in self._storage:
            self._storage[ip] = {"minute": [], "hour": []}
        
        current_time = time.time()
        window_data = self._storage[ip][window]
        
        # Determine window size
        window_seconds = 60 if window == "minute" else 3600
        
        # Count requests in current window
        count = sum(
            c for ts, c in window_data
            if current_time - ts < window_seconds
        )
        
        return count
    
    def _record_request(self, ip: str):
        """Record a request for an IP."""
        if ip not in self._storage:
            self._storage[ip] = {"minute": [], "hour": []}
        
        current_time = time.time()
        
        # Add to both windows
        self._storage[ip]["minute"].append((current_time, 1))
        self._storage[ip]["hour"].append((current_time, 1))
    
    def check_rate_limit(self, ip: str) -> Tuple[bool, str, int]:
        """
        Check if request should be allowed.
        
        Args:
            ip: Client IP address
        
        Returns:
            Tuple of (allowed, reason, retry_after_seconds)
        """
        # Cleanup old entries periodically
        self._cleanup_old_entries()
        
        # Check minute limit
        minute_count = self._get_request_count(ip, "minute")
        if minute_count >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute", 60
        
        # Check hour limit
        hour_count = self._get_request_count(ip, "hour")
        if hour_count >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour", 3600
        
        # Record this request
        self._record_request(ip)
        
        return True, "", 0
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        return {
            "tracked_ips": len(self._storage),
            "requests_per_minute_limit": self.requests_per_minute,
            "requests_per_hour_limit": self.requests_per_hour,
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to enforce rate limiting."""
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    # Check rate limit
    allowed, reason, retry_after = rate_limiter.check_rate_limit(client_ip)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": reason,
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit-Minute"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Limit-Hour"] = str(rate_limiter.requests_per_hour)
    
    return response
