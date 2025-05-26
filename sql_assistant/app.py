from ui.gradio_app import create_gradio_interface
from config.config import MODEL_CONFIG, FEW_SHOT_CONFIG, PERFORMANCE_CONFIG
from utils.schema_extractor import get_database_schema
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, PERFORMANCE_CONFIG['logging_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def startup_checks():
    """Perform startup health checks"""
    logger.info("Performing startup checks...")
    
    try:
        # Test database connection
        schema = get_database_schema()
        logger.info("Database connection successful")
        
        # Log configuration
        logger.info(f"Model: {MODEL_CONFIG['model_name']}")
        logger.info(f"Few-shot enabled: {FEW_SHOT_CONFIG['enabled']}")
        logger.info(f"Cache enabled: {FEW_SHOT_CONFIG['cache_enabled']}")
        logger.info(f"Schema optimization: {PERFORMANCE_CONFIG['schema_optimization']}")
        
        return True
    except Exception as e:
        logger.error(f"Startup check failed: {str(e)}")
        return False

if __name__ == "__main__":
    if startup_checks():
        logger.info("Starting Gradio interface...")
        interface = create_gradio_interface()
        interface.launch(
            share=False,
            server_name="0.0.0.0",
            server_port=7860
        )
    else:
        logger.error("Startup checks failed. Please fix the issues and try again.")
