#!/bin/bash
# Techton Installer v1.0

if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

INSTALL_DIR="/opt/techton"
BIN_LINK="/usr/local/bin/techton"

echo "Installing Techton to $INSTALL_DIR..."

# 1. Clean old installs
rm -rf "$INSTALL_DIR"
rm -f "$BIN_LINK"

# 2. Create Directory Structure
mkdir -p "$INSTALL_DIR"

# 3. Copy Files
echo "Copying core files..."
cp -r bin "$INSTALL_DIR/"
cp -r templates "$INSTALL_DIR/"

# 4. Create Results Directory (Writable)
mkdir -p "$INSTALL_DIR/results"
chmod 777 "$INSTALL_DIR/results" # Allow writing logs

# 5. Create Symlink
echo "Creating executable link..."
ln -sf "$INSTALL_DIR/bin/techton" "$BIN_LINK"
chmod +x "$INSTALL_DIR/bin/techton"

echo "✅ Techton installed successfully!"
echo "Location: $INSTALL_DIR"
echo "Command : techton"