# kast/recon/http_observatory.py
import subprocess
import json
import os
import logging
import sys
from kast.config_handler import get_config
from datetime import datetime

def setup_logger(target_domain="default"):
    """
    Sets up a logger that outputs to both the console and a file.

    Args:
        target_domain (str): The target domain being scanned (used for log file naming).
    Returns:
        logging.Logger: The configured logger.
    """
    config = get_config()
    log_dir = config.get('log_directory', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    now = datetime.now()
    date_time_str = now.strftime("%y%m%d-%H%M%S")
    log_file_name = f"http_observatory-{target_domain}-{date_time_str}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create console handler with colorlog
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    try:
        from colorlog import ColoredFormatter
        console_formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            reset=True,
            style='%'
        )
        console_handler.setFormatter(console_formatter)
    except ImportError:
        # If colorlog is not installed, use a basic formatter
        console_formatter = logging.Formatter("%(levelname)-8s %(message)s")
        console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger



def scan(target_url, output_dir=None, dry_run=False):
    """
    Runs mdn-http-observatory-scan against the specified URL and saves the JSON output.

    Args:
        target_url (str): The URL to scan.
        output_dir (str, optional): The directory to save the output.
                                     Defaults to the 'output' directory from the config.
        dry_run (bool, optional): If True, prints the command that would be executed
                                  instead of running it. Defaults to False.

    Returns:
        dict or None: The parsed JSON output if successful, None otherwise.
    """
    logger = setup_logger(target_url)
    logger.info(f"Starting HTTP Observatory scan for {target_url}")
    config = get_config()
    if output_dir is None:
        output_dir = config.get('output_directory', 'output')

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"http_observatory_{target_url.replace('://', '_').replace('/', '_')}.json")

    command = ["mdn-http-observatory-scan", target_url, "--output", output_file, "--format", "json"]

    if dry_run:
        logger.info(f"[DRY RUN] Would execute: {command}")
        logger.info(f"[DRY RUN] Output would be saved to: {output_file}")
        return None

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"HTTP Observatory scan completed for {target_url}. Output saved to: {output_file}")
        with open(output_file, 'r') as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running HTTP Observatory for {target_url}: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logger.error("Error: mdn-http-observatory-scan command not found. Ensure it's installed and in your PATH.")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON output from HTTP Observatory for {target_url}.")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during HTTP Observatory scan: {e}")
        return None



if __name__ == '__main__':
    # Example usage (for testing)
    target = "https://example.com"
    output = scan(target)
    if output:
        print(json.dumps(output, indent=4))
