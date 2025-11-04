"""
Microservices Architecture Generator
Generates distributed microservices architectures with service mesh and orchestration
"""

import asyncio
from typing import Dict, List, Any, Optional


class MicroservicesGenerator:
    """Generates microservices architectures"""
    
    def __init__(self):
        self.service_templates = {
            "api-gateway": "API Gateway",
            "auth": "Authentication Service",
            "user": "User Service",
            "product": "Product Service",
            "order": "Order Service",
            "payment": "Payment Service",
            "notification": "Notification Service",
        }
    
    async def generate_microservices_architecture(
        self,
        services: List[str],
        communication: str = "grpc",
        service_mesh: str = "istio",
        orchestration: str = "kubernetes"
    ) -> Dict[str, Any]:
        """
        Generate microservices architecture
        
        Args:
            services: List of services to generate
            communication: Inter-service communication (grpc, rest, kafka)
            service_mesh: Service mesh (istio, linkerd, consul)
            orchestration: Container orchestration (kubernetes, docker-swarm)
        
        Returns:
            Generated microservices architecture
        """
        
        try:
            print("🏗️ Generating microservices architecture...")
            
            # Generate services
            service_files = {}
            for service in services:
                service_files[service] = await self._generate_service(service, communication)
            
            # Generate API Gateway
            gateway = await self._generate_api_gateway(services, communication)
            
            # Generate service mesh config
            mesh_config = await self._generate_service_mesh_config(services, service_mesh)
            
            # Generate orchestration config
            orchestration_config = await self._generate_orchestration_config(
                services, orchestration
            )
            
            # Generate inter-service communication
            communication_config = await self._generate_communication_config(
                services, communication
            )
            
            result = {
                "success": True,
                "architecture": {
                    "type": "microservices",
                    "services": services,
                    "communication": communication,
                    "service_mesh": service_mesh,
                    "orchestration": orchestration,
                },
                "files": {
                    "services": service_files,
                    "gateway": gateway,
                    "mesh": mesh_config,
                    "orchestration": orchestration_config,
                    "communication": communication_config,
                },
                "summary": {
                    "total_services": len(services),
                    "communication_protocol": communication,
                    "service_mesh": service_mesh,
                    "orchestration_platform": orchestration,
                },
            }
            
            print(f"✅ Microservices architecture generated: {len(services)} services")
            
            return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_service(self, service_name: str, communication: str) -> Dict[str, str]:
        """Generate individual microservice"""
        
        await asyncio.sleep(0.2)
        
        service_code = f"""import express from 'express';
import {{ createClient }} from 'redis';

const app = express();
const redis = createClient();

// Service: {service_name}
app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy', service: '{service_name}' }});
}});

app.listen(3001, () => {{
  console.log('{service_name} service running on port 3001');
}});
"""
        
        return {
            f"{service_name}/main.ts": service_code,
            f"{service_name}/Dockerfile": f"""FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
""",
        }
    
    async def _generate_api_gateway(self, services: List[str], communication: str) -> Dict[str, str]:
        """Generate API Gateway"""
        
        await asyncio.sleep(0.2)
        
        gateway_code = f"""import express from 'express';
import {{ createProxyMiddleware }} from 'express-http-proxy';

const app = express();

// Route to services
"""
        
        for service in services:
            gateway_code += f"""app.use('/{service}', createProxyMiddleware({{
  target: 'http://{service}:3001',
  changeOrigin: true,
}}));
"""
        
        gateway_code += """
app.listen(8000, () => {
  console.log('API Gateway running on port 8000');
});
"""
        
        return {
            "gateway/main.ts": gateway_code,
        }
    
    async def _generate_service_mesh_config(self, services: List[str], mesh: str) -> Dict[str, str]:
        """Generate service mesh configuration"""
        
        await asyncio.sleep(0.2)
        
        if mesh == "istio":
            config = """apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: services
spec:
  hosts:
  - services
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: services
        port:
          number: 3001
"""
        
        else:
            config = f"# Service mesh configuration for {mesh}"
        
        return {
            f"mesh/{mesh}-config.yaml": config,
        }
    
    async def _generate_orchestration_config(self, services: List[str], orchestration: str) -> Dict[str, str]:
        """Generate orchestration configuration"""
        
        await asyncio.sleep(0.2)
        
        if orchestration == "kubernetes":
            config = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservices
spec:
  replicas: 3
  selector:
    matchLabels:
      app: microservices
  template:
    metadata:
      labels:
        app: microservices
    spec:
      containers:
      - name: service
        image: microservice:latest
        ports:
        - containerPort: 3001
        env:
        - name: SERVICE_NAME
          value: microservice
"""
        
        else:
            config = f"# Orchestration configuration for {orchestration}"
        
        return {
            f"orchestration/{orchestration}-deployment.yaml": config,
        }
    
    async def _generate_communication_config(self, services: List[str], communication: str) -> Dict[str, str]:
        """Generate inter-service communication configuration"""
        
        await asyncio.sleep(0.2)
        
        if communication == "grpc":
            config = """syntax = "proto3";

service ServiceRegistry {
  rpc GetService (ServiceRequest) returns (ServiceResponse);
  rpc RegisterService (ServiceRequest) returns (ServiceResponse);
}

message ServiceRequest {
  string service_name = 1;
  string host = 2;
  int32 port = 3;
}

message ServiceResponse {
  bool success = 1;
  string message = 2;
}
"""
        
        elif communication == "kafka":
            config = """apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-config
data:
  bootstrap.servers: kafka:9092
  topics: |
    - service-events
    - user-events
    - order-events
"""
        
        else:
            config = "# REST communication configuration"
        
        return {
            f"communication/{communication}-config": config,
        }


# Global instance
microservices_generator = MicroservicesGenerator()
