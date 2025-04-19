#!/bin/bash

# Check if the script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi

# Default installation directory
DEFAULT_INSTALL_DIR="/opt/kast"

# Ask the user for the installation directory
read -p "Enter the installation directory (default: $DEFAULT_INSTALL_DIR): " INSTALL_DIR

# Use the default if the user doesn't provide input
if [[ -z "$INSTALL_DIR" ]]; then
    INSTALL_DIR="$DEFAULT_INSTALL_DIR"
fi

# Expand the path, and make sure the directory exists
INSTALL_DIR=$(realpath "$INSTALL_DIR")
mkdir -p "$INSTALL_DIR"

# Copy the necessary files and directories to the installation directory
echo "Copying files to $INSTALL_DIR"
cp -r cli.py "$INSTALL_DIR"       # Copy cli.py
cp -r kast "$INSTALL_DIR"         # Copy the kast package (containing modules)
cp -r config.yaml.example "$INSTALL_DIR/config.yaml" # Copy the config file

# Create the virtual environment
echo "Creating virtual environment in $INSTALL_DIR/.venv"
python3 -m venv "$INSTALL_DIR/.venv"

# Create the requirements.txt
echo "Creating requirements.txt"
cat > "$INSTALL_DIR/requirements.txt" <<EOL
PyYAML
colorlog
EOL

# Install the dependencies
echo "Installing dependencies using pip..."
"$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Create the log directory
echo "Creating log directory in $INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"

# Create the wrapper script
echo "Creating wrapper script in /usr/local/bin/kast"
cat > "/usr/local/bin/kast" <<EOL
#!/bin/bash
# Wrapper script for kast

# Activate the virtual environment
source "$INSTALL_DIR/.venv/bin/activate"

# Set up logging
LOG_DIR="$INSTALL_DIR/logs"
TARGET_DOMAIN="" #Will be overwritten
DATE_TIME=$(date "+%y%m%d-%H%M%S")
LOG_FILE="\$LOG_DIR/kast-\$TARGET_DOMAIN-\$DATE_TIME.log"

#check if target domain was supplied
if [ "\$1" != "" ]; then
  # Extract the domain from the URL
  TARGET_DOMAIN=$(echo "\$1" | sed -E 's/https?:\/\/(www\.)?//; s/\/.*//')
  LOG_FILE="\$LOG_DIR/kast-\$TARGET_DOMAIN-\$DATE_TIME.log"
else
  LOG_FILE="\$LOG_DIR/kast-default-\$DATE_TIME.log"
fi

export KAST_LOG_FILE="\$LOG_FILE"

# Execute cli.py with any provided arguments
python3 "$INSTALL_DIR/cli.py" "\$@"
EOL

# Make the wrapper script executable
chmod +x "/usr/local/bin/kast"

echo "Installation complete!"
echo "You can now run kast using the command: kast <options>"
