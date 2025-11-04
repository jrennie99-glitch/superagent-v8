"""
CLI Interface
Command-line tool for SuperAgent
"""
import sys
import json
from typing import Dict, Optional
import httpx

class CLI:
    """Command-line interface for SuperAgent"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.api_key = None
    
    def set_api_key(self, api_key: str):
        """Set API key for authenticated requests"""
        self.api_key = api_key
    
    async def generate_code(self, instruction: str, language: str = "python") -> Dict:
        """Generate code from CLI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json={"instruction": instruction, "language": language},
                timeout=60.0
            )
            return response.json()
    
    async def build_app(self, instruction: str, language: str = "html") -> Dict:
        """Build complete app from CLI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/build-app",
                json={"instruction": instruction, "language": language},
                timeout=120.0
            )
            return response.json()
    
    async def verify_code(self, code: str, language: str) -> Dict:
        """Verify code from CLI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/verify-code",
                json={"code": code, "language": language, "context": ""},
                timeout=60.0
            )
            return response.json()
    
    async def scan_security(self, code: str, language: str) -> Dict:
        """Scan code for security issues"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/security/scan",
                json={"code": code, "language": language},
                timeout=30.0
            )
            return response.json()
    
    def print_result(self, result: Dict, format: str = "json"):
        """Print result in specified format"""
        if format == "json":
            print(json.dumps(result, indent=2))
        elif format == "text":
            if result.get("success"):
                print("✅ Success!")
                if "code" in result:
                    print("\nGenerated Code:")
                    print(result["code"])
                if "message" in result:
                    print(result["message"])
            else:
                print("❌ Error:", result.get("error", "Unknown error"))
        else:
            print(result)

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python -m api.cli_interface <command> [args]")
        print("\nCommands:")
        print("  generate <instruction>  - Generate code")
        print("  build <instruction>     - Build complete app")
        print("  verify <file>          - Verify code file")
        print("  scan <file>            - Scan for security issues")
        return
    
    command = sys.argv[1]
    cli = CLI()
    
    import asyncio
    
    if command == "generate" and len(sys.argv) > 2:
        instruction = " ".join(sys.argv[2:])
        result = asyncio.run(cli.generate_code(instruction))
        cli.print_result(result, format="text")
    
    elif command == "build" and len(sys.argv) > 2:
        instruction = " ".join(sys.argv[2:])
        result = asyncio.run(cli.build_app(instruction))
        cli.print_result(result, format="text")
    
    elif command == "verify" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            language = file_path.split('.')[-1]
            result = asyncio.run(cli.verify_code(code, language))
            cli.print_result(result, format="text")
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
    
    elif command == "scan" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            language = file_path.split('.')[-1]
            result = asyncio.run(cli.scan_security(code, language))
            cli.print_result(result, format="text")
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
