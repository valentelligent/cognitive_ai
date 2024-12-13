"""
FastAPI server for Cognitive Acceleration Dashboard
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List
from ..acceleration.cognitive_acceleration_tracker import CognitiveAccelerationTracker
from ..acceleration.acceleration_integration import AccelerationIntegration

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DashboardManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_connections: List[WebSocket] = []
        self.acceleration_tracker = CognitiveAccelerationTracker()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast_metrics(self, data: Dict):
        """Broadcast metrics to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                self.logger.error(f"Error broadcasting metrics: {e}")
                
    async def start_metrics_broadcast(self):
        """Start broadcasting metrics periodically"""
        while True:
            try:
                # Get current metrics
                metrics = await self.get_current_metrics()
                
                # Broadcast to all clients
                await self.broadcast_metrics(metrics)
                
                # Wait before next update
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Error in metrics broadcast: {e}")
                await asyncio.sleep(1)
                
    async def get_current_metrics(self) -> Dict:
        """Get current cognitive acceleration metrics"""
        try:
            current_time = datetime.now().isoformat()
            
            # Get metrics from tracker
            acceleration_data = await self.acceleration_tracker.track_realtime_acceleration({
                'timestamp': current_time,
                # Add other metrics here
            })
            
            return {
                'timestamp': current_time,
                'acceleration': acceleration_data.get('current_acceleration', {}),
                'patterns': acceleration_data.get('pattern_evolution', {}),
                'growth': acceleration_data.get('growth_trajectory', {}),
                'meta_patterns': acceleration_data.get('meta_patterns', {})
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}")
            return {}

dashboard_manager = DashboardManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await dashboard_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
    except Exception as e:
        dashboard_manager.logger.error(f"WebSocket error: {e}")
    finally:
        dashboard_manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dashboard_manager.start_metrics_broadcast())
