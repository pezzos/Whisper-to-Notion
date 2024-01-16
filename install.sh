#!/bin/bash

# Check if root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Copy the service file to /etc/systemd/system
echo "Copying service file to /etc/systemd/system"
cp resources/etc/systemd/system/whisper-to-notion.service /etc/systemd/system/

# Copy the rest of the directory to /opt/Whisper-to-Notion/
echo "Copying the rest of the directory to /opt/Whisper-to-Notion/"
cp -r . /opt/Whisper-to-Notion/
rm /opt/Whisper-to-Notion/install.sh

# Install python3 if not installed
echo "Installing python3 if not installed"
if ! command -v python3 &> /dev/null; then
    # Install python3
    apt install python3
fi

# Check if pip is installed
echo "Installing pip if not installed"
if ! command -v pip &> /dev/null; then
    # Install pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm get-pip.py
fi

# Create virtual environment
echo "Creating virtual environment"
python3 -m venv /opt/Whisper-to-Notion/env
source /opt/Whisper-to-Notion/env/bin/activate 

# Create the log file
echo "Creating log file"
touch /var/log/whisper-to-notion.log

# Install requirements with pip
echo "Installing requirements"
/opt/Whisper-to-Notion/env/bin/pip install -r /opt/Whisper-to-Notion/requirements.txt

# Reload systemd daemon
systemctl daemon-reload

# Enable the service
systemctl enable whisper-to-notion.service

# Start the service
systemctl start whisper-to-notion.service