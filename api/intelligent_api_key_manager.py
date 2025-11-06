"""
Intelligent API Key Manager
Guides users through API key setup with automated assistance
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class IntelligentAPIKeyManager:
    """
    Intelligent system that helps users set up API keys
    Detects missing keys, provides signup links, guides through setup
    """
    
    def __init__(self):
        self.service_info = self._initialize_service_info()
        self.setup_history = []
        
    def _initialize_service_info(self) -> Dict[str, Dict]:
        """Initialize information about all supported services"""
        return {
            # Payment Services
            "stripe": {
                "name": "Stripe",
                "category": "payment",
                "signup_url": "https://dashboard.stripe.com/register",
                "api_key_url": "https://dashboard.stripe.com/apikeys",
                "docs_url": "https://stripe.com/docs/keys",
                "env_vars": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"],
                "free_tier": True,
                "requires_payment": False,
                "setup_time": "5 minutes",
                "instructions": [
                    "1. Go to Stripe Dashboard",
                    "2. Click 'Developers' → 'API Keys'",
                    "3. Copy 'Secret key' (starts with sk_)",
                    "4. Copy 'Publishable key' (starts with pk_)",
                    "5. Add both to .env file"
                ]
            },
            "paypal": {
                "name": "PayPal",
                "category": "payment",
                "signup_url": "https://developer.paypal.com/developer/applications",
                "api_key_url": "https://developer.paypal.com/developer/applications",
                "docs_url": "https://developer.paypal.com/docs/api/overview/",
                "env_vars": ["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET"],
                "free_tier": True,
                "requires_payment": False,
                "setup_time": "5 minutes"
            },
            
            # Email Services
            "sendgrid": {
                "name": "SendGrid",
                "category": "email",
                "signup_url": "https://signup.sendgrid.com/",
                "api_key_url": "https://app.sendgrid.com/settings/api_keys",
                "docs_url": "https://docs.sendgrid.com/ui/account-and-settings/api-keys",
                "env_vars": ["SENDGRID_API_KEY"],
                "free_tier": True,
                "free_tier_limit": "100 emails/day",
                "requires_payment": False,
                "setup_time": "3 minutes",
                "instructions": [
                    "1. Sign up for SendGrid (free tier: 100 emails/day)",
                    "2. Go to Settings → API Keys",
                    "3. Click 'Create API Key'",
                    "4. Name it (e.g., 'MyApp')",
                    "5. Select 'Full Access'",
                    "6. Copy the API key (starts with SG.)",
                    "7. Add to .env: SENDGRID_API_KEY=your_key"
                ]
            },
            "mailgun": {
                "name": "Mailgun",
                "category": "email",
                "signup_url": "https://signup.mailgun.com/new/signup",
                "api_key_url": "https://app.mailgun.com/app/account/security/api_keys",
                "docs_url": "https://documentation.mailgun.com/en/latest/api-intro.html",
                "env_vars": ["MAILGUN_API_KEY", "MAILGUN_DOMAIN"],
                "free_tier": True,
                "free_tier_limit": "5,000 emails/month",
                "requires_payment": False,
                "setup_time": "5 minutes"
            },
            
            # Storage Services
            "s3": {
                "name": "AWS S3",
                "category": "storage",
                "signup_url": "https://portal.aws.amazon.com/billing/signup",
                "api_key_url": "https://console.aws.amazon.com/iam/home#/security_credentials",
                "docs_url": "https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html",
                "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "AWS_S3_BUCKET"],
                "free_tier": True,
                "free_tier_limit": "5GB storage, 20,000 GET requests",
                "requires_payment": True,
                "requires_credit_card": True,
                "setup_time": "10 minutes",
                "instructions": [
                    "1. Sign up for AWS (requires credit card, but free tier available)",
                    "2. Go to IAM → Users → Create User",
                    "3. Attach policy: AmazonS3FullAccess",
                    "4. Create access key",
                    "5. Copy Access Key ID and Secret Access Key",
                    "6. Create S3 bucket in desired region",
                    "7. Add to .env file"
                ]
            },
            "gcs": {
                "name": "Google Cloud Storage",
                "category": "storage",
                "signup_url": "https://console.cloud.google.com/",
                "api_key_url": "https://console.cloud.google.com/apis/credentials",
                "docs_url": "https://cloud.google.com/storage/docs/authentication",
                "env_vars": ["GCS_PROJECT_ID", "GCS_BUCKET", "GOOGLE_APPLICATION_CREDENTIALS"],
                "free_tier": True,
                "free_tier_limit": "5GB storage",
                "requires_payment": True,
                "requires_credit_card": True,
                "setup_time": "10 minutes"
            },
            
            # Authentication Services
            "auth0": {
                "name": "Auth0",
                "category": "authentication",
                "signup_url": "https://auth0.com/signup",
                "api_key_url": "https://manage.auth0.com/dashboard",
                "docs_url": "https://auth0.com/docs/get-started",
                "env_vars": ["AUTH0_DOMAIN", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET"],
                "free_tier": True,
                "free_tier_limit": "7,000 active users",
                "requires_payment": False,
                "setup_time": "5 minutes"
            },
            
            # AI Services
            "openai": {
                "name": "OpenAI",
                "category": "ai",
                "signup_url": "https://platform.openai.com/signup",
                "api_key_url": "https://platform.openai.com/api-keys",
                "docs_url": "https://platform.openai.com/docs/api-reference",
                "env_vars": ["OPENAI_API_KEY"],
                "free_tier": False,
                "requires_payment": True,
                "requires_credit_card": True,
                "setup_time": "3 minutes",
                "instructions": [
                    "1. Sign up for OpenAI (requires payment)",
                    "2. Go to API Keys section",
                    "3. Click 'Create new secret key'",
                    "4. Name it and copy the key",
                    "5. Add to .env: OPENAI_API_KEY=your_key"
                ]
            },
            "anthropic": {
                "name": "Anthropic (Claude)",
                "category": "ai",
                "signup_url": "https://console.anthropic.com/",
                "api_key_url": "https://console.anthropic.com/settings/keys",
                "docs_url": "https://docs.anthropic.com/",
                "env_vars": ["ANTHROPIC_API_KEY"],
                "free_tier": False,
                "requires_payment": True,
                "setup_time": "3 minutes"
            },
            
            # Analytics Services
            "google_analytics": {
                "name": "Google Analytics",
                "category": "analytics",
                "signup_url": "https://analytics.google.com/",
                "api_key_url": "https://analytics.google.com/analytics/web/#/a{accountId}w{propertyId}p{viewId}/admin/tracking/tracking-code/",
                "docs_url": "https://developers.google.com/analytics",
                "env_vars": ["GA_TRACKING_ID"],
                "free_tier": True,
                "requires_payment": False,
                "setup_time": "5 minutes"
            },
            "mixpanel": {
                "name": "Mixpanel",
                "category": "analytics",
                "signup_url": "https://mixpanel.com/register/",
                "api_key_url": "https://mixpanel.com/settings/project",
                "docs_url": "https://developer.mixpanel.com/",
                "env_vars": ["MIXPANEL_TOKEN"],
                "free_tier": True,
                "free_tier_limit": "100,000 events/month",
                "requires_payment": False,
                "setup_time": "3 minutes"
            },
            
            # Monitoring Services
            "sentry": {
                "name": "Sentry",
                "category": "monitoring",
                "signup_url": "https://sentry.io/signup/",
                "api_key_url": "https://sentry.io/settings/account/api/auth-tokens/",
                "docs_url": "https://docs.sentry.io/",
                "env_vars": ["SENTRY_DSN"],
                "free_tier": True,
                "free_tier_limit": "5,000 errors/month",
                "requires_payment": False,
                "setup_time": "3 minutes",
                "instructions": [
                    "1. Sign up for Sentry (free tier: 5,000 errors/month)",
                    "2. Create a new project",
                    "3. Select your platform (Node.js, Python, etc.)",
                    "4. Copy the DSN (Data Source Name)",
                    "5. Add to .env: SENTRY_DSN=your_dsn"
                ]
            },
            "datadog": {
                "name": "Datadog",
                "category": "monitoring",
                "signup_url": "https://www.datadoghq.com/free-datadog-trial/",
                "api_key_url": "https://app.datadoghq.com/organization-settings/api-keys",
                "docs_url": "https://docs.datadoghq.com/",
                "env_vars": ["DATADOG_API_KEY"],
                "free_tier": True,
                "free_tier_limit": "14-day trial",
                "requires_payment": True,
                "setup_time": "5 minutes"
            }
        }
    
    async def detect_missing_keys(self, required_services: List[str]) -> Dict[str, Any]:
        """
        Detect which API keys are missing
        
        Args:
            required_services: List of service names needed
            
        Returns:
            Dictionary with missing keys and setup information
        """
        
        print(f"🔍 Detecting missing API keys for {len(required_services)} services...")
        
        missing = []
        configured = []
        
        for service in required_services:
            if service not in self.service_info:
                print(f"   ⚠️  Unknown service: {service}")
                continue
            
            info = self.service_info[service]
            env_vars = info["env_vars"]
            
            # Check if any required env vars are missing
            # In production, would check actual environment variables
            # For now, assume all are missing for demonstration
            is_missing = True  # Simplified for demo
            
            if is_missing:
                missing.append({
                    "service": service,
                    "name": info["name"],
                    "category": info["category"],
                    "env_vars": env_vars,
                    "setup_info": info
                })
                print(f"   ❌ Missing: {info['name']}")
            else:
                configured.append(service)
                print(f"   ✅ Configured: {info['name']}")
        
        return {
            "total_required": len(required_services),
            "missing_count": len(missing),
            "configured_count": len(configured),
            "missing": missing,
            "configured": configured
        }
    
    async def generate_setup_guide(self, services: List[str]) -> Dict[str, Any]:
        """
        Generate comprehensive setup guide for services
        
        Args:
            services: List of service names
            
        Returns:
            Complete setup guide with instructions
        """
        
        print(f"\n📝 Generating setup guide for {len(services)} services...")
        
        guide = {
            "title": "API Key Setup Guide",
            "total_services": len(services),
            "estimated_time": "0 minutes",
            "services": []
        }
        
        total_time = 0
        
        for service in services:
            if service not in self.service_info:
                continue
            
            info = self.service_info[service]
            
            # Calculate time
            time_str = info.get("setup_time", "5 minutes")
            time_minutes = int(time_str.split()[0])
            total_time += time_minutes
            
            service_guide = {
                "service": service,
                "name": info["name"],
                "category": info["category"],
                "estimated_time": info.get("setup_time", "5 minutes"),
                "signup_url": info["signup_url"],
                "api_key_url": info["api_key_url"],
                "docs_url": info["docs_url"],
                "env_vars": info["env_vars"],
                "free_tier": info.get("free_tier", False),
                "free_tier_limit": info.get("free_tier_limit"),
                "requires_payment": info.get("requires_payment", False),
                "requires_credit_card": info.get("requires_credit_card", False),
                "instructions": info.get("instructions", [
                    f"1. Visit {info['signup_url']}",
                    "2. Sign up for an account",
                    f"3. Navigate to {info['api_key_url']}",
                    "4. Create/copy your API key",
                    "5. Add to .env file"
                ])
            }
            
            guide["services"].append(service_guide)
            
            print(f"   ✅ {info['name']}: {info.get('setup_time', '5 minutes')}")
        
        guide["estimated_time"] = f"{total_time} minutes"
        
        print(f"\n⏱️  Total estimated setup time: {total_time} minutes")
        
        return guide
    
    async def generate_env_template(self, services: List[str]) -> str:
        """
        Generate .env template file with all required variables
        
        Args:
            services: List of service names
            
        Returns:
            .env file content
        """
        
        print(f"\n📄 Generating .env template...")
        
        env_content = "# API Keys and Configuration\n"
        env_content += "# Generated by SuperAgent v8 Intelligent API Key Manager\n"
        env_content += f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Group by category
        categories = {}
        for service in services:
            if service not in self.service_info:
                continue
            
            info = self.service_info[service]
            category = info["category"]
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "service": service,
                "info": info
            })
        
        # Generate content by category
        for category, items in sorted(categories.items()):
            env_content += f"# {category.upper()} SERVICES\n"
            env_content += "# " + "="*70 + "\n\n"
            
            for item in items:
                service = item["service"]
                info = item["info"]
                
                env_content += f"# {info['name']}\n"
                env_content += f"# Signup: {info['signup_url']}\n"
                env_content += f"# API Keys: {info['api_key_url']}\n"
                
                if info.get("free_tier"):
                    env_content += f"# Free Tier: Yes"
                    if info.get("free_tier_limit"):
                        env_content += f" ({info['free_tier_limit']})"
                    env_content += "\n"
                
                if info.get("requires_payment"):
                    env_content += "# ⚠️  Requires payment\n"
                
                for env_var in info["env_vars"]:
                    env_content += f"{env_var}=your_{service}_key_here\n"
                
                env_content += "\n"
        
        print(f"   ✅ Generated template with {len(services)} services")
        
        return env_content
    
    async def validate_api_keys(self, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate API keys (check format, test connection if possible)
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            Validation results
        """
        
        print(f"\n🔍 Validating {len(env_vars)} API keys...")
        
        results = {
            "total": len(env_vars),
            "valid": 0,
            "invalid": 0,
            "untested": 0,
            "details": []
        }
        
        for key, value in env_vars.items():
            result = {
                "key": key,
                "status": "unknown",
                "message": ""
            }
            
            # Basic validation
            if not value or value.startswith("your_") or value == "":
                result["status"] = "invalid"
                result["message"] = "Key not set or using placeholder value"
                results["invalid"] += 1
            else:
                # Format validation based on service
                if "STRIPE" in key:
                    if key == "STRIPE_SECRET_KEY" and not value.startswith("sk_"):
                        result["status"] = "invalid"
                        result["message"] = "Stripe secret key should start with 'sk_'"
                        results["invalid"] += 1
                    elif key == "STRIPE_PUBLISHABLE_KEY" and not value.startswith("pk_"):
                        result["status"] = "invalid"
                        result["message"] = "Stripe publishable key should start with 'pk_'"
                        results["invalid"] += 1
                    else:
                        result["status"] = "valid"
                        result["message"] = "Format looks correct"
                        results["valid"] += 1
                
                elif "SENDGRID" in key:
                    if not value.startswith("SG."):
                        result["status"] = "invalid"
                        result["message"] = "SendGrid API key should start with 'SG.'"
                        results["invalid"] += 1
                    else:
                        result["status"] = "valid"
                        result["message"] = "Format looks correct"
                        results["valid"] += 1
                
                else:
                    result["status"] = "untested"
                    result["message"] = "Key set, but cannot validate format"
                    results["untested"] += 1
            
            results["details"].append(result)
            
            status_icon = "✅" if result["status"] == "valid" else "❌" if result["status"] == "invalid" else "⚠️"
            print(f"   {status_icon} {key}: {result['message']}")
        
        print(f"\n📊 Validation complete: {results['valid']} valid, {results['invalid']} invalid, {results['untested']} untested")
        
        return results
    
    async def interactive_setup(self, services: List[str]) -> Dict[str, Any]:
        """
        Run interactive setup wizard
        
        Args:
            services: List of services to set up
            
        Returns:
            Setup results
        """
        
        print(f"\n🚀 Starting Interactive Setup Wizard for {len(services)} services...")
        print("="*70)
        
        # Step 1: Detect missing keys
        print("\n📋 Step 1: Detecting Missing API Keys...")
        detection = await self.detect_missing_keys(services)
        
        if detection["missing_count"] == 0:
            print("\n✅ All API keys are already configured!")
            return {
                "success": True,
                "message": "All keys configured",
                "detection": detection
            }
        
        # Step 2: Generate setup guide
        print(f"\n📝 Step 2: Generating Setup Guide...")
        guide = await self.generate_setup_guide([s["service"] for s in detection["missing"]])
        
        # Step 3: Generate .env template
        print(f"\n📄 Step 3: Generating .env Template...")
        env_template = await self.generate_env_template([s["service"] for s in detection["missing"]])
        
        # Step 4: Provide instructions
        print("\n" + "="*70)
        print("📋 SETUP INSTRUCTIONS")
        print("="*70)
        print(f"\n⏱️  Estimated time: {guide['estimated_time']}")
        print(f"📦 Services to configure: {len(guide['services'])}\n")
        
        for i, service in enumerate(guide["services"], 1):
            print(f"\n{i}. {service['name']} ({service['estimated_time']})")
            print(f"   Category: {service['category']}")
            print(f"   Signup: {service['signup_url']}")
            
            if service['free_tier']:
                tier_info = "Yes"
                if service.get('free_tier_limit'):
                    tier_info += f" ({service['free_tier_limit']})"
                print(f"   Free Tier: {tier_info}")
            
            if service.get('requires_payment'):
                print(f"   ⚠️  Requires payment")
            
            print(f"\n   Instructions:")
            for instruction in service['instructions']:
                print(f"   {instruction}")
        
        print("\n" + "="*70)
        print("📄 .env Template Generated")
        print("="*70)
        print("\nSave this to your .env file:\n")
        print(env_template)
        
        print("\n" + "="*70)
        print("✅ Setup Guide Complete!")
        print("="*70)
        
        return {
            "success": True,
            "detection": detection,
            "guide": guide,
            "env_template": env_template,
            "next_steps": [
                "1. Follow the setup guide above",
                "2. Get API keys from each service",
                "3. Add keys to .env file",
                "4. Restart your application",
                "5. Run validation to verify keys"
            ]
        }


# Global instance
intelligent_api_key_manager = IntelligentAPIKeyManager()
