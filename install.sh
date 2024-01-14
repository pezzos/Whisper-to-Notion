#!/bin/bash

# Copy the service file to /etc/systemd/system
cp resources/etc/systemd/system/whisper-to-notion.service /etc/systemd/system/

# Copy the rest of the directory to /opt/Whisper-to-Notion/
cp -r . /opt/Whisper-to-Notion/

# Install python3 if not installed
if ! command -v python3 &> /dev/null; then
    # Install python3
    apt-get install python3
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    # Install pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm get-pip.py
fi

# Install requirements with pip
pip install -r requirements.txt

# Reload systemd daemon
systemctl daemon-reload

# Enable the service
systemctl enable whisper-to-notion.service

# Start the service
systemctl start whisper-to-notion.service