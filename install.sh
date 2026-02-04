#!/bin/bash
# Techton Installer

if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

echo "Installing Techton..."

# Set permissions
chmod +x bin/techton

# Create symlink
ln -sf "$(pwd)/bin/techton" /usr/local/bin/techton

echo "✅ Techton installed successfully!"
echo "Type 'techton' to start."
