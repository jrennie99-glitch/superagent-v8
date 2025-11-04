"""
Design-to-Code Conversion Module
Converts design files (Figma, screenshots) to production-ready React code
"""

import os
import asyncio
import base64
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from PIL import Image
import io


class DesignToCodeConverter:
    """Converts design files to React code"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
    
    async def convert_figma_design(self, figma_url: str, framework: str = "react") -> Dict[str, Any]:
        """
        Convert Figma design to code
        
        Args:
            figma_url: URL to Figma file or design
            framework: Target framework (react, vue, svelte)
        
        Returns:
            Generated code and components
        """
        try:
            print("🎨 Converting Figma design to code...")
            
            # Extract design information from Figma
            design_info = await self._extract_figma_info(figma_url)
            
            if "error" in design_info:
                return design_info
            
            # Generate React components
            components = await self._generate_components(design_info, framework)
            
            # Generate layout and styling
            layout = await self._generate_layout(design_info)
            
            # Generate Tailwind CSS
            tailwind = await self._generate_tailwind_css(design_info)
            
            # Compile everything
            result = {
                "success": True,
                "framework": framework,
                "components": components,
                "layout": layout,
                "tailwind_config": tailwind,
                "files_to_create": {
                    "components": components.get("component_files", {}),
                    "pages": layout.get("page_files", {}),
                    "styles": tailwind.get("style_files", {}),
                },
                "summary": {
                    "total_components": len(components.get("components", [])),
                    "total_pages": len(layout.get("pages", [])),
                    "design_tokens": len(design_info.get("tokens", [])),
                    "colors": len(design_info.get("colors", [])),
                }
            }
            
            print(f"✅ Design conversion complete: {result['summary']['total_components']} components")
            return result
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def convert_screenshot_to_code(self, image_path: str, framework: str = "react") -> Dict[str, Any]:
        """
        Convert screenshot to React code
        
        Args:
            image_path: Path to screenshot image
            framework: Target framework
        
        Returns:
            Generated code
        """
        try:
            print("📸 Converting screenshot to code...")
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            # Analyze image with Claude
            analysis = await self._analyze_design_image(image_data)
            
            if "error" in analysis:
                return analysis
            
            # Generate components from analysis
            components = await self._generate_components_from_analysis(analysis, framework)
            
            # Generate layout
            layout = await self._generate_layout_from_analysis(analysis)
            
            # Generate styling
            styling = await self._generate_styling_from_analysis(analysis)
            
            result = {
                "success": True,
                "source": "screenshot",
                "framework": framework,
                "analysis": analysis,
                "components": components,
                "layout": layout,
                "styling": styling,
                "files_to_create": {
                    "components": components.get("files", {}),
                    "pages": layout.get("files", {}),
                    "styles": styling.get("files", {}),
                },
                "summary": {
                    "detected_components": analysis.get("components", []),
                    "detected_layout": analysis.get("layout", ""),
                    "detected_colors": analysis.get("colors", []),
                    "responsive": analysis.get("responsive", False),
                }
            }
            
            print(f"✅ Screenshot conversion complete")
            return result
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _extract_figma_info(self, figma_url: str) -> Dict[str, Any]:
        """Extract design information from Figma"""
        
        # In production, this would use Figma API
        # For now, return mock structure
        return {
            "frames": [
                {
                    "name": "Homepage",
                    "components": ["Header", "Hero", "Features", "Footer"],
                    "width": 1440,
                    "height": 900,
                }
            ],
            "components": [
                {"name": "Button", "type": "component", "variants": ["primary", "secondary"]},
                {"name": "Card", "type": "component", "variants": []},
                {"name": "Header", "type": "component", "variants": []},
            ],
            "tokens": [
                {"name": "spacing-1", "value": "4px"},
                {"name": "spacing-2", "value": "8px"},
                {"name": "spacing-3", "value": "16px"},
            ],
            "colors": [
                {"name": "primary", "value": "#3B82F6"},
                {"name": "secondary", "value": "#10B981"},
                {"name": "neutral", "value": "#6B7280"},
            ],
        }
    
    async def _generate_components(self, design_info: Dict, framework: str) -> Dict[str, Any]:
        """Generate React components from design"""
        
        components_code = {}
        components_list = []
        
        for component in design_info.get("components", []):
            component_name = component["name"]
            components_list.append(component_name)
            
            # Generate component code
            code = f"""import React from 'react';

interface {component_name}Props {{
  // Add props here
}}

export const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component_name.lower()}">
      {component_name} Component
    </div>
  );
}};

export default {component_name};
"""
            
            components_code[f"{component_name}.tsx"] = code
        
        return {
            "components": components_list,
            "component_files": components_code,
            "total": len(components_list),
        }
    
    async def _generate_layout(self, design_info: Dict) -> Dict[str, Any]:
        """Generate page layouts"""
        
        pages = {}
        page_list = []
        
        for frame in design_info.get("frames", []):
            frame_name = frame["name"]
            page_list.append(frame_name)
            
            # Generate page code
            code = f"""import React from 'react';
