"""
VS Code Extension Generator
Generates VS Code extensions for SuperAgent integration
"""

import asyncio
from typing import Dict, List, Any, Optional


class VSCodeExtensionGenerator:
    """Generates VS Code extensions"""
    
    def __init__(self):
        self.extension_types = ["command", "language", "debugger", "theme", "snippet"]
    
    async def generate_vscode_extension(
        self,
        extension_name: str,
        extension_type: str,
        features: List[str],
        commands: List[str]
    ) -> Dict[str, Any]:
        """
        Generate VS Code extension
        
        Args:
            extension_name: Extension name
            extension_type: Type of extension
            features: List of features
            commands: List of commands
        
        Returns:
            Generated extension files
        """
        
        try:
            print(f"🔌 Generating VS Code extension: {extension_name}...")
            
            # Generate package.json
            package_json = await self._generate_package_json(extension_name, commands)
            
            # Generate extension.ts
            extension_ts = await self._generate_extension(extension_name, commands)
            
            # Generate commands
            commands_code = await self._generate_commands(commands)
            
            # Generate UI components
            ui_components = await self._generate_ui_components(features)
            
            # Generate settings
            settings = await self._generate_settings()
            
            result = {
                "success": True,
                "extension_name": extension_name,
                "type": extension_type,
                "files": {
                    "package.json": package_json,
                    "src/extension.ts": extension_ts,
                    "src/commands": commands_code,
                    "src/ui": ui_components,
                    "package-lock.json": settings,
                },
                "commands": len(commands),
                "features": len(features),
            }
            
            print(f"✅ VS Code extension generated: {len(commands)} commands")
            
            return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_package_json(self, extension_name: str, commands: List[str]) -> str:
        """Generate package.json"""
        
        await asyncio.sleep(0.2)
        
        commands_config = ""
        for cmd in commands:
            commands_config += f"""    {{
      "command": "superagent.{cmd}",
      "title": "{cmd.replace('_', ' ').title()}"
    }},
"""
        
        package_json = f"""{{
  "name": "{extension_name.lower()}",
  "displayName": "{extension_name}",
  "description": "SuperAgent integration for VS Code",
  "version": "1.0.0",
  "publisher": "superagent",
  "engines": {{
    "vscode": "^1.70.0"
  }},
  "categories": ["Other"],
  "activationEvents": ["onStartupFinished"],
  "main": "./dist/extension.js",
  "contributes": {{
    "commands": [
{commands_config}    ]
  }},
  "scripts": {{
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "lint": "eslint src"
  }},
  "devDependencies": {{
    "@types/vscode": "^1.70.0",
    "@types/node": "^18.0.0",
    "typescript": "^4.7.0",
    "eslint": "^8.0.0"
  }}
}}
"""
        
        return package_json
    
    async def _generate_extension(self, extension_name: str, commands: List[str]) -> str:
        """Generate extension.ts"""
        
        await asyncio.sleep(0.2)
        
        commands_registration = ""
        for cmd in commands:
            commands_registration += f"""  let {cmd}Command = vscode.commands.registerCommand('superagent.{cmd}', () => {{
    vscode.window.showInformationMessage('{cmd.replace('_', ' ').title()} executed');
  }});
  context.subscriptions.push({cmd}Command);
"""
        
        extension_code = f"""import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {{
  console.log('{extension_name} is now active!');

{commands_registration}
}}

export function deactivate() {{}}
"""
        
        return extension_code
    
    async def _generate_commands(self, commands: List[str]) -> Dict[str, str]:
        """Generate command files"""
        
        await asyncio.sleep(0.2)
        
        commands_code = {}
        
        for cmd in commands:
            cmd_file = f"""import * as vscode from 'vscode';

export async function {cmd}() {{
  try {{
    // Implement {cmd} command
    vscode.window.showInformationMessage('{cmd} command executed');
  }} catch (error) {{
    vscode.window.showErrorMessage(`Error: ${{error}}`);
  }}
}}
"""
            commands_code[f"{cmd}.ts"] = cmd_file
        
        return commands_code
    
    async def _generate_ui_components(self, features: List[str]) -> Dict[str, str]:
        """Generate UI components"""
        
        await asyncio.sleep(0.2)
        
        ui_components = {}
        
        for feature in features:
            component_code = f"""import * as vscode from 'vscode';

export class {feature.capitalize()}Panel {{
  public static currentPanel: {feature.capitalize()}Panel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;

  public static createOrShow(extensionUri: vscode.Uri) {{
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if ({feature.capitalize()}Panel.currentPanel) {{
      {feature.capitalize()}Panel.currentPanel._panel.reveal(column);
      return;
    }}

    const panel = vscode.window.createWebviewPanel(
      '{feature}',
      '{feature.capitalize()}',
      column || vscode.ViewColumn.One,
      {{ enableScripts: true }}
    );

    {feature.capitalize()}Panel.currentPanel = new {feature.capitalize()}Panel(panel, extensionUri);
  }}

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {{
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._update();
  }}

  private _update() {{
    this._panel.webview.html = this._getHtmlForWebview(this._panel.webview);
  }}

  private _getHtmlForWebview(webview: vscode.Webview) {{
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <title>{feature.capitalize()}</title>
        </head>
        <body>
          <h1>{feature.capitalize()} Panel</h1>
        </body>
      </html>
    `;
  }}
}}
"""
            ui_components[f"{feature}_panel.ts"] = component_code
        
        return ui_components
    
    async def _generate_settings(self) -> str:
        """Generate settings"""
        
        await asyncio.sleep(0.2)
        
        settings = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
"""
        
        return settings


# Global instance
vscode_generator = VSCodeExtensionGenerator()
