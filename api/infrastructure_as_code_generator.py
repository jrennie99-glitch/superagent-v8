"""
Infrastructure as Code Generator
Generates Terraform, CloudFormation, and Pulumi configurations
"""

import asyncio
from typing import Dict, List, Any, Optional


class InfrastructureAsCodeGenerator:
    """Generates Infrastructure as Code"""
    
    def __init__(self):
        self.supported_providers = ["aws", "gcp", "azure", "digitalocean"]
        self.supported_iac_tools = ["terraform", "cloudformation", "pulumi", "cdk"]
    
    async def generate_infrastructure(
        self,
        provider: str,
        iac_tool: str,
        resources: List[str],
        region: str = "us-east-1"
    ) -> Dict[str, Any]:
        """
        Generate Infrastructure as Code
        
        Args:
            provider: Cloud provider (aws, gcp, azure, digitalocean)
            iac_tool: IaC tool (terraform, cloudformation, pulumi, cdk)
            resources: List of resources to create
            region: Cloud region
        
        Returns:
            Generated IaC files
        """
        
        try:
            print(f"🏗️ Generating {iac_tool} infrastructure for {provider}...")
            
            # Generate main configuration
            main_config = await self._generate_main_config(provider, iac_tool, region)
            
            # Generate resources
            resource_configs = {}
            for resource in resources:
                resource_configs[resource] = await self._generate_resource(
                    provider, iac_tool, resource
                )
            
            # Generate variables
            variables = await self._generate_variables(provider, iac_tool)
            
            # Generate outputs
            outputs = await self._generate_outputs(provider, iac_tool, resources)
            
            # Generate backend configuration
            backend = await self._generate_backend(provider, iac_tool)
            
            result = {
                "success": True,
                "provider": provider,
                "iac_tool": iac_tool,
                "region": region,
                "files": {
                    "main": main_config,
                    "resources": resource_configs,
                    "variables": variables,
                    "outputs": outputs,
                    "backend": backend,
                },
                "resources_count": len(resources),
            }
            
            print(f"✅ Infrastructure generated: {len(resources)} resources")
            
            return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_main_config(self, provider: str, iac_tool: str, region: str) -> str:
        """Generate main configuration"""
        
        await asyncio.sleep(0.2)
        
        if iac_tool == "terraform":
            config = f"""terraform {{
  required_version = ">= 1.0"
  required_providers {{
    {provider} = {{
      source  = "hashicorp/{provider}"
      version = "~> 5.0"
    }}
  }}
}}

provider "{provider}" {{
  region = "{region}"
}}
"""
        
        elif iac_tool == "cloudformation":
            config = f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'Infrastructure template for {provider}'

Parameters:
  Region:
    Type: String
    Default: {region}
    Description: AWS Region

Resources:
  # Add resources here
"""
        
        else:
            config = f"# {iac_tool} configuration for {provider}"
        
        return config
    
    async def _generate_resource(self, provider: str, iac_tool: str, resource: str) -> str:
        """Generate resource configuration"""
        
        await asyncio.sleep(0.2)
        
        if iac_tool == "terraform":
            if resource == "compute":
                config = f"""resource "{provider}_instance" "main" {{
  instance_type = "t3.micro"
  
  tags = {{
    Name = "main-instance"
  }}
}}
"""
            
            elif resource == "database":
                config = f"""resource "{provider}_db_instance" "main" {{
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "14"
  instance_class       = "db.t3.micro"
  identifier           = "main-db"
  
  skip_final_snapshot  = true
}}
"""
            
            elif resource == "networking":
                config = f"""resource "{provider}_vpc" "main" {{
  cidr_block = "10.0.0.0/16"
  
  tags = {{
    Name = "main-vpc"
  }}
}}

resource "{provider}_subnet" "main" {{
  vpc_id            = {provider}_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}}
"""
            
            else:
                config = f"# {resource} resource configuration"
        
        else:
            config = f"# {resource} resource for {iac_tool}"
        
        return config
    
    async def _generate_variables(self, provider: str, iac_tool: str) -> str:
        """Generate variables configuration"""
        
        await asyncio.sleep(0.2)
        
        if iac_tool == "terraform":
            config = """variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}
"""
        
        else:
            config = "# Variables configuration"
        
        return config
    
    async def _generate_outputs(self, provider: str, iac_tool: str, resources: List[str]) -> str:
        """Generate outputs configuration"""
        
        await asyncio.sleep(0.2)
        
        if iac_tool == "terraform":
            config = """output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.main.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.main.public_ip
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
}
"""
        
        else:
            config = "# Outputs configuration"
        
        return config
    
    async def _generate_backend(self, provider: str, iac_tool: str) -> str:
        """Generate backend configuration"""
        
        await asyncio.sleep(0.2)
        
        if iac_tool == "terraform":
            config = """terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
"""
        
        else:
            config = "# Backend configuration"
        
        return config


# Global instance
iac_generator = InfrastructureAsCodeGenerator()
