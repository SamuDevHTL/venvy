# Venvy - Python Virtual Environment Manager

a simple gui based programm to manage python venvs

## Features

- **Browse and Manage Venvs**: Easily view and manage all your Python virtual environments in one place
- **Create New Venvs**: Create new virtual environments with a simple interface
- **Open Terminal**: Quickly open a terminal with the selected virtual environment activated
- **Copy Activation Commands**: One-click copy of activation commands for easy use
- **Delete Venvs**: Safely remove virtual environments you no longer need
- **Automatic Detection**: Automatically finds virtual environments in common locations

## Requirements

- Python 3.6 or higher
- PyQt5
- venv (included in Python standard library)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/samuDevHTL/venvy.git
cd venvy
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python venvy.py
```

### Main Features

- **List View**: Shows all detected virtual environments
- **Info Panel**: Displays details about the selected virtual environment
  - Path to the virtual environment
  - Python executable location
  - Activation command with copy button
- **Actions**:
  - Create new virtual environment
  - Open terminal with selected venv activated
  - Browse for additional venv locations
  - Delete virtual environments (right-click menu)