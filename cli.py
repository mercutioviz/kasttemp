import argparse
from kast.recon import http_observatory
from kast.vuln import nikto_scanner
from kast.config_handler import get_config
import os

def main():
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

    # Tool selection
    group = parser.add_argument_group("Tools")
    group.add_argument(
        "--recon", action="store_true", help="Run reconnaissance tools"
    )
    group.add_argument(
        "--vuln", action="store_true", help="Run vulnerability scanning tools"
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

    # Ensure output and report directories exist
    os.makedirs(config.get('output_directory', 'output'), exist_ok=True)
    os.makedirs(config.get('report_directory', 'reports'), exist_ok=True)

    # Run selected tools
    if args.recon and args.http_observatory_target:
        print(f"\nRunning HTTP Observatory scan against: {args.http_observatory_target}")
        http_observatory.scan(args.http_observatory_target, output_dir=config.get('output_directory'))

    if args.vuln and args.nikto_target:
        print(f"\nRunning Nikto scan against: {args.nikto_target}")
        nikto_timeout = args.nikto_timeout if args.nikto_timeout is not None else config.get('nikto_timeout')
        nikto_scanner.scan(args.nikto_target, output_dir=config.get('output_directory'), timeout=nikto_timeout)

if __name__ == "__main__":
    main()
