import time
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.default_limits = {
            "auth": {"requests": 5, "window": 60},  # 5 requests per minute
            "otp": {"requests": 3, "window": 300},  # 3 OTP requests per 5 minutes
            "login": {"requests": 5, "window": 300},  # 5 login attempts per 5 minutes
            "email": {"requests": 10, "window": 3600},  # 10 emails per hour
            "ip": {"requests": 100, "window": 3600}  # 100 requests per hour per IP
        }
        
        # In-memory storage for development (use Redis in production)
        self.memory_store = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
    
    async def is_rate_limited(self, identifier: str, action: str = "auth", ip_address: str = None) -> bool:
        """
        Check if identifier is rate limited
        
        Args:
            identifier: User ID, phone number, email, or IP address
            action: Action type (auth, otp, login, email, ip)
            ip_address: IP address for IP-based rate limiting
            
        Returns:
            True if rate limited, False otherwise
        """
        try:
            # Check if we need to cleanup
            await self._check_cleanup()
            
            # Get rate limit for action
            limit = self.default_limits.get(action, self.default_limits["auth"])
            max_requests = limit["requests"]
            window_seconds = limit["window"]
            
            # Create rate limit key
            rate_key = f"rate_limit:{action}:{identifier}"
            
            # Check IP-based rate limiting if IP is provided
            if ip_address and action in ["auth", "login", "otp"]:
                ip_key = f"rate_limit:ip:{ip_address}"
                ip_limited = await self._check_rate_limit(ip_key, max_requests, window_seconds)
                if ip_limited:
                    logger.warning(f"IP {ip_address} rate limited for action {action}")
                    return True
            
            # Check identifier-based rate limiting
            return await self._check_rate_limit(rate_key, max_requests, window_seconds)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return False
    
    async def _check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if key is rate limited"""
        try:
            current_time = time.time()
            
            # Use Redis if available
            if self.redis_client:
                # Get current count
                count = await self.redis_client.get(key)
                count = int(count) if count else 0
                
                # Check if limit exceeded
                if count >= max_requests:
                    return True
                
                # Increment count
                await self.redis_client.incr(key)
                await self.redis_client.expire(key, window_seconds)
                
            else:
                # Use memory store
                if key not in self.memory_store:
                    self.memory_store[key] = {
                        "count": 0,
                        "first_request": current_time,
                        "window_start": current_time
                    }
                
                entry = self.memory_store[key]
                
                # Check if window has expired
                if current_time - entry["window_start"] > window_seconds:
                    # Reset window
                    entry["count"] = 1
                    entry["window_start"] = current_time
                    entry["first_request"] = current_time
                else:
                    # Increment count
                    entry["count"] += 1
                
                # Check if limit exceeded
                if entry["count"] >= max_requests:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return False
    
    async def record_attempt(self, identifier: str, action: str = "auth", ip_address: str = None):
        """Record an authentication attempt"""
        try:
            # Record identifier-based attempt
            rate_key = f"rate_limit:{action}:{identifier}"
            await self._record_attempt(rate_key)
            
            # Record IP-based attempt if IP is provided
            if ip_address:
                ip_key = f"rate_limit:ip:{ip_address}"
                await self._record_attempt(ip_key)
                
        except Exception as e:
            logger.error(f"Failed to record attempt: {str(e)}")
    
    async def _record_attempt(self, key: str):
        """Record an attempt for a key"""
        try:
            current_time = time.time()
            
            if self.redis_client:
                await self.redis_client.incr(key)
            else:
                if key not in self.memory_store:
                    self.memory_store[key] = {
                        "count": 0,
                        "first_request": current_time,
                        "window_start": current_time
                    }
                
                self.memory_store[key]["count"] += 1
                
        except Exception as e:
            logger.error(f"Failed to record attempt: {str(e)}")
    
    async def get_rate_limit_info(self, identifier: str, action: str = "auth") -> Dict:
        """Get rate limit information for identifier"""
        try:
            rate_key = f"rate_limit:{action}:{identifier}"
            
            if self.redis_client:
                count = await self.redis_client.get(rate_key)
                count = int(count) if count else 0
                
                # Get TTL
                ttl = await self.redis_client.ttl(rate_key)
                limit = self.default_limits.get(action, self.default_limits["auth"])
                
                return {
                    "identifier": identifier,
                    "action": action,
                    "current_count": count,
                    "max_requests": limit["requests"],
                    "window_seconds": limit["window"],
                    "remaining_requests": max(0, limit["requests"] - count),
                    "reset_time": datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
                }
            else:
                if rate_key not in self.memory_store:
                    return {
                        "identifier": identifier,
                        "action": action,
                        "current_count": 0,
                        "max_requests": self.default_limits.get(action, self.default_limits["auth"])["requests"],
                        "window_seconds": self.default_limits.get(action, self.default_limits["auth"])["window"],
                        "remaining_requests": self.default_limits.get(action, self.default_limits["auth"])["requests"],
                        "reset_time": None
                    }
                
                entry = self.memory_store[rate_key]
                limit = self.default_limits.get(action, self.default_limits["auth"])
                
                return {
                    "identifier": identifier,
                    "action": action,
                    "current_count": entry["count"],
                    "max_requests": limit["requests"],
                    "window_seconds": limit["window"],
                    "remaining_requests": max(0, limit["requests"] - entry["count"]),
                    "reset_time": datetime.utcnow() + timedelta(seconds=limit["window"] - (time.time() - entry["window_start"])) if entry["count"] > 0 else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {str(e)}")
            return {}
    
    async def reset_rate_limit(self, identifier: str, action: str = "auth"):
        """Reset rate limit for identifier"""
        try:
            rate_key = f"rate_limit:{action}:{identifier}"
            
            if self.redis_client:
                await self.redis_client.delete(rate_key)
            else:
                if rate_key in self.memory_store:
                    del self.memory_store[rate_key]
                    
            logger.info(f"Rate limit reset for {identifier} on action {action}")
            
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {str(e)}")
    
    async def _check_cleanup(self):
        """Check if cleanup is needed"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup()
            self.last_cleanup = current_time
    
    async def _cleanup(self):
        """Clean up expired rate limit entries"""
        try:
            current_time = time.time()
            
            if self.redis_client:
                # Redis handles TTL automatically
                pass
            else:
                # Clean up memory store
                expired_keys = []
                for key, entry in self.memory_store.items():
                    if current_time - entry["window_start"] > self.default_limits.get("auth", {"window": 60})["window"] * 2:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.memory_store[key]
                    
            logger.info("Rate limit cleanup completed")
            
        except Exception as e:
            logger.error(f"Rate limit cleanup error: {str(e)}")
    
    async def _cleanup_task(self):
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup()
            except Exception as e:
                logger.error(f"Cleanup task error: {str(e)}")
    
    async def get_all_rate_limits(self) -> Dict:
        """Get all current rate limits"""
        try:
            rate_limits = {}
            
            if self.redis_client:
                # Get all rate limit keys
                keys = await self.redis_client.keys("rate_limit:*")
                for key in keys:
                    identifier = key.split(":")[2]
                    action = key.split(":")[1]
                    rate_limits[f"{action}:{identifier}"] = await self.get_rate_limit_info(identifier, action)
            else:
                # Get from memory store
                for key in self.memory_store.keys():
                    identifier = key.split(":")[2]
                    action = key.split(":")[1]
                    rate_limits[f"{action}:{identifier}"] = await self.get_rate_limit_info(identifier, action)
            
            return rate_limits
            
        except Exception as e:
            logger.error(f"Failed to get all rate limits: {str(e)}")
            return {}
    
    async def set_custom_limit(self, action: str, max_requests: int, window_seconds: int):
        """Set custom rate limit for action"""
        try:
            self.default_limits[action] = {
                "requests": max_requests,
                "window": window_seconds
            }
            logger.info(f"Custom rate limit set for {action}: {max_requests} requests per {window_seconds} seconds")
        except Exception as e:
            logger.error(f"Failed to set custom limit: {str(e)}")
    
    async def get_statistics(self) -> Dict:
        """Get rate limiting statistics"""
        try:
            stats = {
                "total_limits": len(self.default_limits),
                "memory_store_size": len(self.memory_store) if not self.redis_client else 0,
                "cleanup_interval": self.cleanup_interval,
                "last_cleanup": datetime.fromtimestamp(self.last_cleanup).isoformat(),
                "limits": self.default_limits
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}