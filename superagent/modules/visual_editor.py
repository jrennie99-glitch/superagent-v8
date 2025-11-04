"""
Visual Editor - Drag-and-Drop UI Editor
Edit UI visually with live code sync
Component-based visual editing
"""

import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class VisualEditor:
    """
    Visual UI editor with drag-and-drop
    Features:
    - Component palette
    - Drag-and-drop interface
    - Live code synchronization
    - CSS styling editor
    - Responsive preview
    """
    
    def __init__(self):
        self.components = self._load_component_library()
        self.current_project = None
    
    def _load_component_library(self) -> Dict:
        """Load available UI components"""
        return {
            "layout": [
                {"type": "container", "name": "Container", "html": "<div class='container'></div>"},
                {"type": "row", "name": "Row", "html": "<div class='row'></div>"},
                {"type": "column", "name": "Column", "html": "<div class='col'></div>"}
            ],
            "components": [
                {"type": "button", "name": "Button", "html": "<button class='btn'>Click me</button>"},
                {"type": "input", "name": "Text Input", "html": "<input type='text' class='input' placeholder='Enter text'>"},
                {"type": "heading", "name": "Heading", "html": "<h1>Heading</h1>"},
                {"type": "paragraph", "name": "Paragraph", "html": "<p>Your text here</p>"},
                {"type": "image", "name": "Image", "html": "<img src='https://via.placeholder.com/300' alt='Image'>"},
                {"type": "card", "name": "Card", "html": "<div class='card'><div class='card-body'><h5>Card Title</h5><p>Card content</p></div></div>"}
            ],
            "forms": [
                {"type": "form", "name": "Form", "html": "<form></form>"},
                {"type": "select", "name": "Dropdown", "html": "<select class='select'><option>Option 1</option></select>"},
                {"type": "checkbox", "name": "Checkbox", "html": "<input type='checkbox'> <label>Check me</label>"},
                {"type": "radio", "name": "Radio", "html": "<input type='radio' name='option'> <label>Option</label>"}
            ]
        }
    
    def create_visual_project(self, project_name: str, framework: str = 'html') -> Dict:
        """
        Create a new visual editing project
        
        Args:
            project_name: Name of the project
            framework: 'html', 'react', 'vue'
        
        Returns:
            Project configuration
        """
        try:
            project = {
                "name": project_name,
                "framework": framework,
                "components": [],
                "styles": {},
                "html": "",
                "css": "",
                "js": ""
            }
            
            self.current_project = project
            
            return {
                "success": True,
                "project": project,
                "editor_url": "/visual-editor",
                "components_library": self.components
            }
            
        except Exception as e:
            logger.error(f"Visual project creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def add_component(self, component_type: str, position: Dict, properties: Dict = None) -> Dict:
        """
        Add a component to the canvas
        
        Args:
            component_type: Type of component
            position: {x, y, width, height}
            properties: Component properties
        
        Returns:
            Updated project
        """
        if not self.current_project:
            return {"success": False, "error": "No project loaded"}
        
        properties = properties or {}
        
        # Find component template
        component_template = None
        for category in self.components.values():
            for comp in category:
                if comp['type'] == component_type:
                    component_template = comp
                    break
        
        if not component_template:
            return {"success": False, "error": f"Component {component_type} not found"}
        
        # Create component instance
        component_instance = {
            "id": f"comp_{len(self.current_project['components']) + 1}",
            "type": component_type,
            "html": component_template['html'],
            "position": position,
            "properties": properties
        }
        
        self.current_project['components'].append(component_instance)
        
        # Regenerate HTML
        self._regenerate_code()
        
        return {
            "success": True,
            "component": component_instance,
            "updated_html": self.current_project['html']
        }
    
    def update_component_style(self, component_id: str, styles: Dict) -> Dict:
        """Update component styles"""
        if not self.current_project:
            return {"success": False, "error": "No project loaded"}
        
        # Find component
        component = None
        for comp in self.current_project['components']:
            if comp['id'] == component_id:
                component = comp
                break
        
        if not component:
            return {"success": False, "error": "Component not found"}
        
        # Update styles
        if 'styles' not in component:
            component['styles'] = {}
        component['styles'].update(styles)
        
        # Regenerate CSS
        self._regenerate_code()
        
        return {
            "success": True,
            "component": component,
            "updated_css": self.current_project['css']
        }
    
    def _regenerate_code(self):
        """Regenerate HTML/CSS from components"""
        if not self.current_project:
            return
        
        # Generate HTML
        html_parts = []
        css_parts = []
        
        for comp in self.current_project['components']:
            # Add HTML
            html_parts.append(comp['html'])
            
            # Add CSS if component has styles
            if 'styles' in comp:
                css_rule = f"#{comp['id']} {{\n"
                for prop, value in comp['styles'].items():
                    css_rule += f"  {prop}: {value};\n"
                css_rule += "}\n"
                css_parts.append(css_rule)
        
        self.current_project['html'] = '\n'.join(html_parts)
        self.current_project['css'] = '\n'.join(css_parts)
    
    def export_project(self) -> Dict:
        """Export project as complete HTML/CSS/JS files"""
        if not self.current_project:
            return {"success": False, "error": "No project loaded"}
        
        # Generate complete HTML file
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.current_project['name']}</title>
    <style>
        {self.current_project['css']}
    </style>
</head>
<body>
    {self.current_project['html']}
    <script>
        {self.current_project['js']}
    </script>
</body>
</html>'''
        
        return {
            "success": True,
            "files": {
                "index.html": html_template,
                "styles.css": self.current_project['css'],
                "script.js": self.current_project['js']
            }
        }
    
    def get_component_library(self) -> Dict:
        """Get the component library"""
        return {
            "success": True,
            "components": self.components
        }


# Global instance
visual_editor_instance = VisualEditor()


def create_visual_project(project_name: str, framework: str = 'html') -> Dict:
    """Create a visual editing project"""
    return visual_editor_instance.create_visual_project(project_name, framework)


def get_components() -> Dict:
    """Get available components for visual editor"""
    return visual_editor_instance.get_component_library()
