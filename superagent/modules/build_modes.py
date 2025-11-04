"""
Build Modes Module - Replit Agent Style
Supports:
- Start with Design: Creates clickable prototype in ~3 minutes
- Build Full App: Creates complete functionality in ~10 minutes
"""

import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class BuildModes:
    """
    Build modes for different development approaches
    """
    
    def __init__(self):
        self.modes = {
            'design': {
                'name': 'Start with Design',
                'description': 'Create clickable prototype first',
                'estimated_time': '3 minutes',
                'focus': 'UI/UX and visual design'
            },
            'full': {
                'name': 'Build Full App',
                'description': 'Build complete functionality from start',
                'estimated_time': '10 minutes',
                'focus': 'Full-stack development'
            }
        }
    
    def generate_prototype(self, project_desc: str, project_type: str) -> Dict:
        """
        Generate a clickable prototype (design mode)
        Focuses on UI/UX with placeholder functionality
        """
        try:
            logger.info(f"Generating prototype for {project_type}: {project_desc[:100]}")
            
            # Design-focused prompt
            design_prompt = f"""
            Create a clickable HTML/CSS prototype for: {project_desc}
            
            Requirements:
            - Focus on visual design and user interface
            - Create realistic-looking UI components
            - Add placeholder functionality (buttons, forms, navigation)
            - Use modern, professional styling
            - Make it fully responsive
            - Add comments indicating where functionality will go
            
            Project type: {project_type}
            
            This is a DESIGN PROTOTYPE - prioritize aesthetics and UX over functionality.
            """
            
            return {
                "success": True,
                "mode": "design",
                "prompt": design_prompt,
                "estimated_time": "3 minutes",
                "output_type": "prototype",
                "next_step": "Review the design, then build full functionality"
            }
            
        except Exception as e:
            logger.error(f"Prototype generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_full_app(self, project_desc: str, project_type: str) -> Dict:
        """
        Generate complete application (full mode)
        Focuses on functionality and backend logic
        """
        try:
            logger.info(f"Generating full app for {project_type}: {project_desc[:100]}")
            
            # Full-featured prompt
            full_prompt = f"""
            Create a complete, production-ready application for: {project_desc}
            
            Requirements:
            - Implement all core functionality
            - Add proper error handling
            - Include database/state management if needed
            - Create clean, maintainable code
            - Add security best practices
            - Include comments and documentation
            - Make it deployment-ready
            
            Project type: {project_type}
            
            This is a FULL APPLICATION - prioritize functionality and completeness.
            """
            
            return {
                "success": True,
                "mode": "full",
                "prompt": full_prompt,
                "estimated_time": "10 minutes",
                "output_type": "complete_app",
                "next_step": "Test and deploy the application"
            }
            
        except Exception as e:
            logger.error(f"Full app generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_mode_info(self, mode: str) -> Dict:
        """Get information about a specific build mode"""
        return self.modes.get(mode, {})
    
    def convert_prototype_to_full(self, prototype_code: str, project_desc: str) -> Dict:
        """
        Convert a design prototype into a full application
        Used when user starts with design mode then wants full functionality
        """
        try:
            conversion_prompt = f"""
            Convert this design prototype into a fully functional application:
            
            Original request: {project_desc}
            
            Current prototype code: {prototype_code[:500]}...
            
            Requirements:
            - Keep the existing design and UI
            - Add complete backend functionality
            - Implement data persistence
            - Add error handling and validation
            - Make all interactive elements functional
            - Add any necessary API integrations
            """
            
            return {
                "success": True,
                "prompt": conversion_prompt,
                "mode": "conversion",
                "message": "Converting prototype to full application"
            }
            
        except Exception as e:
            logger.error(f"Prototype conversion failed: {e}")
            return {"success": False, "error": str(e)}


# Global instance
build_modes_instance = BuildModes()


def get_build_strategy(mode: str, project_desc: str, project_type: str) -> Dict:
    """
    Get the build strategy based on selected mode
    
    Args:
        mode: 'design' or 'full'
        project_desc: Project description
        project_type: Type of project (webapp, api, etc.)
    
    Returns:
        Build strategy with prompts and configuration
    """
    if mode == 'design':
        return build_modes_instance.generate_prototype(project_desc, project_type)
    elif mode == 'full':
        return build_modes_instance.generate_full_app(project_desc, project_type)
    else:
        return {"success": False, "error": f"Unknown mode: {mode}"}
