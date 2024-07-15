import logging
from src import Config
import requests
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

config = Config()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def wait_for_resource():
    try:
        logger.info(
            f"Checking if {config.NRMOCK_SERVICE_URL}/nrmock-service/ping is available"
        )
        response = requests.get(f"{config.NRMOCK_SERVICE_URL}/nrmock-service/ping")
        response.raise_for_status()
    except requests.RequestException:
        logger.error("API not available, retrying...")
        raise


def main():
    logger.info("Waiting for nrmock to start...")
    wait_for_nrmock()
    logger.info("nrmock is ready")


if __name__ == "__main__":
    main()
