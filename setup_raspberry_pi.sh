#!/bin/bash
################################################################################
# JARVIS 2.0 IoT - Complete Raspberry Pi Setup Script
# Run this script after fresh flash to setup everything automatically
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
clear
echo "================================================================================"
echo "                    JARVIS 2.0 IoT - Auto Setup Script"
echo "                    Raspberry Pi Complete Installation"
echo "================================================================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    log_warning "Not running on Raspberry Pi - continuing anyway..."
else
    log_info "Detected: $(cat /proc/device-tree/model)"
fi

echo ""
log_info "This script will:"
echo "  1. Update system packages"
echo "  2. Install Python dependencies"
echo "  3. Install GPIO libraries (pigpio, RPi.GPIO)"
echo "  4. Install sensor libraries (DHT, I2C)"
echo "  5. Setup I2C and SPI interfaces"
echo "  6. Install audio libraries for voice"
echo "  7. Configure systemd services"
echo "  8. Setup environment variables"
echo "  9. Create startup scripts"
echo " 10. Test all hardware connections"
echo ""

read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warning "Installation cancelled"
    exit 0
fi

################################################################################
# STEP 1: System Update
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 1/10: Updating system packages..."
echo "================================================================================"
sudo apt-get update -y
sudo apt-get upgrade -y
log_success "System packages updated"

################################################################################
# STEP 2: Install Python and pip
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 2/10: Installing Python 3 and pip..."
echo "================================================================================"
sudo apt-get install -y python3 python3-pip python3-dev python3-venv
log_success "Python 3 installed"

################################################################################
# STEP 3: Install GPIO Libraries
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 3/10: Installing GPIO libraries..."
echo "================================================================================"

# pigpio for servo control
log_info "Installing pigpio..."
sudo apt-get install -y pigpio python3-pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
log_success "pigpio installed and daemon started"

# RPi.GPIO for general GPIO
log_info "Installing RPi.GPIO..."
sudo apt-get install -y python3-rpi.gpio
log_success "RPi.GPIO installed"

################################################################################
# STEP 4: Install Sensor Libraries
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 4/10: Installing sensor libraries..."
echo "================================================================================"

# I2C tools for LCD display
log_info "Installing I2C tools..."
sudo apt-get install -y i2c-tools python3-smbus
log_success "I2C tools installed"

# DHT sensor library
log_info "Installing Adafruit DHT sensor library..."
pip3 install adafruit-circuitpython-dht --break-system-packages 2>/dev/null || \
    pip3 install adafruit-circuitpython-dht
log_success "DHT library installed"

# RPLCD for LCD display
log_info "Installing RPLCD library..."
pip3 install RPLCD --break-system-packages 2>/dev/null || pip3 install RPLCD
log_success "RPLCD installed"

################################################################################
# STEP 5: Enable I2C and SPI
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 5/10: Enabling I2C and SPI interfaces..."
echo "================================================================================"

# Enable I2C
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    log_info "I2C enabled in config"
fi

# Enable SPI
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    log_info "SPI enabled in config"
fi

# Load I2C modules
sudo modprobe i2c-dev
sudo modprobe i2c-bcm2708

log_success "I2C and SPI configured"

################################################################################
# STEP 6: Install Audio Libraries
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 6/10: Installing audio libraries for voice..."
echo "================================================================================"

sudo apt-get install -y portaudio19-dev python3-pyaudio
sudo apt-get install -y espeak espeak-ng
sudo apt-get install -y alsa-utils

# Install pyttsx3 for text-to-speech
pip3 install pyttsx3 --break-system-packages 2>/dev/null || pip3 install pyttsx3

# Install vosk for speech recognition
pip3 install vosk sounddevice --break-system-packages 2>/dev/null || \
    pip3 install vosk sounddevice

log_success "Audio libraries installed"

################################################################################
# STEP 7: Install Python Dependencies
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 7/10: Installing Python dependencies from requirements.txt..."
echo "================================================================================"

if [ -f "requirements.txt" ]; then
    log_info "Found requirements.txt, installing packages..."
    
    # Try with --break-system-packages for Debian 12+
    pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
        pip3 install -r requirements.txt
    
    log_success "Python dependencies installed"
else
    log_warning "requirements.txt not found, skipping..."
fi

################################################################################
# STEP 8: Setup Environment Variables
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 8/10: Setting up environment variables..."
echo "================================================================================"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating .env file..."
    cat > .env << 'EOF'
# JARVIS 2.0 IoT Configuration

# GPIO Pin Configuration (BCM numbering)
NECK_SERVO_PIN=18
ARM_L_SERVO_PIN=23
ARM_R_SERVO_PIN=24

