import sys
import logging
from pathlib import Path
from core.monitoring.interaction_tracker import InteractionTracker

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_interaction.log')
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")

try:
    tracker = InteractionTracker()
    logger.info(f"Created tracker. Log file: {tracker.log_file}")
    tracker.start()
    logger.info("Tracker started")
    
    # Keep running for 30 seconds
    import time
    for i in range(30):
        logger.info(f"Running... {i+1}/30")
        time.sleep(1)
        
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
finally:
    logger.info("Test complete")
