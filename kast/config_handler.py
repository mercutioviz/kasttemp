import yaml
import os

_config = None

def get_config():
    """
    Loads and returns the configuration from config.yaml.
    If the file doesn't exist, it attempts to load from config.yaml.example.
    """
    global _config
    if _config is None:
        config_file = 'config.yaml'
        example_config_file = 'config.yaml.example'

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    _config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error loading configuration from {config_file}: {e}")
                _config = {}
        elif os.path.exists(example_config_file):
            print(f"Warning: {config_file} not found. Loading default configuration from {example_config_file}.")
            try:
                with open(example_config_file, 'r') as f:
                    _config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error loading default configuration from {example_config_file}: {e}")
                _config = {}
        else:
            print("Warning: config.yaml and config.yaml.example not found. Using default empty configuration.")
            _config = {}

    return _config

if __name__ == '__main__':
    # Example usage:
    config = get_config()
    print("Current Configuration:")
    print(yaml.dump(config, default_flow_style=False))
