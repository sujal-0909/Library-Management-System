#!/bin/bash

# Library Management System Setup Script
# This script automates the setup process for the Library Management System

echo "🚀 Library Management System Setup"
echo "=================================="

# Check if running as root for MySQL operations
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  This script should not be run as root for security reasons."
   echo "   Please run as a regular user with sudo privileges."
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status messages
print_status() {
    echo "📋 $1"
}

print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is required but not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check MySQL
if command_exists mysql; then
    print_success "MySQL client found"
else
    print_error "MySQL is required but not installed"
    echo "Installing MySQL server..."
    
    # Detect OS and install MySQL
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt; then
            sudo apt update
            sudo apt install -y mysql-server
        elif command_exists yum; then
            sudo yum install -y mysql-server
        else
            print_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command_exists brew; then
            brew install mysql
        else
            print_error "Homebrew is required on macOS"
            exit 1
        fi
    else
        print_error "Unsupported operating system"
        exit 1
    fi
fi

# Start MySQL service
print_status "Starting MySQL service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start mysql
    sudo systemctl enable mysql
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start mysql
fi

# Configure MySQL
print_status "Configuring MySQL..."
echo "Setting up MySQL root password..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password123'; FLUSH PRIVILEGES;" 2>/dev/null || {
    print_error "Failed to configure MySQL. Please set up MySQL manually."
    exit 1
}

# Create database
print_status "Creating database..."
if [ -f "database/schema.sql" ]; then
    mysql -u root -ppassword123 < database/schema.sql
    print_success "Database created successfully"
else
    print_error "Database schema file not found"
    exit 1
fi

# Set up Python environment
print_status "Setting up Python environment..."
cd backend/library_api

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Update environment configuration
print_status "Configuring environment..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password123
MYSQL_DATABASE=library_management

# JWT Configuration
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_ACCESS_TOKEN_EXPIRES=3600
EOF
    print_success "Environment configuration created"
fi

# Test the setup
print_status "Testing the setup..."
python3 -c "
import pymysql
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='password123',
        database='library_management'
    )
    connection.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

print_success "Setup completed successfully!"
echo ""
echo "🎉 Library Management System is ready to use!"
echo ""
echo "To start the application:"
echo "1. cd backend/library_api"
echo "2. source venv/bin/activate"
echo "3. python src/main.py"
echo "4. Open http://localhost:5000 in your browser"
echo ""
echo "Default login credentials:"
echo "Username: admin"
echo "Password: password"
echo ""
echo "For more information, see README.md"

