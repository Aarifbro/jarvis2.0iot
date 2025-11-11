#!/bin/bash
# Installation script for JARVIS GPIO auto-setup on Raspberry Pi

echo "=========================================="
echo "  JARVIS GPIO Auto-Setup Installer"
echo "=========================================="
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo:"
    echo "  sudo ./install_gpio_service.sh"
    exit 1
fi

echo "→ Installing GPIO auto-setup service..."

# Copy setup script to system location
echo "  → Copying setup script..."
cp setup_gpio_auto.sh /usr/local/bin/jarvis-gpio-setup.sh
chmod +x /usr/local/bin/jarvis-gpio-setup.sh
echo "    ✓ Script installed to /usr/local/bin/jarvis-gpio-setup.sh"

# Copy systemd service file
echo "  → Installing systemd service..."
cp jarvis-gpio.service /etc/systemd/system/
chmod 644 /etc/systemd/system/jarvis-gpio.service
echo "    ✓ Service file installed"

# Reload systemd
echo "  → Reloading systemd daemon..."
systemctl daemon-reload
echo "    ✓ Systemd reloaded"

# Enable service
echo "  → Enabling service to start on boot..."
systemctl enable jarvis-gpio.service
echo "    ✓ Service enabled"

# Start service now
echo "  → Starting service..."
systemctl start jarvis-gpio.service
sleep 2

# Check status
echo ""
echo "→ Checking service status..."
if systemctl is-active --quiet jarvis-gpio.service; then
    echo "  ✓ Service is running!"
else
    echo "  ⚠ Service failed to start"
    echo "  Run 'sudo journalctl -u jarvis-gpio.service' to see logs"
fi

echo ""
echo "=========================================="
echo "  ✓ Installation Complete!"
echo "=========================================="
echo ""
echo "GPIO interfaces will now automatically enable on every boot."
echo ""
echo "Useful commands:"
echo "  - Check status:  sudo systemctl status jarvis-gpio"
echo "  - View logs:     sudo journalctl -u jarvis-gpio -f"
echo "  - Restart:       sudo systemctl restart jarvis-gpio"
echo "  - Disable:       sudo systemctl disable jarvis-gpio"
echo ""
echo "You can now run JARVIS without manual GPIO setup!"
echo ""
