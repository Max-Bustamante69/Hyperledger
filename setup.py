#!/usr/bin/env python3
"""
Setup script for University Room Reservation System
This script helps set up the development environment
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_colored(message, color):
    print(f"{color}{message}{Colors.END}")

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_docker():
    """Check if Docker is installed and running"""
    print_colored("Checking Docker installation...", Colors.BLUE)
    
    success, output = run_command("docker --version")
    if not success:
        print_colored("❌ Docker is not installed. Please install Docker first.", Colors.RED)
        return False
    
    print_colored(f"✅ Docker found: {output.strip()}", Colors.GREEN)
    
    # Check if Docker is running
    success, output = run_command("docker info")
    if not success:
        print_colored("❌ Docker is not running. Please start Docker.", Colors.RED)
        return False
    
    print_colored("✅ Docker is running", Colors.GREEN)
    return True

def check_docker_compose():
    """Check if Docker Compose is installed"""
    print_colored("Checking Docker Compose installation...", Colors.BLUE)
    
    success, output = run_command("docker-compose --version")
    if not success:
        # Try docker compose (newer syntax)
        success, output = run_command("docker compose version")
    
    if not success:
        print_colored("❌ Docker Compose is not installed. Please install Docker Compose.", Colors.RED)
        return False
    
    print_colored(f"✅ Docker Compose found: {output.strip()}", Colors.GREEN)
    return True

def check_python():
    """Check Python version"""
    print_colored("Checking Python installation...", Colors.BLUE)
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored("❌ Python 3.8+ is required. Current version: {}.{}.{}".format(
            version.major, version.minor, version.micro), Colors.RED)
        return False
    
    print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} found", Colors.GREEN)
    return True

def check_go():
    """Check if Go is installed"""
    print_colored("Checking Go installation...", Colors.BLUE)
    
    success, output = run_command("go version")
    if not success:
        print_colored("❌ Go is not installed. Please install Go 1.19+", Colors.RED)
        return False
    
    print_colored(f"✅ Go found: {output.strip()}", Colors.GREEN)
    return True

def setup_python_environment():
    """Set up Python virtual environment and install dependencies"""
    print_colored("Setting up Python virtual environment...", Colors.BLUE)
    
    # Create virtual environment
    if not os.path.exists("venv"):
        success, output = run_command(f"{sys.executable} -m venv venv")
        if not success:
            print_colored("❌ Failed to create virtual environment", Colors.RED)
            return False
        print_colored("✅ Virtual environment created", Colors.GREEN)
    else:
        print_colored("✅ Virtual environment already exists", Colors.YELLOW)
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    # Install dependencies
    print_colored("Installing Python dependencies...", Colors.BLUE)
    success, output = run_command(f"{pip_path} install -r requirements.txt")
    if not success:
        print_colored("❌ Failed to install Python dependencies", Colors.RED)
        print(output)
        return False
    
    print_colored("✅ Python dependencies installed", Colors.GREEN)
    return True

def setup_fabric_tools():
    """Download and setup Hyperledger Fabric tools"""
    print_colored("Checking Hyperledger Fabric tools...", Colors.BLUE)
    
    # Check if fabric binaries exist
    fabric_bin_path = "fabric-samples/bin"
    if os.path.exists(fabric_bin_path):
        print_colored("✅ Hyperledger Fabric tools already exist", Colors.YELLOW)
        return True
    
    print_colored("Downloading Hyperledger Fabric tools...", Colors.BLUE)
    
    # Download fabric samples and binaries
    download_cmd = "curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.4.7 1.5.2"
    if platform.system() == "Windows":
        # For Windows, we'll need to handle this differently
        print_colored("⚠️ Please manually download Hyperledger Fabric tools:", Colors.YELLOW)
        print("1. Visit: https://hyperledger-fabric.readthedocs.io/en/latest/install.html")
        print("2. Follow the installation instructions for Windows")
        return True
    
    success, output = run_command(download_cmd)
    if not success:
        print_colored("❌ Failed to download Hyperledger Fabric tools", Colors.RED)
        print(output)
        return False
    
    print_colored("✅ Hyperledger Fabric tools downloaded", Colors.GREEN)
    return True

def make_scripts_executable():
    """Make shell scripts executable on Unix systems"""
    if platform.system() != "Windows":
        print_colored("Making scripts executable...", Colors.BLUE)
        
        scripts = [
            "network/scripts/start-network.sh",
            "network/scripts/stop-network.sh"
        ]
        
        for script in scripts:
            if os.path.exists(script):
                os.chmod(script, 0o755)
                print_colored(f"✅ Made {script} executable", Colors.GREEN)
    
    return True

def create_directories():
    """Create necessary directories"""
    print_colored("Creating necessary directories...", Colors.BLUE)
    
    directories = [
        "network/channel-artifacts",
        "network/crypto-config",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_colored(f"✅ Created directory: {directory}", Colors.GREEN)
    
    return True

def main():
    """Main setup function"""
    print_colored("🏗️ University Room Reservation System Setup", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)
    
    # Check prerequisites
    checks = [
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("Python", check_python),
        ("Go", check_go)
    ]
    
    failed_checks = []
    for name, check_func in checks:
        if not check_func():
            failed_checks.append(name)
        print()  # Empty line for readability
    
    if failed_checks:
        print_colored(f"❌ Setup failed. Missing requirements: {', '.join(failed_checks)}", Colors.RED)
        print_colored("Please install the missing requirements and run setup again.", Colors.YELLOW)
        return False
    
    # Setup environment
    setup_steps = [
        ("Python Environment", setup_python_environment),
        ("Fabric Tools", setup_fabric_tools),
        ("Script Permissions", make_scripts_executable),
        ("Directories", create_directories)
    ]
    
    for name, setup_func in setup_steps:
        print_colored(f"Setting up {name}...", Colors.BLUE)
        if not setup_func():
            print_colored(f"❌ Failed to setup {name}", Colors.RED)
            return False
        print()  # Empty line for readability
    
    # Success message
    print_colored("🎉 Setup completed successfully!", Colors.GREEN)
    print_colored("=" * 50, Colors.GREEN)
    print_colored("Next steps:", Colors.BLUE)
    print("1. Start the blockchain network:")
    print("   cd network && ./scripts/start-network.sh")
    print("2. Start the web application:")
    print("   cd client && python app.py")
    print("3. Open your browser to http://localhost:5000")
    print()
    print_colored("For more information, see README.md", Colors.YELLOW)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\n❌ Setup interrupted by user", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_colored(f"❌ Setup failed with error: {e}", Colors.RED)
        sys.exit(1)

