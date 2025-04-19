import subprocess
import json
import os
from kast.config_handler import get_config

def scan(target_url, output_dir=None):
    """
    Runs mdn-http-observatory-scan against the specified URL and saves the JSON output.

    Args:
        target_url (str): The URL to scan.
        output_dir (str, optional): The directory to save the output.
                                     Defaults to the 'output' directory from the config.

    Returns:
        dict or None: The parsed JSON output if successful, None otherwise.
    """
    config = get_config()
    if output_dir is None:
        output_dir = config.get('output_directory', 'output')

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"http_observatory_{target_url.replace('://', '_').replace('/', '_')}.json")

    command = ["mdn-http-observatory-scan", target_url, "--output", output_file, "--format", "json"]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"HTTP Observatory scan completed for {target_url}. Output saved to: {output_file}")
        with open(output_file, 'r') as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        print(f"Error running HTTP Observatory for {target_url}: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: mdn-http-observatory-scan command not found. Ensure it's installed and in your PATH.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON output from HTTP Observatory for {target_url}.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during HTTP Observatory scan: {e}")
        return None

if __name__ == '__main__':
    # Example usage (for testing)
    target = "https://example.com"
    output = scan(target)
    if output:
        print(json.dumps(output, indent=4))