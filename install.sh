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

# Create the virtual environment
echo "Creating virtual environment in $INSTALL_DIR/.venv"
python3 -m venv "$INSTALL_DIR/.venv"

# Copy the kast directory to the installation directory
echo "Copying kast files to $INSTALL_DIR"
cp -r kast "$INSTALL_DIR"

# Create the requirements.txt
echo "Creating requirements.txt"
cat > "$INSTALL_DIR/kast/requirements.txt" <<EOL
PyYAML
EOL

# Install the dependencies
echo "Installing dependencies using pip..."
"$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/kast/requirements.txt"

# Create the wrapper script
echo "Creating wrapper script in /usr/local/bin/kast"
cat > "/usr/local/bin/kast" <<EOL
#!/bin/bash
# Wrapper script for kast

# Activate the virtual environment
source "$INSTALL_DIR/.venv/bin/activate"

# Execute cli.py with any provided arguments
python3 "$INSTALL_DIR/kast/kast/cli.py" "\$@"
EOL

# Make the wrapper script executable
chmod +x "/usr/local/bin/kast"

echo "Installation complete!"
echo "You can now run kast using the command: kast <options>"
