"""Firebase Firestore service for persistence layer."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Firebase imports - handled with try/except for flexibility
try:
    from firebase_admin import firestore, credentials
    import firebase_admin
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase not installed. Using mock mode.")

from config import settings


class FirebaseService:
    """Service for interacting with Firebase Firestore."""

    def __init__(self):
        """Initialize Firebase Admin SDK."""
        self.db = None
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase not available. Using mock mode.")
            return
            
        try:
            if not firebase_admin._apps:
                if settings.firebase_credentials_path != "firebase_credentials.json":
                    creds = credentials.Certificate(settings.firebase_credentials_path)
                    firebase_admin.initialize_app(creds)
                else:
                    firebase_admin.initialize_app()
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.warning(f"Firebase init failed: {e}. Using mock mode.")
            self.db = None

    def save_council_query(self, query: str, response: Dict[str, Any], 
                          domain: str = "healthcare", tenant_id: str = "default") -> str:
        """Save a council query and response to Firestore."""
        if not self.db:
            logger.warning("Firestore unavailable. Skipping save.")
            return "mock_id"
            
        try:
            doc_data = {
                "query": query,
                "response": response,
                "domain": domain,
                "tenant_id": tenant_id,
                "created_at": datetime.utcnow(),
                "model_votes": response.get("model_votes", {}),
                "chairman_reasoning": response.get("chairman_reasoning", ""),
            }
            
            collection = f"tenants/{tenant_id}/council_queries"
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(doc_data)
            logger.info(f"Council query saved: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error saving council query: {e}")
            raise

    def get_council_query(self, query_id: str, tenant_id: str = "default") -> Optional[Dict]:
        """Retrieve a council query."""
        if not self.db:
            return None
            
        try:
            collection = f"tenants/{tenant_id}/council_queries"
            doc = self.db.collection(collection).document(query_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error retrieving council query: {e}")
            return None

    def save_healthcare_context(self, context: Dict[str, Any], 
                               tenant_id: str = "default") -> str:
        """Save healthcare context and patient information."""
        if not self.db:
            return "mock_id"
            
        try:
            context["created_at"] = datetime.utcnow()
            context["tenant_id"] = tenant_id
            
            collection = f"tenants/{tenant_id}/healthcare_contexts"
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(context)
            logger.info(f"Healthcare context saved: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error saving healthcare context: {e}")
            raise

    def create_tenant(self, tenant_id: str, tenant_config: Dict[str, Any]) -> None:
        """Create a new tenant."""
        if not self.db:
            logger.warning("Firestore unavailable. Skipping tenant creation.")
            return
            
        try:
            tenant_config["created_at"] = datetime.utcnow()
            tenant_config["status"] = "active"
            self.db.collection("tenants").document(tenant_id).set(tenant_config)
            logger.info(f"Tenant created: {tenant_id}")
        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            raise

    def get_tenant_config(self, tenant_id: str) -> Optional[Dict]:
        """Get tenant configuration."""
        if not self.db:
            return None
            
        try:
            doc = self.db.collection("tenants").document(tenant_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error retrieving tenant config: {e}")
            return None


# Global Firebase service instance
firebase_service = FirebaseService()