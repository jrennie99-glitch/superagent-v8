"""
Plan Analyzer - Replit-style build planning
Analyzes user requirements and creates a detailed plan with time estimates
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import re

router = APIRouter(prefix="/api/v1", tags=["Plan Analyzer"])

class PlanRequest(BaseModel):
    instruction: str

class BuildOption(BaseModel):
    type: str  # 'design' or 'full'
    label: str
    description: str
    time: str

class BuildPlan(BaseModel):
    plan_id: str
    title: str
    description: str
    components: List[str]
    tech_stack: Dict[str, str]
    estimated_time: Dict[str, str]
    options: List[BuildOption]
    complexity: str  # 'simple', 'medium', 'complex'

def analyze_complexity(instruction: str) -> tuple[str, int]:
    """Analyze instruction complexity and return complexity level and score"""
    instruction_lower = instruction.lower()
    
    # Complexity keywords and their scores
    complexity_keywords = {
        # Simple (0-2 points)
        'simple': 0,
        'basic': 0,
        'minimal': 0,
        
        # Low complexity (1-2 points)
        'todo': 1,
        'list': 1,
        'counter': 1,
        'calculator': 1,
        
        # Medium complexity (2-4 points)
        'blog': 2,
        'portfolio': 2,
        'landing page': 2,
        'form': 2,
        'gallery': 2,
        
        # Higher complexity (3-5 points)
        'dashboard': 4,
        'admin': 4,
        'analytics': 4,
        'chart': 3,
        'graph': 3,
        
        # High complexity (4-6 points)
        'ecommerce': 5,
        'e-commerce': 5,
        'shop': 4,
        'store': 4,
        'marketplace': 6,
        
        # Authentication/User features (3-4 points)
        'authentication': 3,
        'auth': 3,
        'login': 3,
        'signup': 3,
        'user': 2,
        'profile': 2,
        
        # Backend features (3-5 points)
        'database': 4,
        'api': 3,
        'backend': 4,
        'server': 4,
        
        # Advanced features (4-6 points)
        'real-time': 5,
        'chat': 4,
        'messaging': 4,
        'notification': 3,
        'payment': 5,
        'stripe': 5,
        
        # AI/ML features (5-7 points)
        'ai': 5,
        'machine learning': 6,
        'recommendation': 5,
        'search': 3,
    }
    
    # Calculate complexity score
    complexity_score = 0
    for keyword, score in complexity_keywords.items():
        if keyword in instruction_lower:
            complexity_score += score
    
    # Count features mentioned (each adds complexity)
    feature_indicators = ['with', 'and', 'including', 'that has', 'featuring']
    feature_count = sum(1 for indicator in feature_indicators if indicator in instruction_lower)
    complexity_score += feature_count
    
    # Determine complexity level
    if complexity_score <= 3:
        complexity = 'simple'
    elif complexity_score <= 8:
        complexity = 'medium'
    else:
        complexity = 'complex'
    
    return complexity, complexity_score

def extract_components(instruction: str, complexity_score: int) -> List[str]:
    """Extract likely components from the instruction"""
    instruction_lower = instruction.lower()
    components = []
    
    # Common component patterns
    component_patterns = {
        'todo': ['Task input field', 'Task list display', 'Add/Delete buttons', 'Mark as complete checkbox'],
        'list': ['List container', 'List items', 'Add/Remove functionality'],
        'blog': ['Article list', 'Article detail view', 'Author info', 'Comments section', 'Search functionality'],
        'portfolio': ['Project showcase', 'About section', 'Skills display', 'Contact form'],
        'dashboard': ['Data visualization', 'Statistics cards', 'Charts/Graphs', 'Navigation sidebar', 'User profile'],
        'ecommerce': ['Product catalog', 'Shopping cart', 'Checkout flow', 'Payment integration', 'Order management'],
        'shop': ['Product grid', 'Product details', 'Add to cart', 'Checkout'],
        'form': ['Input fields', 'Validation', 'Submit button', 'Success/Error messages'],
        'calculator': ['Number input', 'Operation buttons', 'Display screen', 'Clear/Reset'],
        'chat': ['Message list', 'Message input', 'Send button', 'User avatars', 'Timestamp display'],
        'landing': ['Hero section', 'Features section', 'Call-to-action', 'Footer'],
        'auth': ['Login form', 'Signup form', 'Password reset', 'Session management'],
        'gallery': ['Image grid', 'Lightbox viewer', 'Image upload', 'Filtering/Sorting'],
    }
    
    # Find matching patterns
    for keyword, component_list in component_patterns.items():
        if keyword in instruction_lower:
            components.extend(component_list)
            break  # Use first match
    
    # If no specific pattern, generate generic components
    if not components:
        components = [
            'Main application interface',
            'User input controls',
            'Data display area',
            'Interactive elements',
            'Responsive layout'
        ]
    
    # Add common features based on keywords
    if 'dark mode' in instruction_lower or 'theme' in instruction_lower:
        components.append('Dark/Light mode toggle')
    
    if 'search' in instruction_lower:
        components.append('Search functionality')
    
    if 'filter' in instruction_lower:
        components.append('Filtering options')
    
    if 'sort' in instruction_lower:
        components.append('Sorting controls')
    
    if 'responsive' in instruction_lower or 'mobile' in instruction_lower:
        components.append('Mobile-responsive design')
    
    if 'animation' in instruction_lower:
        components.append('Smooth animations')
    
    # Add storage if needed
    if any(word in instruction_lower for word in ['save', 'store', 'persist', 'remember']):
        components.append('Local storage persistence')
    
    return components[:8]  # Limit to 8 components for clarity

def determine_tech_stack(instruction: str, complexity: str) -> Dict[str, str]:
    """Determine appropriate tech stack based on requirements"""
    instruction_lower = instruction.lower()
    
    tech_stack = {
        'frontend': 'HTML5, CSS3, JavaScript',
        'styling': 'Modern CSS with Flexbox/Grid',
        'framework': 'Vanilla JavaScript',
        'storage': 'LocalStorage'
    }
    
    # Check for specific framework mentions
    if 'react' in instruction_lower:
        tech_stack['framework'] = 'React'
    elif 'vue' in instruction_lower:
        tech_stack['framework'] = 'Vue.js'
    elif 'angular' in instruction_lower:
        tech_stack['framework'] = 'Angular'
    
    # Check for styling preferences
    if 'tailwind' in instruction_lower:
        tech_stack['styling'] = 'Tailwind CSS'
    elif 'bootstrap' in instruction_lower:
        tech_stack['styling'] = 'Bootstrap'
    elif 'material' in instruction_lower:
        tech_stack['styling'] = 'Material Design'
    
    # Check for backend needs
    if any(word in instruction_lower for word in ['database', 'api', 'backend', 'server']):
        tech_stack['backend'] = 'Node.js/Express (if needed)'
        tech_stack['database'] = 'SQLite/PostgreSQL (if needed)'
    
    # Check for advanced features
    if 'real-time' in instruction_lower or 'chat' in instruction_lower:
        tech_stack['realtime'] = 'WebSockets'
    
    if 'payment' in instruction_lower or 'stripe' in instruction_lower:
        tech_stack['payment'] = 'Stripe API'
    
    return tech_stack

def estimate_build_time(complexity: str, complexity_score: int, build_type: str) -> str:
    """Estimate build time based on complexity and build type"""
    
    # Base times (in seconds)
    base_times = {
        'design': {
            'simple': (3, 5),
            'medium': (5, 8),
            'complex': (8, 12)
        },
        'full': {
            'simple': (8, 12),
            'medium': (12, 20),
            'complex': (20, 35)
        }
    }
    
    min_time, max_time = base_times[build_type][complexity]
    
    # Add time for complexity score
    additional_time = complexity_score // 2
    max_time += additional_time
    
    return f"{min_time}-{max_time} seconds"

@router.post("/analyze-and-plan", response_model=BuildPlan)
async def analyze_and_plan(request: PlanRequest):
    """
    Analyze user instruction and create a detailed build plan
    Similar to Replit Agent's planning phase
    """
    
    try:
        instruction = request.instruction.strip()
        
        if not instruction:
            raise HTTPException(status_code=400, detail="Instruction cannot be empty")
        
        # Analyze complexity
        complexity, complexity_score = analyze_complexity(instruction)
        
        # Extract components
        components = extract_components(instruction, complexity_score)
        
        # Determine tech stack
        tech_stack = determine_tech_stack(instruction, complexity)
        
        # Generate title from instruction
        title = instruction[:50] + "..." if len(instruction) > 50 else instruction
        title = title.capitalize()
        
        # Generate description
        description = f"A {complexity} application with {len(components)} main components"
        
        # Create build options
        options = [
            BuildOption(
                type="design",
                label="🎨 Design/Prototype Only",
                description="Quick mockup with beautiful styling (no functionality)",
                time=estimate_build_time(complexity, complexity_score, 'design')
            ),
            BuildOption(
                type="full",
                label="🚀 Full Production App",
                description="Complete working app with all features",
                time=estimate_build_time(complexity, complexity_score, 'full')
            )
        ]
        
        # Create plan
        plan = BuildPlan(
            plan_id=str(uuid.uuid4()),
            title=title,
            description=description,
            components=components,
            tech_stack=tech_stack,
            estimated_time={
                'design_only': estimate_build_time(complexity, complexity_score, 'design'),
                'full_build': estimate_build_time(complexity, complexity_score, 'full')
            },
            options=options,
            complexity=complexity
        )
        
        return plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze instruction: {str(e)}")
