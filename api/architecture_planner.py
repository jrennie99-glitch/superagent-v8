"""
Enterprise Architecture Planner
Analyzes requirements and designs optimal system architectures for complex applications
"""
import os
import json
from typing import Dict, List, Any, Optional
import google.generativeai as genai


class ArchitecturePlanner:
    """Plans enterprise-grade system architectures"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
        else:
            self.model = None
    
    async def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """Analyze user requirements and extract key information"""
        
        if not self.model:
            return {"error": "AI model not configured"}
        
        prompt = f"""Analyze these application requirements and extract key information:

REQUIREMENTS:
{requirements}

Extract and return JSON with:
{{
    "app_type": "e-commerce|saas|realtime|analytics|microservices|etc",
    "scale": "small|medium|large|enterprise",
    "key_features": ["feature1", "feature2", ...],
    "data_requirements": {{"primary_data": ["entity1", "entity2"], "relationships": ["rel1", "rel2"]}},
    "performance_needs": {{"concurrent_users": number, "data_volume": "small|medium|large", "latency_requirement": "ms"}},
    "integrations": ["payment", "auth", "email", "analytics", ...],
    "compliance": ["gdpr", "hipaa", "pci-dss", ...],
    "deployment": ["cloud", "on-premise", "hybrid"]
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_analysis": text}
        except Exception as e:
            return {"error": str(e)}
    
    async def design_architecture(self, requirements: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Design optimal system architecture based on requirements"""
        
        if not self.model:
            return {"error": "AI model not configured"}
        
        app_type = analysis.get("app_type", "general")
        scale = analysis.get("scale", "medium")
        
        prompt = f"""Design a production-ready system architecture for:

APP TYPE: {app_type}
SCALE: {scale}
REQUIREMENTS: {requirements}

Return a comprehensive architecture design in JSON:
{{
    "architecture_pattern": "monolith|microservices|serverless|hybrid",
    "frontend": {{
        "framework": "react|vue|next.js|svelte",
        "state_management": "redux|zustand|pinia",
        "deployment": "cdn|vercel|netlify",
        "features": ["ssr", "pwa", "offline"]
    }},
    "backend": {{
        "services": [
            {{
                "name": "service_name",
                "framework": "fastapi|express|django|go",
                "responsibilities": ["responsibility1", "responsibility2"],
                "endpoints": ["/api/v1/resource1", "/api/v1/resource2"]
            }}
        ],
        "api_style": "rest|graphql|grpc",
        "authentication": "jwt|oauth2|saml",
        "rate_limiting": true,
        "caching": "redis|memcached"
    }},
    "database": {{
        "primary": "postgresql|mongodb|dynamodb",
        "cache": "redis",
        "search": "elasticsearch",
        "entities": ["entity1", "entity2"],
        "relationships": ["one-to-many", "many-to-many"]
    }},
    "infrastructure": {{
        "container": "docker",
        "orchestration": "kubernetes|docker-compose",
        "cloud": "aws|gcp|azure",
        "cdn": "cloudflare|aws-cloudfront",
        "monitoring": "prometheus|datadog",
        "logging": "elk|cloudwatch"
    }},
    "security": {{
        "encryption": "tls|end-to-end",
        "secrets_management": "vault|aws-secrets",
        "ddos_protection": true,
        "waf": true,
        "compliance": ["gdpr", "hipaa"]
    }},
    "scalability": {{
        "horizontal_scaling": true,
        "load_balancing": "nginx|aws-elb",
        "auto_scaling": true,
        "database_sharding": true
    }},
    "deployment": {{
        "ci_cd": "github-actions|gitlab-ci|jenkins",
        "environments": ["dev", "staging", "production"],
        "blue_green_deployment": true,
        "rollback_strategy": "automatic|manual"
    }}
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_design": text}
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_architecture_diagram(self, architecture: Dict[str, Any]) -> str:
        """Generate Mermaid diagram for the architecture"""
        
        diagram = """graph TB
    Client["🖥️ Client Layer"]
    CDN["📡 CDN<br/>Cloudflare"]
    LB["⚖️ Load Balancer<br/>Nginx"]
    
    subgraph Backend["Backend Services"]
        API["API Gateway<br/>FastAPI"]
        Auth["Auth Service<br/>JWT/OAuth2"]
        Business["Business Logic<br/>Services"]
    end
    
    subgraph Data["Data Layer"]
        DB["Primary DB<br/>PostgreSQL"]
        Cache["Cache<br/>Redis"]
        Search["Search<br/>Elasticsearch"]
    end
    
    subgraph Infrastructure["Infrastructure"]
        Docker["🐳 Docker<br/>Containers"]
        K8s["☸️ Kubernetes<br/>Orchestration"]
        Monitor["📊 Monitoring<br/>Prometheus"]
    end
    
    Client -->|HTTPS| CDN
    CDN -->|Route| LB
    LB -->|Distribute| API
    API -->|Authenticate| Auth
    API -->|Process| Business
    Business -->|Query| DB
    Business -->|Cache| Cache
    Business -->|Search| Search
    Docker -->|Deploy| K8s
    K8s -->|Monitor| Monitor
    
    style Client fill:#e1f5ff
    style Backend fill:#f3e5f5
    style Data fill:#e8f5e9
    style Infrastructure fill:#fff3e0"""
        
        return diagram
    
    async def plan_complete_architecture(self, requirements: str) -> Dict[str, Any]:
        """Complete architecture planning workflow"""
        
        # Step 1: Analyze requirements
        analysis = await self.analyze_requirements(requirements)
        if "error" in analysis:
            return analysis
        
        # Step 2: Design architecture
        architecture = await self.design_architecture(requirements, analysis)
        if "error" in architecture:
            return architecture
        
        # Step 3: Generate diagram
        diagram = await self.generate_architecture_diagram(architecture)
        
        return {
            "success": True,
            "analysis": analysis,
            "architecture": architecture,
            "diagram": diagram,
            "next_steps": [
                "Generate database schema based on entities",
                "Create API specifications",
                "Build backend services",
                "Create frontend components",
                "Set up CI/CD pipeline",
                "Configure monitoring and logging"
            ]
        }


# Global instance
architecture_planner = ArchitecturePlanner()
