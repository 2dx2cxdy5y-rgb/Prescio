import logging

# -----------------------------
# LOGGER CONFIG
# -----------------------------

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(
    "Prescio"
)

# -----------------------------
# INFO
# -----------------------------

def log_info(message):

    logger.info(message)

# -----------------------------
# WARNING
# -----------------------------

def log_warning(message):

    logger.warning(message)

# -----------------------------
# ERROR
# -----------------------------

def log_error(message):

    logger.error(message)