# 🐍 Venvy – Python Virtual Environment Manager

A simple GUI-based program to manage Python virtual environments.

---

## ✨ Features

- **Browse and Manage Venvs**: Easily view and manage all your Python virtual environments in one place
- **Create New Venvs**: Create new virtual environments with a simple interface
- **Open Terminal**: Quickly open a terminal with the selected virtual environment activated
- **Copy Activation Commands**: One-click copy of activation commands for easy use
- **Delete Venvs**: Safely remove virtual environments you no longer need
- **Automatic Detection**: Automatically finds virtual environments in common locations

---

## ⚙️ Requirements

- Python 3.6 or higher
- PyQt5
- `venv` (included in Python standard library)

---

## 📦 Installation

1. Clone this repository:
    
    ```bash
    git clone https://github.com/samuDevHTL/venvy.git
    cd venvy
    
    ```
    
2. Install required packages:
    
    ```bash
    pip install -r requirements.txt
    
    ```
    

---

## 🚀 Usage

Run the application:

```bash
python venvy.py

```

---

# 🖥️ Main Features (Venvy)

- **List View**: Shows all detected virtual environments
- **Info Panel**: Displays details about the selected virtual environment:
    - Path to the virtual environment
    - Python executable location
    - Activation command with copy button
- **Actions**:
    - Create new virtual environment
    - Open terminal with selected venv activated
    - Browse for additional venv locations
    - Delete virtual environments (right-click menu)

---

# 🐍 venvty – Terminal Utility

`venvty.py` is a simple terminal utility for managing Python virtual environments from the command line.

## Features
- List, create, activate, and delete virtual environments via CLI
- Choose Python version when creating a new venv
- Works cross-platform (Windows, Linux, Mac)

## Usage Example

List all venvs in the current directory (and subfolders):

```bash
python venvty.py list
```

Create a new venv in a folder called `myenv`:

```bash
python venvty.py create myenv
```

Delete a venv:

```bash
python venvty.py delete myenv
```

Activate a venv (opens a terminal with it activated):

```bash
python venvty.py activate myenv
```

You can specify a base directory for searching/creating venvs with `--base`:

```bash
python venvty.py list --base path/to/your/projects
```

You can also specify a Python executable when creating a venv:

```bash
python venvty.py create myenv --python path/to/python.exe
```

---

For more details, run:

```bash
python venvty.py --help