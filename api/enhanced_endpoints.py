"""
Enhanced Endpoints for 100% Production-Ready Code Generation
New API endpoints that use the enhanced builder system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Import the enhanced systems
from api.enhanced_enterprise_builder import enhanced_enterprise_builder
from api.production_validator import production_validator
from api.integration_library import integration_library

router = APIRouter()


class Build100Request(BaseModel):
    """Request for 100% production-ready build"""
    instruction: str
    requirements: Dict[str, Any] = {}
    integrations: List[str] = []
    validate: bool = True


class IntegrationRequest(BaseModel):
    """Request for service integration"""
    service: str
    config: Dict[str, Any] = {}


@router.post("/api/v1/build-100-percent")
async def build_100_percent(request: Build100Request):
    """
    Build 100% production-ready application
    
    This endpoint uses multi-pass generation, automatic QA,
    production validation, and best practices enforcement.
    
    Example:
    ```json
    {
      "instruction": "Create an enterprise CRM system",
      "requirements": {
        "frontend": "React + TypeScript",
        "backend": "Node.js + Express",
        "database": "PostgreSQL",
        "scale": "large"
      },
      "integrations": ["stripe", "sendgrid", "s3"],
      "validate": true
    }
    ```
    """
    
    try:
        # Build with enhanced builder
        result = await enhanced_enterprise_builder.build_100_percent(
            instruction=request.instruction,
            requirements=request.requirements
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Build failed'))
        
        # Add integrations if requested
        if request.integrations:
            integrations = {}
            for service in request.integrations:
                integration = await integration_library.generate_integration(
                    service=service,
                    config=request.requirements
                )
                if integration.get('success'):
                    integrations[service] = integration
            
            result['integrations'] = integrations
        
        # Validate if requested
        if request.validate:
            validation = await production_validator.validate_production_readiness(
                code=result['code'],
                config=request.requirements
            )
            result['validation'] = validation
        
        return {
            "success": True,
            "production_ready": result.get('production_ready', False),
            "quality_score": result.get('quality_score', 0),
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/validate-production")
async def validate_production(code: Dict):
    """
    Validate code for production readiness
    
    Runs comprehensive checks on:
    - Security
    - Performance
    - Testing
    - Documentation
    - Error handling
    - Logging
    - Monitoring
    - Scalability
    - Deployment
    - Code quality
    """
    
    try:
        result = await production_validator.validate_production_readiness(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/add-integration")
async def add_integration(request: IntegrationRequest):
    """
    Add service integration to your application
    
    Supported services:
    - Payment: stripe, paypal, square
    - Email: sendgrid, mailgun, ses
    - SMS: twilio, vonage
    - Storage: s3, gcs, azure_blob
    - Auth: auth0, okta, firebase_auth
    - Analytics: google_analytics, mixpanel, segment
    - Monitoring: sentry, datadog, new_relic
    - AI: openai, anthropic, huggingface
    
    Example:
    ```json
    {
      "service": "stripe",
      "config": {
        "features": ["payments", "subscriptions"]
      }
    }
    ```
    """
    
    try:
        result = await integration_library.generate_integration(
            service=request.service,
            config=request.config
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Integration failed'))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/available-integrations")
async def list_integrations():
    """
    List all available service integrations
    """
    return {
        "integrations": integration_library.integrations,
        "total": len(integration_library.integrations)
    }


@router.get("/api/v1/production-checklist")
async def get_production_checklist():
    """
    Get production readiness checklist
    """
    return {
        "checklist": {
            "security": [
                "SQL injection prevention",
                "XSS protection",
                "CSRF protection",
                "Authentication",
                "Authorization",
                "Input validation",
                "Secure headers",
                "Encryption",
                "Rate limiting",
                "Secrets management"
            ],
            "performance": [
                "Database indexes",
                "Query optimization",
                "Caching (Redis)",
                "Code splitting",
                "Lazy loading",
                "Compression",
                "CDN",
                "Async operations"
            ],
            "testing": [
                "Unit tests",
                "Integration tests",
                "E2E tests",
                "90%+ test coverage",
                "Test documentation",
                "CI integration"
            ],
            "documentation": [
                "README",
                "API documentation",
                "Architecture docs",
                "Deployment guide",
                "User guide",
                "Developer guide",
                "Inline comments",
                "API spec (OpenAPI)"
            ],
            "deployment": [
                "Dockerfile",
                "docker-compose.yml",
                "Kubernetes manifests",
                "CI/CD pipeline",
                "Environment configuration",
                "Secrets management"
            ],
            "monitoring": [
                "Health check endpoint",
                "Metrics collection",
                "Error tracking (Sentry)",
                "APM (Application Performance Monitoring)",
                "Uptime monitoring",
                "Logging framework"
            ]
        },
        "minimum_score": 95,
        "recommended_score": 100
    }
