"""Healthcare domain-specific configuration and prompts."""

from typing import Dict, List, Any
from enum import Enum


class HealthcareDomain(Enum):
    """Healthcare-specific domains."""
    PSYCHIATRY = "psychiatry"
    GENERAL_PRACTICE = "general_practice"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    PEDIATRICS = "pediatrics"


class HealthcareDomainConfig:
    """Configuration for healthcare domain."""

    # Specialty-specific model selections
    SPECIALTY_MODELS = {
        HealthcareDomain.PSYCHIATRY.value: [
            "gpt-4-turbo",
            "claude-3-opus",
            "mistral-large"
        ],
        HealthcareDomain.GENERAL_PRACTICE.value: [
            "gpt-4-turbo",
            "claude-3-opus",
            "gemini-2-pro"
        ],
        HealthcareDomain.CARDIOLOGY.value: [
            "gpt-4-turbo",
            "claude-3-opus",
            "llama-2-70b"
        ],
    }

    # Required context fields per specialty
    REQUIRED_CONTEXT = {
        HealthcareDomain.PSYCHIATRY.value: [
            "patient_age",
            "symptoms",
            "medication_history",
            "medical_history",
            "comorbidities"
        ],
        HealthcareDomain.GENERAL_PRACTICE.value: [
            "patient_age",
            "symptoms",
            "vital_signs",
            "medical_history"
        ],
    }

    # Compliance and HIPAA settings
    HIPAA_COMPLIANCE = {
        "requires_audit_logging": True,
        "requires_encryption": True,
        "max_retention_days": 2555,  # ~7 years
        "anonymization_required": False,
        "phi_fields": [
            "patient_name",
            "date_of_birth",
            "medical_record_number",
            "phone_number",
            "email"
        ]
    }

    # Multi-tenant configuration for healthcare providers
    TENANT_ROLES = {
        "healthcare_admin": {
            "permissions": ["manage_users", "view_analytics", "manage_domain_config"],
            "can_access_all_patients": False,
            "rate_limit_per_minute": 100
        },
        "clinician": {
            "permissions": ["query_council", "view_history"],
            "can_access_all_patients": False,
            "rate_limit_per_minute": 30
        },
        "researcher": {
            "permissions": ["query_council", "view_aggregated_analytics"],
            "can_access_all_patients": False,
            "rate_limit_per_minute": 50
        },
        "admin": {
            "permissions": ["*"],
            "can_access_all_patients": True,
            "rate_limit_per_minute": 1000
        }
    }

    # Clinical decision support guidelines
    CLINICAL_GUIDELINES = {
        HealthcareDomain.PSYCHIATRY.value: {
            "evidence_base": "DSM-5, ICD-11, NICE Guidelines",
            "treatment_modalities": ["psychotherapy", "pharmacotherapy", "combination"],
            "safety_considerations": [
                "suicidal ideation assessment",
                "substance_abuse_screening",
                "medication_interactions",
                "contraindications"
            ]
        }
    }

    @staticmethod
    def get_models_for_specialty(specialty: str) -> List[str]:
        """Get recommended models for a medical specialty."""
        return HealthcareDomainConfig.SPECIALTY_MODELS.get(
            specialty,
            ["gpt-4-turbo", "claude-3-opus"]
        )

    @staticmethod
    def get_required_context(specialty: str) -> List[str]:
        """Get required context fields for a specialty."""
        return HealthcareDomainConfig.REQUIRED_CONTEXT.get(specialty, [])

    @staticmethod
    def get_role_config(role: str) -> Dict[str, Any]:
        """Get role-based access control configuration."""
        return HealthcareDomainConfig.TENANT_ROLES.get(role, {})

    @staticmethod
    def validate_phi_sensitivity(context: Dict[str, Any]) -> Dict[str, bool]:
        """Validate if context contains sensitive PHI."""
        phi_fields = HealthcareDomainConfig.HIPAA_COMPLIANCE["phi_fields"]
        return {field: field in context for field in phi_fields}

    @staticmethod
    def get_clinical_guidelines(specialty: str) -> Dict[str, Any]:
        """Get clinical guidelines for a specialty."""
        return HealthcareDomainConfig.CLINICAL_GUIDELINES.get(specialty, {})


# Multi-tenant healthcare provider configuration
class TenantHealthcareConfig:
    """Tenant-specific healthcare configuration."""

    def __init__(self, tenant_id: str, organization_name: str, specialty: str):
        self.tenant_id = tenant_id
        self.organization_name = organization_name
        self.specialty = specialty
        self.models = HealthcareDomainConfig.get_models_for_specialty(specialty)
        self.required_context = HealthcareDomainConfig.get_required_context(specialty)
        self.guidelines = HealthcareDomainConfig.get_clinical_guidelines(specialty)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for storage."""
        return {
            "tenant_id": self.tenant_id,
            "organization_name": self.organization_name,
            "specialty": self.specialty,
            "models": self.models,
            "required_context": self.required_context,
            "guidelines": self.guidelines,
            "hipaa_compliance": HealthcareDomainConfig.HIPAA_COMPLIANCE
        }