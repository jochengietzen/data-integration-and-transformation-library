from ditl.logging import logger

logger.load_plugins()  # attaches the file handler registered by this package
logger.info("DITL is running")