# Motor Pins (L298N)
MOTOR_L_EN=12
MOTOR_L_IN1=5
MOTOR_L_IN2=6
MOTOR_R_EN=13
MOTOR_R_IN1=26
MOTOR_R_IN2=16

# Sensor Pins
PIR_PIN=17
ULTRASONIC_TRIGGER_PIN=27
ULTRASONIC_ECHO_PIN=22
DHT_PIN=4
DHT_TYPE=11
MQ3_ENABLED=false
MQ3_DIGITAL_PIN=26

# I2C Display
I2C_ADDRESS=0x27

# Voice Settings
VOICE_RATE=150
VOICE_VOLUME=1.0

# LLM Settings (Optional - add your keys)
# GROQ_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Location
JARVIS_LOCATION=home
EOF
    log_success ".env file created"
else
    log_info ".env file already exists"
fi

################################################################################
# STEP 9: Setup Systemd Services
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 9/10: Setting up systemd services..."
echo "================================================================================"

# Run GPIO setup service installer
if [ -f "install_gpio_service.sh" ]; then
    log_info "Installing GPIO auto-setup service..."
    sudo bash install_gpio_service.sh
    log_success "GPIO service installed"
else
    log_warning "install_gpio_service.sh not found"
fi

################################################################################
# STEP 10: Create Startup Scripts
################################################################################
echo ""
echo "================================================================================"
log_info "STEP 10/10: Creating startup scripts..."
echo "================================================================================"

# Make all scripts executable
chmod +x *.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true

log_info "Making scripts executable..."
for script in start_jarvis.sh restart_jarvis.sh status.sh run.sh; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        log_success "$script is now executable"
    fi
done

################################################################################
# Hardware Test (Optional)
################################################################################
echo ""
echo "================================================================================"
log_info "Hardware Test (Optional)"
echo "================================================================================"

read -p "Do you want to run hardware tests now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Running hardware tests..."
    
    if [ -f "test_complete_system.py" ]; then
        python3 test_complete_system.py
    else
        log_warning "test_complete_system.py not found"
    fi
else
    log_info "Skipping hardware tests"
fi

################################################################################
# Final Summary
################################################################################
echo ""
echo "================================================================================"
echo "                         INSTALLATION COMPLETE!"
echo "================================================================================"
echo ""

log_success "JARVIS 2.0 IoT has been successfully installed!"
echo ""

echo "📋 INSTALLED COMPONENTS:"
echo "  ✓ Python 3 and pip"
echo "  ✓ GPIO libraries (pigpio, RPi.GPIO)"
echo "  ✓ Sensor libraries (DHT, I2C, ultrasonic)"
echo "  ✓ Audio libraries (espeak, vosk, pyttsx3)"
echo "  ✓ Display libraries (RPLCD)"
echo "  ✓ All Python dependencies"
echo "  ✓ Systemd services configured"
echo ""

echo "🎯 NEXT STEPS:"
echo ""
echo "  1. Reboot Raspberry Pi (recommended):"
echo "     sudo reboot"
echo ""
echo "  2. After reboot, test JARVIS:"
echo "     cd $(pwd)"
echo "     python3 main.py"
echo ""
echo "  3. Or run in headless mode:"
echo "     python3 jarvis_headless.py"
echo ""
echo "  4. Check status:"
echo "     ./status.sh"
echo ""

echo "📚 USEFUL COMMANDS:"
echo "  • Start JARVIS:        python3 main.py"
echo "  • Headless mode:       python3 jarvis_headless.py"
echo "  • Test sensors:        python3 test_complete_system.py"
echo "  • Test ultrasonic:     python3 test_ultrasonic_sensor.py"
echo "  • Test follow me:      python3 test_follow_me.py"
echo "  • Test conversation:   python3 test_conversation_features.py"
echo ""

echo "🔧 TROUBLESHOOTING:"
echo "  • Check GPIO setup:    sudo systemctl status jarvis-gpio"
echo "  • View logs:           journalctl -u jarvis-gpio"
echo "  • Test I2C display:    sudo i2cdetect -y 1"
echo "  • Test pigpiod:        sudo systemctl status pigpiod"
echo ""

echo "📖 DOCUMENTATION:"
echo "  • System ready:        cat SYSTEM_READY.txt"
echo "  • Quick reference:     cat PIN_REFERENCE_CARD.txt"
echo "  • Features guide:      cat COMPLETE_FEATURES_GUIDE.md"
echo ""

echo "================================================================================"
echo "                      🤖 JARVIS 2.0 IoT Ready! 🚀"
echo "================================================================================"
echo ""

# Ask about reboot
read -p "Would you like to reboot now? (recommended) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Rebooting in 5 seconds..."
    sleep 5
    sudo reboot
else
    log_info "Please reboot manually when ready: sudo reboot"
fi
