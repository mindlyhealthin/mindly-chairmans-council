"""Authentication and multi-tenant middleware for the council API."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, Header, Request
import hashlib
import json

logger = logging.getLogger(__name__)

from domain_config import HealthcareDomainConfig
from firebase_service import firebase_service


class TenantContext:
    """Context for multi-tenant operations."""

    def __init__(self, tenant_id: str, user_id: str, user_role: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.user_role = user_role
        self.permissions = self._get_permissions()

    def _get_permissions(self) -> list:
        """Get permissions based on user role."""
        role_config = HealthcareDomainConfig.get_role_config(self.user_role)
        return role_config.get("permissions", [])

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        if "*" in self.permissions:
            return True
        return permission in self.permissions

    def can_access_patient(self, patient_id: str) -> bool:
        """Check if user can access a patient."""
        role_config = HealthcareDomainConfig.get_role_config(self.user_role)
        if role_config.get("can_access_all_patients", False):
            return True
        # Additional checks can be added here for granular access control
        return True


class AuthMiddleware:
    """Authentication middleware for API requests."""

    def __init__(self, api_key_secret: str = None):
        self.api_key_secret = api_key_secret or "mindly-default-secret"
        self.token_cache = {}  # Simple in-memory cache

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return tenant info."""
        try:
            # Hash the API key for security
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Check cache first
            if key_hash in self.token_cache:
                cached = self.token_cache[key_hash]
                if cached["expires_at"] > datetime.utcnow():
                    return cached["data"]
            
            # Verify via Firebase (would be implemented)
            # For now, accept API key format: "sk-chairmancouncil-{tenant_id}-{user_id}"
            if api_key.startswith("sk-chairmancouncil-"):
                parts = api_key.split("-")
                if len(parts) >= 4:
                    tenant_id = parts[2]
                    user_id = parts[3]
                    
                    # Get tenant config from Firebase
                    tenant_config = firebase_service.get_tenant_config(tenant_id)
                    
                    if tenant_config:
                        data = {
                            "tenant_id": tenant_id,
                            "user_id": user_id,
                            "tenant_name": tenant_config.get("organization_name", "Unknown"),
                            "specialty": tenant_config.get("specialty", "healthcare")
                        }
                        
                        # Cache for 1 hour
                        self.token_cache[key_hash] = {
                            "data": data,
                            "expires_at": datetime.utcnow() + timedelta(hours=1)
                        }
                        
                        return data
            
            return None
        except Exception as e:
            logger.error(f"Error verifying API key: {e}")
            return None

    def create_tenant_context(self, api_key: str, user_role: str = "clinician") -> Optional[TenantContext]:
        """Create a tenant context from API key."""
        verified = self.verify_api_key(api_key)
        if not verified:
            return None
        
        return TenantContext(
            tenant_id=verified["tenant_id"],
            user_id=verified["user_id"],
            user_role=user_role
        )


class RateLimiter:
    """Rate limiter for API endpoints."""

    def __init__(self):
        self.requests = {}  # {tenant_id: {timestamp: count}}

    def is_allowed(self, tenant_id: str, limit_per_minute: int = 30) -> bool:
        """Check if request is within rate limit."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        if tenant_id not in self.requests:
            self.requests[tenant_id] = []
        
        # Remove old requests
        self.requests[tenant_id] = [
            req_time for req_time in self.requests[tenant_id]
            if req_time > minute_ago
        ]
        
        if len(self.requests[tenant_id]) >= limit_per_minute:
            return False
        
        self.requests[tenant_id].append(now)
        return True


# Global instances
auth_middleware = AuthMiddleware()
rate_limiter = RateLimiter()


def require_auth(func):
    """Decorator to require authentication for endpoints."""
    @wraps(func)
    async def wrapper(request: Request, authorization: Optional[str] = Header(None), *args, **kwargs):
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing API key")
        
        # Extract API key from "Bearer {key}" format
        try:
            parts = authorization.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                api_key = parts[1]
            else:
                api_key = authorization
        except:
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        # Verify API key
        tenant_info = auth_middleware.verify_api_key(api_key)
        if not tenant_info:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Store in request state for use in endpoint
        request.state.tenant_id = tenant_info["tenant_id"]
        request.state.user_id = tenant_info["user_id"]
        request.state.tenant_context = auth_middleware.create_tenant_context(api_key)
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request.state, "tenant_context"):
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            if not request.state.tenant_context.has_permission(permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator