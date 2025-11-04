"""
Plan Mode - Brainstorming Without Code Changes
Planning and architecture mode that doesn't modify project files
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PlanMode:
    """
    Planning mode for brainstorming and architecture
    Features:
    - Architecture planning
    - Task breakdown
    - Technology recommendations
    - Timeline estimation
    - Risk analysis
    - No code/file modifications
    """
    
    def __init__(self):
        self.plans = []
        self.active_plan = None
    
    def create_plan(self, 
                   project_name: str,
                   goal: str,
                   requirements: List[str] = None) -> Dict:
        """
        Create a new project plan
        
        Args:
            project_name: Name of the project
            goal: Project goal/objective
            requirements: List of requirements
        
        Returns:
            Plan structure
        """
        try:
            logger.info(f"Creating plan for: {project_name}")
            
            requirements = requirements or []
            
            plan = {
                "id": f"plan_{len(self.plans) + 1}",
                "project_name": project_name,
                "goal": goal,
                "requirements": requirements,
                "created_at": datetime.now().isoformat(),
                "architecture": {},
                "tasks": [],
                "timeline": {},
                "tech_stack": [],
                "risks": [],
                "status": "draft"
            }
            
            self.plans.append(plan)
            self.active_plan = plan
            
            return {
                "success": True,
                "plan": plan,
                "message": "Plan created. Use planning tools to develop the architecture.",
                "available_actions": [
                    "add_architecture_component",
                    "break_down_tasks",
                    "recommend_technologies",
                    "estimate_timeline",
                    "analyze_risks"
                ]
            }
            
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def add_architecture_component(self, 
                                   component_type: str,
                                   description: str,
                                   technologies: List[str] = None) -> Dict:
        """
        Add an architecture component to the plan
        
        Args:
            component_type: Type of component (frontend, backend, database, etc.)
            description: Component description
            technologies: Suggested technologies
        
        Returns:
            Updated plan
        """
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        technologies = technologies or []
        
        component = {
            "type": component_type,
            "description": description,
            "technologies": technologies,
            "added_at": datetime.now().isoformat()
        }
        
        if 'architecture' not in self.active_plan:
            self.active_plan['architecture'] = {}
        
        self.active_plan['architecture'][component_type] = component
        
        return {
            "success": True,
            "component": component,
            "plan": self.active_plan
        }
    
    def break_down_tasks(self, feature: str, subtasks: List[str]) -> Dict:
        """
        Break down a feature into subtasks
        
        Args:
            feature: Feature name
            subtasks: List of subtasks
        
        Returns:
            Task breakdown
        """
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        task_breakdown = {
            "feature": feature,
            "subtasks": [
                {
                    "id": f"task_{i+1}",
                    "description": task,
                    "status": "planned",
                    "estimated_hours": None
                }
                for i, task in enumerate(subtasks)
            ],
            "created_at": datetime.now().isoformat()
        }
        
        self.active_plan['tasks'].append(task_breakdown)
        
        return {
            "success": True,
            "breakdown": task_breakdown,
            "total_subtasks": len(subtasks)
        }
    
    def recommend_technologies(self, category: str, options: List[Dict]) -> Dict:
        """
        Recommend technologies for a category
        
        Args:
            category: Category (e.g., 'frontend', 'backend', 'database')
            options: List of technology options with pros/cons
        
        Returns:
            Recommendations
        """
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        recommendation = {
            "category": category,
            "options": options,
            "recommended_at": datetime.now().isoformat()
        }
        
        self.active_plan['tech_stack'].append(recommendation)
        
        return {
            "success": True,
            "recommendation": recommendation,
            "message": f"Added technology recommendations for {category}"
        }
    
    def estimate_timeline(self, phases: List[Dict]) -> Dict:
        """
        Estimate project timeline
        
        Args:
            phases: List of project phases with durations
        
        Returns:
            Timeline estimate
        """
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        total_days = sum(phase.get('duration_days', 0) for phase in phases)
        
        timeline = {
            "phases": phases,
            "total_days": total_days,
            "total_weeks": round(total_days / 7, 1),
            "estimated_at": datetime.now().isoformat()
        }
        
        self.active_plan['timeline'] = timeline
        
        return {
            "success": True,
            "timeline": timeline,
            "message": f"Estimated timeline: {total_days} days (~{timeline['total_weeks']} weeks)"
        }
    
    def analyze_risks(self, risks: List[Dict]) -> Dict:
        """
        Analyze project risks
        
        Args:
            risks: List of risks with mitigation strategies
        
        Returns:
            Risk analysis
        """
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        self.active_plan['risks'] = risks
        
        # Calculate risk score
        high_risk_count = sum(1 for r in risks if r.get('severity') == 'high')
        medium_risk_count = sum(1 for r in risks if r.get('severity') == 'medium')
        
        risk_score = (high_risk_count * 3) + (medium_risk_count * 2)
        
        return {
            "success": True,
            "risks": risks,
            "risk_score": risk_score,
            "high_risks": high_risk_count,
            "medium_risks": medium_risk_count,
            "message": f"Identified {len(risks)} risks (Risk Score: {risk_score})"
        }
    
    def finalize_plan(self) -> Dict:
        """
        Finalize the plan
        
        Returns:
            Complete plan ready for implementation
        """
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        self.active_plan['status'] = 'finalized'
        self.active_plan['finalized_at'] = datetime.now().isoformat()
        
        return {
            "success": True,
            "plan": self.active_plan,
            "message": "Plan finalized. Ready to start implementation!",
            "next_step": "Switch to Build Mode to start coding"
        }
    
    def get_plan_summary(self) -> Dict:
        """Get summary of active plan"""
        if not self.active_plan:
            return {"success": False, "error": "No active plan"}
        
        return {
            "success": True,
            "summary": {
                "project": self.active_plan['project_name'],
                "goal": self.active_plan['goal'],
                "architecture_components": len(self.active_plan.get('architecture', {})),
                "total_tasks": sum(len(t['subtasks']) for t in self.active_plan['tasks']),
                "tech_stack_categories": len(self.active_plan.get('tech_stack', [])),
                "timeline": self.active_plan.get('timeline', {}).get('total_weeks', 'Not estimated'),
                "risks": len(self.active_plan.get('risks', [])),
                "status": self.active_plan['status']
            },
            "plan": self.active_plan
        }


# Global instance
plan_mode_instance = PlanMode()


def create_project_plan(project_name: str, goal: str, requirements: List[str] = None) -> Dict:
    """Create a project plan in planning mode"""
    return plan_mode_instance.create_plan(project_name, goal, requirements)


def get_active_plan() -> Dict:
    """Get the active plan summary"""
    return plan_mode_instance.get_plan_summary()
