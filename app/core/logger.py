import logging
import os
from datetime import datetime

def setup_logger() -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"logs/{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger("app")
    logger.info(f"Logger initialized: {log_filename}")
    return logger

logger = setup_logger()
