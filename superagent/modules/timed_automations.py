"""
Timed Automations - Cron-like Scheduling
Schedule automated tasks and workflows
Supports cron expressions and interval-based scheduling
"""

import logging
from typing import Dict, List, Callable, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TimedAutomations:
    """
    Scheduled automation system
    Features:
    - Cron-like scheduling
    - Interval-based tasks
    - Webhook triggers
    - Task dependencies
    - Retry logic
    """
    
    def __init__(self):
        self.automations = []
        self.scheduler_running = False
    
    def create_automation(self,
                         name: str,
                         description: str,
                         schedule: str,
                         task_type: str,
                         config: Dict) -> Dict:
        """
        Create a timed automation
        
        Args:
            name: Automation name
            description: Description
            schedule: Cron expression or interval (e.g., "0 9 * * *" or "every 5 minutes")
            task_type: Type of task (webhook, script, api_call, etc.)
            config: Task configuration
        
        Returns:
            Automation configuration
        """
        try:
            logger.info(f"Creating automation: {name}")
            
            automation = {
                "id": f"auto_{len(self.automations) + 1}",
                "name": name,
                "description": description,
                "schedule": schedule,
                "task_type": task_type,
                "config": config,
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "next_run": self._calculate_next_run(schedule),
                "run_count": 0,
                "success_count": 0,
                "failure_count": 0
            }
            
            self.automations.append(automation)
            
            # Generate code for this automation
            code = self._generate_automation_code(automation)
            
            return {
                "success": True,
                "automation": automation,
                "code": code,
                "setup_instructions": self._get_setup_instructions(schedule)
            }
            
        except Exception as e:
            logger.error(f"Automation creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_automation_code(self, automation: Dict) -> str:
        """Generate Python code for automation"""
        
        name = automation['name']
        schedule = automation['schedule']
        task_type = automation['task_type']
        config = automation['config']
        
        code = f'''"""
{name} - Automated Task
Schedule: {schedule}
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def {name.lower().replace(' ', '_')}_task():
    """Execute the automated task"""
    logger.info(f"Running automation: {name} at {{datetime.now()}}")
    
'''
        
        if task_type == 'webhook':
            webhook_url = config.get('url', '')
            code += f'''    
    # Send webhook
    try:
        response = requests.post(
            "{webhook_url}",
            json={{"automation": "{name}", "timestamp": datetime.now().isoformat()}},
            headers={{"Content-Type": "application/json"}}
        )
        logger.info(f"Webhook response: {{response.status_code}}")
    except Exception as e:
        logger.error(f"Webhook failed: {{e}}")
'''
        elif task_type == 'script':
            script = config.get('script', '')
            code += f'''    
    # Execute script
    try:
        {script}
        logger.info("Script executed successfully")
    except Exception as e:
        logger.error(f"Script execution failed: {{e}}")
'''
        elif task_type == 'api_call':
            api_url = config.get('url', '')
            method = config.get('method', 'GET')
            code += f'''    
    # API call
    try:
        response = requests.{method.lower()}("{api_url}")
        logger.info(f"API response: {{response.status_code}}")
    except Exception as e:
        logger.error(f"API call failed: {{e}}")
'''
        
        # Add scheduler setup
        if 'every' in schedule.lower():
            # Interval-based
            parts = schedule.lower().split()
            interval_value = int(parts[1])
            interval_unit = parts[2].rstrip('s')  # Remove 's' from 'minutes', 'hours', etc.
            
            code += f'''
# Schedule with interval
scheduler.add_job(
    {name.lower().replace(' ', '_')}_task,
    trigger=IntervalTrigger({interval_unit}s={interval_value}),
    id="{name.lower().replace(' ', '_')}",
    name="{name}",
    replace_existing=True
)
'''
        else:
            # Cron-based
            code += f'''
# Schedule with cron
scheduler.add_job(
    {name.lower().replace(' ', '_')}_task,
    trigger=CronTrigger.from_crontab("{schedule}"),
    id="{name.lower().replace(' ', '_')}",
    name="{name}",
    replace_existing=True
)
'''
        
        code += '''
def start_automation():
    """Start the scheduler"""
    scheduler.start()
    logger.info("Automation scheduler started")

def stop_automation():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Automation scheduler stopped")

if __name__ == "__main__":
    start_automation()
    # Keep running
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        stop_automation()
'''
        
        return code
    
    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time"""
        # Simple implementation - in production use APScheduler
        if 'every' in schedule.lower():
            parts = schedule.lower().split()
            if 'minute' in schedule:
                minutes = int(parts[1])
                next_run = datetime.now() + timedelta(minutes=minutes)
            elif 'hour' in schedule:
                hours = int(parts[1])
                next_run = datetime.now() + timedelta(hours=hours)
            else:
                next_run = datetime.now() + timedelta(days=1)
            return next_run.isoformat()
        else:
            # Cron - return approximate next run
            return (datetime.now() + timedelta(hours=1)).isoformat()
    
    def _get_setup_instructions(self, schedule: str) -> List[str]:
        """Get setup instructions"""
        return [
            "1. Install dependencies: pip install apscheduler requests",
            "2. Save the generated code to a file (e.g., automation.py)",
            "3. Run the automation: python automation.py",
            f"4. Automation will run on schedule: {schedule}",
            "5. Check logs for execution status",
            "6. To run in background: nohup python automation.py &",
            "7. To stop: kill the process or Ctrl+C"
        ]
    
    def list_automations(self) -> List[Dict]:
        """List all automations"""
        return self.automations
    
    def get_automation(self, automation_id: str) -> Optional[Dict]:
        """Get automation by ID"""
        for auto in self.automations:
            if auto['id'] == automation_id:
                return auto
        return None
    
    def disable_automation(self, automation_id: str) -> bool:
        """Disable an automation"""
        auto = self.get_automation(automation_id)
        if auto:
            auto['enabled'] = False
            return True
        return False
    
    def enable_automation(self, automation_id: str) -> bool:
        """Enable an automation"""
        auto = self.get_automation(automation_id)
        if auto:
            auto['enabled'] = True
            return True
        return False


# Global instance
timed_automations_instance = TimedAutomations()


def create_scheduled_task(name: str,
                         description: str,
                         schedule: str,
                         task_type: str,
                         config: Dict) -> Dict:
    """
    Create a scheduled automation
    
    Example:
        create_scheduled_task(
            "Daily Backup",
            "Backup database daily",
            "0 2 * * *",  # 2 AM daily
            "webhook",
            {"url": "https://api.example.com/backup"}
        )
    """
    return timed_automations_instance.create_automation(
        name, description, schedule, task_type, config
    )
