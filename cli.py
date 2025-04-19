# cli.py
import argparse
import os
from kast.recon import http_observatory
from kast.vuln import nikto_scanner
from kast.config_handler import get_config
import logging
import sys
from datetime import datetime

def setup_logger():
    """
    Sets up a global logger that outputs to both the console and a file.
    This logger is used for the main script (cli.py).
    """
    config = get_config()
    log_dir = config.get('log_directory', 'logs')  # Use 'logs' as the default
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now()
    date_time_str = now.strftime("%y%m%d-%H%M%S")
    log_file_name = f"kast-{date_time_str}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    # Create logger
    logger = logging.getLogger('kast')  # Changed logger name to 'kast'
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

def main():
    """
    Main function to parse command line arguments and run selected tools.
    """
    logger = setup_logger()
    parser = argparse.ArgumentParser(description="Kast: Kali Automation Toolkit")
    # Configuration options
    parser.add_argument(
        "--output-dir",
        dest="output_directory",
        help="Directory to save tool output (overrides config)",
    )
    parser.add_argument(
        "--report-dir",
        dest="report_directory",
        help="Directory to save reports (overrides config)",
    )
     parser.add_argument(
        "--log-dir",
        dest="log_directory",
        help="Directory to save logs (overrides config)",
    )
    # Tool selection
    group = parser.add_argument_group("Tools")
    group.add_argument(
        "--recon", action="store_true", help="Run reconnaissance tools"
    )
    group.add_argument(
        "--vuln", action="store_true", help="Run vulnerability scanning tools"
    )
    # Global option
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run (print commands but don't execute)",
    )

    # Reconnaissance tool options
    recon_group = parser.add_argument_group("Reconnaissance Options")
    recon_group.add_argument(
        "--http-observatory-target",
        metavar="URL",
        help="Target URL for HTTP Observatory scan",
    )
    # Vulnerability scanning tool options
    vuln_group = parser.add_argument_group("Vulnerability Scanning Options")
    vuln_group.add_argument(
        "--nikto-target", metavar="URL", help="Target URL for Nikto scan"
    )
    vuln_group.add_argument(
        "--nikto-timeout",
        type=int,
        metavar="SECONDS",
        help="Timeout in seconds for Nikto scan (overrides config)",
    )
    args = parser.parse_args()
    # Load configuration
    config = get_config()
    # Override config with CLI arguments if provided
    if args.output_directory:
        config['output_directory'] = args.output_directory
    if args.report_directory:
        config['report_directory'] = args.report_directory
    if args.log_directory:
        config['log_directory'] = args.log_directory #adds log_directory to config
    # Ensure output and report directories exist
    os.makedirs(config.get('output_directory', 'output'), exist_ok=True)
    os.makedirs(config.get('report_directory', 'reports'), exist_ok=True)
    os.makedirs(config.get('log_directory','logs'), exist_ok=True) # Ensure log directory exists
    # Run selected tools
    if args.recon and args.http_observatory_target:
        logger.info(f"Running HTTP Observatory scan against: {args.http_observatory_target}")
        http_observatory.scan(args.http_observatory_target, output_dir=config.get('output_directory'), dry_run=args.dry_run)
    if args.vuln and args.nikto_target:
        logger.info(f"Running Nikto scan against: {args.nikto_target}")
        nikto_timeout = args.nikto_timeout if args.nikto_timeout is not None else config.get('nikto_timeout')
        nikto_scanner.scan(args.nikto_target, output_dir=config.get('output_directory'), timeout=nikto_timeout, dry_run=args.dry_run)
if __name__ == "__main__":
    main()
