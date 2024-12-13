from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session
import json
import asyncio
from datetime import datetime, timedelta
import random
import logging
from typing import Dict, Any

from .database import get_db, engine, SessionLocal
from . import models
from .cognitive_logger import CognitiveEvolutionLogger
from .services.cognitive_state_service import CognitiveStateService
from .services.gray_area_detector import GrayAreaDetector
from .services.health_monitor import HealthMonitor
from .config.monitoring_config import MonitoringConfig

# Load configuration
config = MonitoringConfig()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cognitive AI Dashboard")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected clients
clients = set()

# Store active monitoring tasks and services
monitoring_tasks = []
health_monitor = None

@app.on_event("startup")
async def startup_event():
    """Initialize services and start monitoring on startup"""
    try:
        logger.info("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        logger.info("Starting cognitive monitoring services...")
        
        # Initialize database session
        db = SessionLocal()
        
        # Initialize health monitor
        global health_monitor
        health_monitor = HealthMonitor(db)
        
        if config.ENABLE_AUTONOMOUS_MONITORING:
            # Start cognitive monitoring task
            monitoring_tasks.append(
                asyncio.create_task(monitor_cognitive_evolution(db))
            )
            
            # Start health monitoring task
            monitoring_tasks.append(
                asyncio.create_task(monitor_system_health(health_monitor))
            )
            
            # Start generating metrics task
            metrics_task = asyncio.create_task(generate_metrics(db))
            monitoring_tasks.append(metrics_task)
        
        logger.info("Cognitive monitoring services started successfully")
        
    except Exception as e:
        logger.error(f"Error starting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down cognitive monitoring services...")
    for task in monitoring_tasks:
        task.cancel()
    logger.info("Services shutdown complete")

async def monitor_cognitive_evolution(db: Session):
    """Background task to continuously monitor cognitive evolution"""
    try:
        while True:
            metrics = generate_metrics_for_response()
            
            # Create cognitive logger instance
            cognitive_logger = CognitiveEvolutionLogger(db)
            
            # Log event with current metrics
            await cognitive_logger.log_cognitive_event({
                'type': 'autonomous_monitoring',
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
            
            # Track patterns if enabled
            if config.ENABLE_PATTERN_ANALYSIS:
                patterns = await cognitive_logger.track_evolution_patterns()
                logger.info(f"Tracked patterns: {patterns}")
            
            logger.debug(f"Logged cognitive metrics: {metrics}")
            await asyncio.sleep(config.COGNITIVE_MONITOR_INTERVAL)
            
    except asyncio.CancelledError:
        logger.info("Cognitive monitoring task cancelled")
    except Exception as e:
        logger.error(f"Error in cognitive monitoring: {e}")

async def monitor_system_health(health_monitor: HealthMonitor):
    """Background task to monitor system health"""
    try:
        while True:
            health_stats = await health_monitor.check_system_health()
            logger.debug(f"System health stats: {health_stats}")
            
            # Alert on high resource usage
            if health_stats.get('cpu_usage', 0) > 80:
                logger.warning("High CPU usage detected")
            if health_stats.get('memory_usage', 0) > 80:
                logger.warning("High memory usage detected")
                
            await asyncio.sleep(30)  # Check every 30 seconds
            
    except asyncio.CancelledError:
        logger.info("Health monitoring task cancelled")
    except Exception as e:
        logger.error(f"Error in health monitoring: {e}")

async def generate_metrics(db: Session):
    """Generate and store metrics in the database"""
    counter = 0
    while True:
        try:
            timestamp = datetime.now()
            counter += 1
            metrics = {
                "acceleration": {
                    "typing_speed": random.uniform(0.5, 1.0),
                    "error_recovery": random.uniform(0.6, 0.9),
                    "context_switching": random.uniform(0.4, 0.8),
                    "problem_solving": random.uniform(0.5, 0.95)
                },
                "patterns": {
                    "recognition_speed": random.uniform(0.6, 0.9),
                    "integration_speed": random.uniform(0.5, 0.85),
                    "pattern_complexity": random.uniform(0.3, 0.7)
                },
                "growth": {
                    "acceleration_trend": random.uniform(0.4, 0.8),
                    "learning_efficiency": random.uniform(0.5, 0.9),
                    "adaptability": random.uniform(0.6, 0.85)
                },
                "meta_patterns": {
                    "learning_acceleration": random.uniform(0.5, 0.9),
                    "pattern_recognition_evolution": random.uniform(0.4, 0.8),
                    "integration_speed_changes": random.uniform(0.3, 0.7),
                    "adaptability_growth": random.uniform(0.5, 0.85)
                },
                "cognitive_load": {
                    "current_load": random.uniform(0.3, 0.9),
                    "complexity_level": random.uniform(0.2, 0.8),
                    "verification_counter": counter
                }
            }
            
            logger.info(f"Generating metrics #{counter}")
            
            # Store in database
            db_metrics = models.CognitiveMetrics(
                timestamp=timestamp,
                acceleration=metrics["acceleration"],
                patterns=metrics["patterns"],
                growth=metrics["growth"],
                meta_patterns=metrics["meta_patterns"],
                cognitive_load=metrics["cognitive_load"]
            )
            db.add(db_metrics)
            db.commit()
            logger.info(f"Stored metrics #{counter} in database")
            
            # Add timestamp to metrics for websocket broadcast
            metrics["timestamp"] = timestamp.isoformat()
            
            # Broadcast to all connected clients
            if clients:
                await asyncio.gather(
                    *[client.send_text(json.dumps(metrics)) for client in clients]
                )
            
            await asyncio.sleep(1)  # Update every second
        except Exception as e:
            logger.error(f"Error in generate_metrics: {str(e)}")
            await asyncio.sleep(1)  # Wait before retrying

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not health_monitor:
        raise HTTPException(status_code=503, detail="Health monitor not initialized")
    
    return await health_monitor.get_monitoring_stats()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    
    # Initialize services
    cognitive_logger = CognitiveEvolutionLogger(db)
    state_service = CognitiveStateService(db)
    
    try:
        while True:
            data = await websocket.receive_text()
            event_data = json.loads(data)
            
            # Log cognitive evolution event
            await cognitive_logger.log_cognitive_event(event_data)
            
            # Track evolution patterns if enabled
            patterns = await cognitive_logger.track_evolution_patterns() if config.ENABLE_PATTERN_ANALYSIS else {}
            
            # Process state transition
            current_state = {
                'baseline_state': event_data.get('baseline_state', {}),
                'evolved_state': event_data.get('evolved_state', {})
            }
            
            transition_data = {
                'transition_indicators': event_data.get('transition_indicators', {}),
                'consciousness_patterns': event_data.get('consciousness_patterns', {}),
                'context_depth': event_data.get('context_depth', 0),
                'context_quality': event_data.get('context_quality', {}),
                'trigger': event_data.get('trigger', 'unknown'),
                'self_awareness': event_data.get('self_awareness', 0.0),
                'meta_cognitive': event_data.get('meta_cognitive', {}),
                'pattern_evolution': event_data.get('pattern_evolution', {}),
                'understanding_metrics': event_data.get('understanding_metrics', {}),
                'interaction_type': event_data.get('interaction_type', 'general'),
                'resonance_score': event_data.get('resonance_score', 0.0),
                'uncertainty': event_data.get('uncertainty', {}),
                'certainty_flux': event_data.get('certainty_flux', {}),
                'environment': event_data.get('environment', {}),
                'system_state': event_data.get('system_state', {})
            }
            
            await state_service.log_cognitive_transition(current_state, transition_data)
            
            # Analyze gray areas if enabled
            gray_area_analysis = (
                await state_service.analyze_gray_areas(timedelta(minutes=30))
                if config.ENABLE_GRAY_AREA_DETECTION else {}
            )
            
            # Get consciousness patterns if enabled
            consciousness_patterns = (
                await state_service.get_consciousness_emergence_patterns()
                if config.ENABLE_CONSCIOUSNESS_TRACKING else {}
            )
            
            # Get system health
            health_stats = await health_monitor.check_system_health() if health_monitor else {}
            
            # Prepare comprehensive response
            response = {
                "metrics": generate_metrics_for_response(),
                "evolution_patterns": patterns,
                "gray_area_analysis": gray_area_analysis,
                "consciousness_patterns": consciousness_patterns,
                "system_health": health_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_json(response)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

@app.websocket("/ws/gray-area")
async def gray_area_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """Dedicated WebSocket endpoint for gray area detection"""
    if not config.ENABLE_GRAY_AREA_DETECTION:
        await websocket.close(code=1000, reason="Gray area detection disabled")
        return
        
    await websocket.accept()
    detector = GrayAreaDetector(websocket, db)
    await detector.monitor_cognitive_transitions()

def generate_metrics_for_response():
    """Generate cognitive metrics"""
    return {
        "acceleration": random.uniform(0.1, 1.0),
        "pattern_recognition": random.uniform(0.1, 1.0),
        "cognitive_load": random.uniform(0.1, 1.0),
        "learning_rate": random.uniform(0.1, 1.0),
        "counter": 0  # Remove global counter dependency
    }
