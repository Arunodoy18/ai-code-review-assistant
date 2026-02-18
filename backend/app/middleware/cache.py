"""
API Response Caching Middleware

Caches GET requests to improve performance and reduce database load.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.cache import cache
import json
from typing import Callable


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """Middleware to cache API responses"""
    
    # Routes to cache and their TTL in seconds
    CACHE_CONFIG = {
        "/api/analysis/runs": 10,       # 10 seconds for runs list (frequently updated)
        "/api/projects": 300,           # 5 minutes for projects list
        "/api/config/rules": 600,       # 10 minutes for rules (rarely change)
        "/api/config/projects/": 120,   # 2 minutes for project config
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            # For non-GET requests, invalidate related cache
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                self._invalidate_cache(request.url.path)
            return await call_next(request)
        
        # Check if route should be cached
        cache_ttl = self._get_cache_ttl(request.url.path)
        if cache_ttl is None:
            return await call_next(request)
        
        # Create cache key from URL and query params
        cache_key = f"api_response:{request.url.path}:{str(request.query_params)}"
        
        # Try to get from cache
        cached_response = cache.get(cache_key, ttl=cache_ttl)
        if cached_response:
            return Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=dict(cached_response["headers"]),
                media_type=cached_response.get("media_type", "application/json")
            )
        
        # Execute request and cache response
        response = await call_next(request)
        
        # Only cache successful responses
        if 200 <= response.status_code < 300:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Cache the response
            cache.set(cache_key, {
                "content": body,
                "status_code": response.status_code,
                "headers": {k: v for k, v in response.headers.items() if k.lower() != "set-cookie"},
                "media_type": response.media_type
            })
            
            # Return response with body
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        return response
    
    def _get_cache_ttl(self, path: str) -> int:
        """Get cache TTL for a given path"""
        for route_pattern, ttl in self.CACHE_CONFIG.items():
            if path.startswith(route_pattern):
                return ttl
        return None
    
    def _invalidate_cache(self, path: str):
        """Invalidate cache for related routes"""
        # Map of paths to invalidate
        invalidate_patterns = {
            "/api/runs": ["api_response:/api/runs"],
            "/api/projects": ["api_response:/api/projects"],
            "/api/config": ["api_response:/api/config"],
            "/api/analysis": ["api_response:/api/runs", "api_response:/api/analysis"],
        }
        
        for pattern_key, cache_patterns in invalidate_patterns.items():
            if path.startswith(pattern_key):
                for cache_pattern in cache_patterns:
                    cache.invalidate_pattern(cache_pattern)
