"""
Background monitoring service for continuous self-repair
Runs in the background to detect and fix errors autonomously
"""
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BackgroundMonitor:
    """Continuous background monitoring for auto-repair"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
    
    async def start(self):
        """Start background monitoring"""
        self.running = True
        logger.info("🔧 Self-repair background monitoring started")
        
        while self.running:
            try:
                await self.check_and_repair()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Background monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_and_repair(self):
        """Check logs and run auto-repair if needed"""
        from api.self_repair import self_repair_system
        
        if not self_repair_system.monitoring_active:
            return
        
        try:
            # Read recent logs
            log_files = []
            log_dir = Path("/tmp/logs")
            if log_dir.exists():
                log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
            
            combined_logs = ""
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        # Read last 500 lines
                        lines = f.readlines()[-500:]
                        combined_logs += ''.join(lines) + "\n"
                except:
                    pass
            
            if combined_logs:
                # Run auto-repair
                result = await self_repair_system.auto_repair(combined_logs)
                
                if result['errors_detected'] > 0:
                    logger.info(f"🔧 Self-repair: Found {result['errors_detected']} errors, "
                              f"fixed {result['repairs_successful']}/{result['repairs_attempted']}")
        
        except Exception as e:
            logger.error(f"Auto-repair check failed: {e}")
    
    def stop(self):
        """Stop background monitoring"""
        self.running = False
        logger.info("🔧 Self-repair background monitoring stopped")

# Global instance
background_monitor = BackgroundMonitor()
