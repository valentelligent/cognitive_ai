from datetime import datetime, timedelta
import psutil
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, db: Session):
        self.db = db
        self.start_time = datetime.now()
        self.last_check = None
        self.system_stats = {}
        
    async def check_system_health(self) -> Dict[str, Any]:
        """Check system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.system_stats = {
                'timestamp': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.start_time),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'process_count': len(psutil.pids())
            }
            
            self.last_check = datetime.now()
            return self.system_stats
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {}
    
    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        try:
            stats = await self.db.execute("""
                SELECT 
                    COUNT(*) as total_events,
                    MAX(timestamp) as last_event,
                    COUNT(DISTINCT event_type) as event_types
                FROM cognitive_evolution_events
                WHERE timestamp >= NOW() - INTERVAL '1 hour'
            """)
            
            return {
                'system_health': self.system_stats,
                'monitoring_stats': dict(stats.first()),
                'last_check': self.last_check.isoformat() if self.last_check else None
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring stats: {e}")
            return {}
