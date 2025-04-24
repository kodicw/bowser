import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Log file creation
logfile = Path(f"./{__name__}")
if not logfile.exists():
    if not logfile.parent.exists():
        logfile.parent.mkdir(parents=True)
    logfile.touch()

# File handler
filehandler = RotatingFileHandler(
    str(logfile),
    maxBytes=5 * 1024 * 1024,
    mode="a",
    backupCount=6,
    encoding=None,
    delay=False,
)


logging.Formatter("%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
