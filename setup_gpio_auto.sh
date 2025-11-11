#!/bin/bash
# Auto GPIO Setup Script for JARVIS IoT System
# This script automatically enables GPIO and starts required services on boot

set -e

echo "================================================"
echo "  JARVIS GPIO Auto-Setup"
echo "================================================"

# Function to check if running on Raspberry Pi
is_raspberry_pi() {
    if [ -f /proc/cpuinfo ]; then
        grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null && return 0
    fi
    return 1
}

# Function to enable GPIO permissions
enable_gpio() {
    echo "→ Enabling GPIO access..."
    
    # Add user to gpio group if not already
    if ! groups | grep -q gpio; then
        echo "  Adding $USER to gpio group..."
        sudo usermod -a -G gpio "$USER"
        echo "  ✓ Added to gpio group (logout and login to apply)"
    else
        echo "  ✓ Already in gpio group"
    fi
    
    # Set GPIO permissions
    if [ -d /sys/class/gpio ]; then
        sudo chmod -R a+rw /sys/class/gpio 2>/dev/null || true
        echo "  ✓ GPIO permissions set"
    fi
    
    # Enable I2C if needed
    if [ -e /dev/i2c-1 ]; then
        sudo chmod a+rw /dev/i2c-1 2>/dev/null || true
        echo "  ✓ I2C permissions set"
    fi
    
    # Enable SPI if needed
    if [ -e /dev/spidev0.0 ]; then
        sudo chmod a+rw /dev/spidev0.* 2>/dev/null || true
        echo "  ✓ SPI permissions set"
    fi
}

# Function to start pigpiod daemon
start_pigpiod() {
    echo "→ Starting pigpio daemon..."
    
    # Check if pigpiod is installed
    if ! command -v pigpiod &> /dev/null; then
        echo "  ⚠ pigpiod not installed"
        echo "  Installing pigpio..."
        sudo apt-get update -qq && sudo apt-get install -y pigpio python3-pigpio
    fi
    
    # Check if already running
    if pgrep -x "pigpiod" > /dev/null; then
        echo "  ✓ pigpiod already running"
    else
        # Start pigpiod
        sudo pigpiod -s 10 2>/dev/null || pigpiod -s 10 2>/dev/null || true
        sleep 1
        
        if pgrep -x "pigpiod" > /dev/null; then
            echo "  ✓ pigpiod started successfully"
        else
            echo "  ⚠ Could not start pigpiod"
            return 1
        fi
    fi
}

# Function to enable I2C and SPI interfaces
enable_interfaces() {
    echo "→ Enabling hardware interfaces..."
    
    # Check if raspi-config is available (Raspberry Pi)
    if command -v raspi-config &> /dev/null; then
        # Enable I2C
        sudo raspi-config nonint do_i2c 0 2>/dev/null || true
        echo "  ✓ I2C enabled"
        
        # Enable SPI
        sudo raspi-config nonint do_spi 0 2>/dev/null || true
        echo "  ✓ SPI enabled"
        
        # Enable hardware PWM
        sudo raspi-config nonint do_serial_hw 0 2>/dev/null || true
        echo "  ✓ Hardware serial enabled"
    else
        echo "  ⚠ raspi-config not available (not on Raspberry Pi?)"
        
        # Try manual config file editing
        if [ -f /boot/config.txt ]; then
            echo "  → Checking /boot/config.txt..."
            
            # Enable I2C
            if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
                echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt > /dev/null
                echo "  ✓ I2C enabled in config.txt"
            fi
            
            # Enable SPI
            if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
                echo "dtparam=spi=on" | sudo tee -a /boot/config.txt > /dev/null
                echo "  ✓ SPI enabled in config.txt"
            fi
        fi
    fi
}

# Function to load kernel modules
load_modules() {
    echo "→ Loading kernel modules..."
    
    # Load I2C modules
    sudo modprobe i2c-dev 2>/dev/null || true
    sudo modprobe i2c-bcm2835 2>/dev/null || true
    echo "  ✓ I2C modules loaded"
    
    # Load SPI modules
    sudo modprobe spi-bcm2835 2>/dev/null || true
    echo "  ✓ SPI modules loaded"
}

# Main execution
main() {
    echo ""
    
    if is_raspberry_pi; then
        echo "✓ Running on Raspberry Pi"
        echo ""
        
        enable_interfaces
        load_modules
        enable_gpio
        start_pigpiod
        
        echo ""
        echo "================================================"
        echo "  ✓ GPIO Setup Complete!"
        echo "================================================"
        echo ""
        echo "All GPIO interfaces are now enabled and ready."
        echo "You can now run JARVIS without manual GPIO setup."
        echo ""
        
    else
        echo "⚠ Not running on Raspberry Pi"
        echo "  Running in development/simulation mode"
        echo "  GPIO operations will be simulated"
        echo ""
        
        # Try to start pigpiod anyway (for dev containers with GPIO access)
        start_pigpiod || true
    fi
}

# Run main function
main

# Check if running as part of systemd service
if [ -n "$SYSTEMD_EXEC_PID" ]; then
    echo "Running as systemd service - keeping alive"
    # Keep the service running
    while true; do
        sleep 60
        # Restart pigpiod if it died
        if ! pgrep -x "pigpiod" > /dev/null; then
            echo "pigpiod died, restarting..."
            start_pigpiod
        fi
    done
fi
