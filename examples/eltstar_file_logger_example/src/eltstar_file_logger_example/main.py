from ditl.logging import logger

logger.setup_stdout_handler()
logger.load_plugins()  # attaches the file handler registered by this package
logger.debug("Running debug message")
logger.info("DITL is running with info")
logger.warning("DITL is running with warning")
logger.critical("DITL is running with critical")
logger.error("DITL is running with error")
