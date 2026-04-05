# ditl-file-logger-example

<!---aigen_start-->
Example DITL logger plugin that registers a rotating file handler on the central `ditl` logger.

## How it works

This package declares an entry point in the `ditl.logger` group:

```toml
[project.entry-points."ditl.logger"]
file_handler = "ditl_file_logger_example.plugin:setup"
```

When `logger.load_plugins()` is called, DITL discovers this entry point and invokes `setup(logging.Logger)`, which attaches a [`RotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler) to the logger.

## Configuration

| Environment variable | Default     | Description                                    |
|----------------------|-------------|------------------------------------------------|
| `DITL_LOG_FILE`      | `ditl.log`  | Path to the log file (relative or absolute).   |

Rotation triggers at **5 MB** per file, keeping up to **3** backups.

## Usage

Install the package alongside `ditl`, then call `load_plugins()` once at startup:

```python
from ditl.logging import logger

logger.load_plugins()   # attaches the file handler registered by this package
logger.info("DITL is running")
```
<!---aigen_end-->