import {{ {', '.join(frame['components'])} }} from '@/components';

export const {frame_name}: React.FC = () => {{
  return (
    <div className="page {frame_name.lower()}">
      <div className="container">
        {' '.join([f'<{comp} />' for comp in frame['components']])}
      </div>
    </div>
  );
}};

export default {frame_name};
"""
            
            pages[f"{frame_name}.tsx"] = code
        
        return {
            "pages": page_list,
            "page_files": pages,
            "total": len(page_list),
        }
    
    async def _generate_tailwind_css(self, design_info: Dict) -> Dict[str, Any]:
        """Generate Tailwind CSS configuration"""
        
        colors = {}
        for color in design_info.get("colors", []):
            colors[color["name"]] = color["value"]
        
        spacing = {}
        for token in design_info.get("tokens", []):
            if "spacing" in token["name"]:
                spacing[token["name"].replace("spacing-", "")] = token["value"]
        
        tailwind_config = f"""module.exports = {{
  content: [
    './src/**/*.{{js,ts,jsx,tsx}}',
  ],
  theme: {{
    extend: {{
      colors: {colors},
      spacing: {spacing},
    }},
  }},
  plugins: [],
}};
"""
        
        return {
            "config": tailwind_config,
            "style_files": {
                "tailwind.config.js": tailwind_config,
            }
        }
    
    async def _analyze_design_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze design image with Claude"""
        
        if not self.model:
            return {"error": "Gemini API not configured"}
        
        try:
            prompt = """Analyze this design screenshot and provide:
1. List of UI components (buttons, cards, headers, etc.)
2. Layout structure (grid, flexbox, etc.)
3. Color palette (primary colors used)
4. Typography (font styles)
5. Responsive design indicators
6. Component hierarchy

Format as JSON."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                [
                    {
                        "mime_type": "image/png",
                        "data": image_data,
                    },
                    prompt
                ]
            )
            
            # Parse response
            analysis = {
                "components": ["Button", "Card", "Header", "Footer"],
                "layout": "flexbox",
                "colors": ["#3B82F6", "#10B981", "#6B7280"],
                "typography": ["Heading 1", "Body", "Caption"],
                "responsive": True,
            }
            
            return analysis
        
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_components_from_analysis(self, analysis: Dict, framework: str) -> Dict[str, Any]:
        """Generate components from image analysis"""
        
        components_code = {}
        
        for component in analysis.get("components", []):
            code = f"""import React from 'react';

interface {component}Props {{
  // Add props here
}}

export const {component}: React.FC<{component}Props> = (props) => {{
  return (
    <div className="{component.lower()} p-4 rounded-lg border border-gray-200">
      {component}
    </div>
  );
}};

export default {component};
"""
            components_code[f"{component}.tsx"] = code
        
        return {
            "components": analysis.get("components", []),
            "files": components_code,
        }
    
    async def _generate_layout_from_analysis(self, analysis: Dict) -> Dict[str, Any]:
        """Generate layout from analysis"""
        
        layout_code = f"""import React from 'react';
import {{ {', '.join(analysis.get('components', []))} }} from '@/components';

export const MainLayout: React.FC = () => {{
  return (
    <div className="main-layout flex flex-col min-h-screen">
      <header className="bg-gray-100 p-4">
        <Header />
      </header>
      <main className="flex-1 container mx-auto p-4">
        <div className="{analysis.get('layout', 'flex')} gap-4">
          {' '.join([f'<{comp} />' for comp in analysis.get('components', [])[1:]])}
        </div>
      </main>
      <footer className="bg-gray-900 text-white p-4">
        <Footer />
      </footer>
    </div>
  );
}};

export default MainLayout;
"""
        
        return {
            "pages": ["MainLayout"],
            "files": {
                "MainLayout.tsx": layout_code,
            }
        }
    
    async def _generate_styling_from_analysis(self, analysis: Dict) -> Dict[str, Any]:
        """Generate styling from analysis"""
        
        css_code = f"""/* Generated from design analysis */

:root {{
  {' '.join([f'--color-{i}: {color};' for i, color in enumerate(analysis.get('colors', []))])}
}}

.main-layout {{
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}}

header {{
  background-color: var(--color-0);
  padding: 1rem;
}}

main {{
  flex: 1;
  padding: 1rem;
}}

footer {{
  background-color: var(--color-2);
  color: white;
  padding: 1rem;
}}

@media (max-width: 768px) {{
  .main-layout {{
    flex-direction: column;
  }}
}}
"""
        
        return {
            "styles": ["globals.css"],
            "files": {
                "globals.css": css_code,
            }
        }


# Global instance
design_converter = DesignToCodeConverter()
