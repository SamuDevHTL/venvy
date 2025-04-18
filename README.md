# Python Venv Manager

A user-friendly desktop application built with PyQt5 for managing Python virtual environments. This tool provides a graphical interface to create, browse, and open virtual environments in VSCode.

## Features

- Browse and list existing virtual environments
- Create new virtual environments with custom names
- View detailed information about selected virtual environments
- Open virtual environments directly in VSCode with the correct Python interpreter
- Browse custom folders to scan for virtual environments

## Requirements

- Python 3.x
- PyQt5
- VSCode (for opening environments)

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
   ```bash
   pip install PyQt5
   ```

## Usage

1. Run the application:
   ```bash
   python venvy.py
   ```

2. The main window will show a list of detected virtual environments
3. Use the buttons to:
   - Create a new virtual environment
   - Open the selected environment in VSCode
   - Browse for virtual environments in a different folder

## How It Works

The application scans your home directory by default for virtual environments. It detects them by checking for the presence of activation scripts (`activate.bat` on Windows or `activate` on Unix-like systems).

When you select a virtual environment, you can see its path and the Python interpreter location. The "Open in VSCode" feature automatically configures VSCode to use the correct Python interpreter from the selected virtual environment.

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!
 
