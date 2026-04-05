### aigen_start
import logging
from collections.abc import Callable
from importlib.metadata import entry_points

LoggerPlugin = Callable[[logging.Logger], None]

DITL_LOGGER_NAME = "ditl"


class DitlLogger:
    """Central logger singleton for DITL.

    Wraps a standard :class:`logging.Logger` under the name ``"ditl"`` and
    supports extending it at runtime via plugins discovered through the
    ``ditl.logger`` entry point group.

    Each plugin must be a callable that accepts a :class:`logging.Logger`
    and configures it (e.g. adds handlers, sets a level, attaches a formatter).

    Example entry point declaration in a plugin's ``pyproject.toml``::

        [project.entry-points."ditl.logger"]
        my_handler = "my_package.logging:setup"

    Where ``setup`` is a function ``(logger: logging.Logger) -> None``.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(DITL_LOGGER_NAME)

    @property
    def underlying_logger(self) -> logging.Logger:
        """Return the underlying :class:`logging.Logger` instance."""
        return self._logger

    def load_plugins(self) -> None:
        """Discover and apply all logger plugins registered via the ``ditl.logger`` entry point group."""
        for entry_point in entry_points(group="ditl.logger"):
            self._logger.debug("Loading logger plugin: %s", entry_point.name)
            plugin: LoggerPlugin = entry_point.load()
            plugin(self._logger)

    # ------------------------------------------------------------------
    # Standard logging delegation
    # ------------------------------------------------------------------

    def debug(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at DEBUG level."""
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at INFO level."""
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at WARNING level."""
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level."""
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at CRITICAL level."""
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level, including the current exception traceback."""
        self._logger.exception(msg, *args, **kwargs)


logger = DitlLogger()
### aigen_end
