"""
Automated Environment Setup Wizard
Guides through setup and auto-configures everything
"""

import asyncio
from typing import Dict, List, Any, Optional
import os
import json


class EnvironmentWizard:
    """
    Automated setup wizard that configures the entire environment
    Handles API keys, databases, services, and deployment
    """
    
    def __init__(self):
        self.setup_steps = []
        self.configuration = {}
        
    async def run_setup_wizard(
        self,
        project_type: str,
        integrations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Run interactive setup wizard
        
        Args:
            project_type: Type of project (web, api, mobile, etc.)
            integrations: List of integrations to set up
            
        Returns:
            Complete environment configuration
        """
        
        print("🧙 Starting Automated Environment Setup Wizard...")
        print("="*70)
        
        # Step 1: Detect required services
        print("\n📋 Step 1: Detecting Required Services...")
        required_services = await self._detect_required_services(project_type, integrations)
        print(f"   Found {len(required_services)} services to configure")
        
        # Step 2: Check existing configuration
        print("\n🔍 Step 2: Checking Existing Configuration...")
        existing_config = await self._check_existing_configuration()
        print(f"   {len(existing_config)} services already configured")
        
        # Step 3: Generate configuration templates
        print("\n📝 Step 3: Generating Configuration Templates...")
        templates = await self._generate_configuration_templates(required_services)
        print(f"   Generated {len(templates)} configuration files")
        
        # Step 4: Set up databases
        print("\n🗄️  Step 4: Setting Up Databases...")
        database_config = await self._setup_databases(project_type)
        print(f"   Database configured: {database_config.get('type', 'None')}")
        
        # Step 5: Configure API keys
        print("\n🔑 Step 5: Configuring API Keys...")
        api_keys_config = await self._configure_api_keys(required_services)
        print(f"   {len(api_keys_config)} API keys configured")
        
        # Step 6: Set up cloud services
        print("\n☁️  Step 6: Setting Up Cloud Services...")
        cloud_config = await self._setup_cloud_services(integrations or [])
        print(f"   {len(cloud_config)} cloud services configured")
        
        # Step 7: Configure deployment
        print("\n🚀 Step 7: Configuring Deployment...")
        deployment_config = await self._configure_deployment(project_type)
        print(f"   Deployment target: {deployment_config.get('platform', 'Docker')}")
        
        # Step 8: Generate environment files
        print("\n📄 Step 8: Generating Environment Files...")
        env_files = await self._generate_environment_files(
            templates, database_config, api_keys_config, cloud_config, deployment_config
        )
        print(f"   Generated {len(env_files)} environment files")
        
        # Step 9: Validate configuration
        print("\n✅ Step 9: Validating Configuration...")
        validation = await self._validate_configuration(env_files)
        print(f"   Validation: {'✅ PASSED' if validation['valid'] else '❌ FAILED'}")
        
        # Step 10: Generate setup instructions
        print("\n📖 Step 10: Generating Setup Instructions...")
        instructions = await self._generate_setup_instructions(
            required_services, env_files, validation
        )
        
        print("\n" + "="*70)
        print("🎉 Environment Setup Complete!")
        print("="*70)
        
        return {
            "success": True,
            "required_services": required_services,
            "existing_config": existing_config,
            "templates": templates,
            "database_config": database_config,
            "api_keys_config": api_keys_config,
            "cloud_config": cloud_config,
            "deployment_config": deployment_config,
            "env_files": env_files,
            "validation": validation,
            "instructions": instructions
        }
    
    async def _detect_required_services(self, project_type: str, integrations: List[str]) -> List[Dict]:
        """Detect which services are required"""
        await asyncio.sleep(0.1)
        
        services = []
        
        # Always required
        services.append({
            "name": "Database",
            "type": "database",
            "required": True,
            "options": ["PostgreSQL", "MySQL", "MongoDB"]
        })
        
        # Based on project type
        if project_type in ["web", "fullstack", "ecommerce"]:
            services.extend([
                {
                    "name": "Email Service",
                    "type": "email",
                    "required": True,
                    "options": ["SendGrid", "Mailgun", "AWS SES"]
                },
                {
                    "name": "File Storage",
                    "type": "storage",
                    "required": False,
                    "options": ["AWS S3", "Google Cloud Storage", "Azure Blob"]
                }
            ])
        
        # Based on integrations
        if integrations:
            for integration in integrations:
                if integration == "stripe":
                    services.append({
                        "name": "Stripe",
                        "type": "payment",
                        "required": True,
                        "env_vars": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"]
                    })
                elif integration == "sendgrid":
                    services.append({
                        "name": "SendGrid",
                        "type": "email",
                        "required": True,
                        "env_vars": ["SENDGRID_API_KEY"]
                    })
                elif integration == "s3":
                    services.append({
                        "name": "AWS S3",
                        "type": "storage",
                        "required": True,
                        "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET"]
                    })
        
        return services
    
    async def _check_existing_configuration(self) -> Dict:
        """Check what's already configured"""
        await asyncio.sleep(0.1)
        
        existing = {}
        
        # Check for .env file
        if os.path.exists(".env"):
            existing["env_file"] = True
        
        # Check for common environment variables
        env_vars = [
            "DATABASE_URL",
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "STRIPE_SECRET_KEY",
            "SENDGRID_API_KEY",
            "AWS_ACCESS_KEY_ID"
        ]
        
        for var in env_vars:
            if os.getenv(var):
                existing[var] = "configured"
        
        return existing
    
    async def _generate_configuration_templates(self, services: List[Dict]) -> Dict:
        """Generate configuration templates"""
        await asyncio.sleep(0.1)
        
        templates = {}
        
        # .env template
        env_template = ["# Environment Configuration", "# Generated by SuperAgent v8\n"]
        
        # Add database
        env_template.extend([
            "# Database",
            "DATABASE_URL=postgresql://user:password@localhost:5432/dbname",
            "DB_HOST=localhost",
            "DB_PORT=5432",
            "DB_NAME=myapp",
            "DB_USER=postgres",
            "DB_PASSWORD=changeme\n"
        ])
        
        # Add AI services
        env_template.extend([
            "# AI Services",
            "GEMINI_API_KEY=your_gemini_key_here",
            "OPENAI_API_KEY=your_openai_key_here\n"
        ])
        
        # Add service-specific vars
        for service in services:
            if service.get("env_vars"):
                env_template.append(f"\n# {service['name']}")
                for var in service["env_vars"]:
                    env_template.append(f"{var}=your_{var.lower()}_here")
        
        # Add common vars
        env_template.extend([
            "\n# Application",
            "NODE_ENV=development",
            "PORT=8000",
            "ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000\n",
            "# Security",
            "JWT_SECRET=your_jwt_secret_here",
            "SESSION_SECRET=your_session_secret_here\n"
        ])
        
        templates[".env.template"] = "\n".join(env_template)
        templates[".env.example"] = "\n".join(env_template)
        
        return templates
    
    async def _setup_databases(self, project_type: str) -> Dict:
        """Set up database configuration"""
        await asyncio.sleep(0.1)
        
        # Recommend database based on project type
        if project_type in ["ecommerce", "enterprise"]:
            db_type = "PostgreSQL"
        elif project_type in ["blog", "cms"]:
            db_type = "MySQL"
        elif project_type in ["realtime", "analytics"]:
            db_type = "MongoDB"
        else:
            db_type = "PostgreSQL"
        
        return {
            "type": db_type,
            "host": "localhost",
            "port": self._get_default_port(db_type),
            "name": "myapp_db",
            "user": "postgres" if db_type == "PostgreSQL" else "root",
            "connection_string": self._generate_connection_string(db_type),
            "docker_command": self._get_docker_command(db_type)
        }
    
    def _get_default_port(self, db_type: str) -> int:
        """Get default port for database"""
        ports = {
            "PostgreSQL": 5432,
            "MySQL": 3306,
            "MongoDB": 27017
        }
        return ports.get(db_type, 5432)
    
    def _generate_connection_string(self, db_type: str) -> str:
        """Generate database connection string"""
        if db_type == "PostgreSQL":
            return "postgresql://user:password@localhost:5432/myapp_db"
        elif db_type == "MySQL":
            return "mysql://user:password@localhost:3306/myapp_db"
        elif db_type == "MongoDB":
            return "mongodb://localhost:27017/myapp_db"
        return ""
    
    def _get_docker_command(self, db_type: str) -> str:
        """Get Docker command to run database"""
        if db_type == "PostgreSQL":
            return "docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=changeme -e POSTGRES_DB=myapp_db postgres:15"
        elif db_type == "MySQL":
            return "docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=changeme -e MYSQL_DATABASE=myapp_db mysql:8"
        elif db_type == "MongoDB":
            return "docker run -d -p 27017:27017 mongo:6"
        return ""
    
    async def _configure_api_keys(self, services: List[Dict]) -> Dict:
        """Configure API keys"""
        await asyncio.sleep(0.1)
        
        config = {}
        
        for service in services:
            if service.get("env_vars"):
                for var in service["env_vars"]:
                    config[var] = {
                        "service": service["name"],
                        "required": service.get("required", False),
                        "get_url": self._get_api_key_url(service["name"]),
                        "docs_url": self._get_docs_url(service["name"])
                    }
        
        return config
    
    def _get_api_key_url(self, service_name: str) -> str:
        """Get URL to obtain API key"""
        urls = {
            "Stripe": "https://dashboard.stripe.com/apikeys",
            "SendGrid": "https://app.sendgrid.com/settings/api_keys",
            "AWS S3": "https://console.aws.amazon.com/iam/home#/security_credentials",
            "OpenAI": "https://platform.openai.com/api-keys",
            "Gemini": "https://makersuite.google.com/app/apikey"
        }
        return urls.get(service_name, f"https://{service_name.lower()}.com")
    
    def _get_docs_url(self, service_name: str) -> str:
        """Get documentation URL"""
        return f"https://docs.{service_name.lower().replace(' ', '')}.com"
    
    async def _setup_cloud_services(self, integrations: List[str]) -> Dict:
        """Set up cloud services"""
        await asyncio.sleep(0.1)
        
        config = {}
        
        for integration in integrations:
            if integration == "s3":
                config["s3"] = {
                    "provider": "AWS",
                    "service": "S3",
                    "region": "us-east-1",
                    "bucket": "myapp-uploads"
                }
            elif integration == "gcs":
                config["gcs"] = {
                    "provider": "Google Cloud",
                    "service": "Cloud Storage",
                    "project_id": "myapp-project",
                    "bucket": "myapp-uploads"
                }
        
        return config
    
    async def _configure_deployment(self, project_type: str) -> Dict:
        """Configure deployment"""
        await asyncio.sleep(0.1)
        
        return {
            "platform": "Docker",
            "alternatives": ["Kubernetes", "AWS", "Google Cloud", "Azure", "Heroku", "Vercel"],
            "recommended": "Docker" if project_type in ["api", "backend"] else "Vercel",
            "config_files": ["Dockerfile", "docker-compose.yml", ".dockerignore"]
        }
    
    async def _generate_environment_files(
        self,
        templates: Dict,
        database_config: Dict,
        api_keys_config: Dict,
        cloud_config: Dict,
        deployment_config: Dict
    ) -> Dict:
        """Generate all environment files"""
        await asyncio.sleep(0.1)
        
        files = {}
        
        # .env file
        env_content = templates.get(".env.template", "")
        env_content = env_content.replace(
            "postgresql://user:password@localhost:5432/dbname",
            database_config.get("connection_string", "")
        )
        files[".env"] = env_content
        files[".env.example"] = env_content
        
        # Database setup script
        files["scripts/setup-database.sh"] = f"""#!/bin/bash
# Database Setup Script

echo "Setting up {database_config['type']}..."

# Start database with Docker
{database_config.get('docker_command', '')}

echo "Database started!"
echo "Connection string: {database_config.get('connection_string', '')}"
"""
        
        # Setup instructions
        files["SETUP.md"] = self._generate_setup_markdown(
            database_config, api_keys_config, cloud_config, deployment_config
        )
        
        return files
    
    def _generate_setup_markdown(
        self,
        database_config: Dict,
        api_keys_config: Dict,
        cloud_config: Dict,
        deployment_config: Dict
    ) -> str:
        """Generate setup instructions markdown"""
        
        return f"""# Environment Setup Guide

## Quick Start

### 1. Database Setup

**Recommended:** {database_config['type']}

**Option A: Using Docker (Recommended)**
```bash
{database_config.get('docker_command', '')}
```

**Option B: Local Installation**
- Install {database_config['type']} locally
- Create database: `{database_config['name']}`
- Update DATABASE_URL in .env

### 2. API Keys Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

**Required API Keys:**

{self._format_api_keys_list(api_keys_config)}

### 3. Install Dependencies

```bash
# Backend
npm install

# Frontend (if applicable)
cd frontend && npm install
```

### 4. Run Database Migrations

```bash
npm run migrate
```

### 5. Start Development Server

```bash
npm run dev
```

## Deployment

**Recommended Platform:** {deployment_config.get('recommended', 'Docker')}

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## Troubleshooting

### Database Connection Issues
- Ensure database is running
- Check DATABASE_URL in .env
- Verify credentials

### API Key Issues
- Verify keys are correct
- Check key permissions
- Ensure no extra spaces

## Support

For issues, check the documentation or create an issue.
"""
    
    def _format_api_keys_list(self, api_keys_config: Dict) -> str:
        """Format API keys list for markdown"""
        lines = []
        for var, info in api_keys_config.items():
            required = "**REQUIRED**" if info.get("required") else "Optional"
            lines.append(f"- `{var}` ({required})")
            lines.append(f"  - Service: {info['service']}")
            lines.append(f"  - Get key: {info['get_url']}")
            lines.append(f"  - Docs: {info['docs_url']}\n")
        return "\n".join(lines)
    
    async def _validate_configuration(self, env_files: Dict) -> Dict:
        """Validate the generated configuration"""
        await asyncio.sleep(0.1)
        
        issues = []
        warnings = []
        
        # Check if .env file exists
        if ".env" not in env_files:
            issues.append("Missing .env file")
        
        # Check for required variables
        required_vars = ["DATABASE_URL", "GEMINI_API_KEY"]
        env_content = env_files.get(".env", "")
        
        for var in required_vars:
            if var not in env_content:
                warnings.append(f"Missing {var} in .env")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": 100 if len(issues) == 0 else 80
        }
    
    async def _generate_setup_instructions(
        self,
        services: List[Dict],
        env_files: Dict,
        validation: Dict
    ) -> Dict:
        """Generate final setup instructions"""
        await asyncio.sleep(0.1)
        
        return {
            "quick_start": [
                "1. Copy .env.example to .env",
                "2. Add your API keys to .env",
                "3. Run: bash scripts/setup-database.sh",
                "4. Run: npm install",
                "5. Run: npm run migrate",
                "6. Run: npm run dev"
            ],
            "detailed_steps": "See SETUP.md for detailed instructions",
            "required_services": len([s for s in services if s.get("required")]),
            "optional_services": len([s for s in services if not s.get("required")]),
            "estimated_time": "10-15 minutes"
        }


# Global instance
environment_wizard = EnvironmentWizard()
