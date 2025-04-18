import os
import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QLabel, QHBoxLayout, QInputDialog, QMessageBox
)


class VenvManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Venv Manager")
        self.setGeometry(100, 100, 600, 400)

        self.venv_list = QListWidget()
        self.info_label = QLabel("Select a venv to see details.")
        self.base_path = str(Path.home())  # default path to scan

        self.load_venvs()

        open_terminal_btn = QPushButton("Open Terminal")
        open_cursor_btn = QPushButton("Open in Cursor")
        new_btn = QPushButton("Create New Venv")
        browse_btn = QPushButton("Browse Folder")

        open_terminal_btn.clicked.connect(self.open_terminal)
        open_cursor_btn.clicked.connect(self.open_cursor)
        new_btn.clicked.connect(self.create_venv)
        browse_btn.clicked.connect(self.browse_folder)
        self.venv_list.currentItemChanged.connect(self.update_info)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Virtual Environments:"))
        layout.addWidget(self.venv_list)
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(open_terminal_btn)
        btn_layout.addWidget(open_cursor_btn)
        btn_layout.addWidget(browse_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_venvs(self):
        self.venv_list.clear()
        # Common locations to search for virtual environments
        search_paths = [
            Path.home(),  # User's home directory
            Path.home() / ".virtualenvs",  # virtualenvwrapper default
            Path.home() / "venvs",  # Common venv directory
            Path.home() / "virtualenvs",  # Another common venv directory
            Path.home() / "envs",  # Another common venv directory
            Path.home() / ".venv",  # Common project-level venv
            Path.home() / "Documents" / "Python" / "venvs",  # Common Windows location
            Path.home() / "Documents" / "Python" / "virtualenvs",  # Another Windows location
            Path(os.getcwd()),  # Current working directory
        ]

        # Add any custom paths from environment variables
        if "WORKON_HOME" in os.environ:
            search_paths.append(Path(os.environ["WORKON_HOME"]))
        if "VIRTUALENVWRAPPER_HOOK_DIR" in os.environ:
            search_paths.append(Path(os.environ["VIRTUALENVWRAPPER_HOOK_DIR"]))
        if "VIRTUAL_ENV" in os.environ:
            search_paths.append(Path(os.environ["VIRTUAL_ENV"]).parent)

        # Keep track of found venvs to avoid duplicates
        found_venvs = set()

        # Scan all paths for virtual environments
        for base_path in search_paths:
            if not base_path.exists():
                continue
            try:
                # First check if the base path itself is a venv
                if self.is_venv(base_path):
                    venv_path = str(base_path)
                    if venv_path not in found_venvs:
                        self.venv_list.addItem(venv_path)
                        found_venvs.add(venv_path)
                
                # Then check immediate subdirectories
                for folder in base_path.iterdir():
                    if folder.is_dir() and self.is_venv(folder):
                        venv_path = str(folder)
                        if venv_path not in found_venvs:
                            self.venv_list.addItem(venv_path)
                            found_venvs.add(venv_path)
            except PermissionError:
                continue  # Skip directories we can't access

        # Sort the list alphabetically
        self.venv_list.sortItems()

    def is_venv(self, path: Path):
        """Check if the given path is a Python virtual environment."""
        if not path.is_dir():
            return False
            
        # Check for common virtual environment indicators
        venv_indicators = [
            # Standard venv and virtualenv
            ["Scripts", "activate.bat"],  # Windows
            ["Scripts", "python.exe"],    # Windows
            ["bin", "activate"],          # Unix
            ["bin", "python"],            # Unix
            ["pyvenv.cfg"],               # venv config file
            # Conda environments
            ["conda-meta"],
            ["etc", "conda"]
        ]
        
        for indicator in venv_indicators:
            if (path / Path(*indicator)).exists():
                return True
                
        return False

    def update_info(self):
        item = self.venv_list.currentItem()
        if item:
            path = Path(item.text())
            python_exe = path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            self.info_label.setText(f"Path: {path}\nPython: {python_exe}")
        else:
            self.info_label.setText("Select a venv to see details.")

    def create_venv(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder for New Venv")
        if not folder:
            return
        name, ok = QInputDialog.getText(self, "Venv Name", "Enter name for new venv:")
        if ok and name:
            venv_path = Path(folder) / name
            try:
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
                QMessageBox.information(self, "Success", f"Venv '{name}' created!")
                self.load_venvs()
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to create virtual environment.")

    def open_terminal(self):
        item = self.venv_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "Please select a venv first.")
            return
        
        path = Path(item.text())
        if os.name == "nt":  # Windows
            activate_script = path / "Scripts" / "activate.bat"
            if not activate_script.exists():
                QMessageBox.critical(self, "Error", "Could not find activation script.")
                return
            
            # Create a temporary batch file to activate the venv and keep the window open
            temp_bat = Path(os.getenv('TEMP')) / f"activate_{path.name}.bat"
            with open(temp_bat, 'w') as f:
                f.write(f'@echo off\ncall "{activate_script}"\necho Virtual environment "{path.name}" is now active.\necho.\ncmd /k')
            
            try:
                subprocess.Popen(['cmd', '/c', str(temp_bat)], creationflags=subprocess.CREATE_NEW_CONSOLE)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open terminal:\n{str(e)}")
        else:  # Unix-like systems
            activate_script = path / "bin" / "activate"
            if not activate_script.exists():
                QMessageBox.critical(self, "Error", "Could not find activation script.")
                return
            
            try:
                # For Unix-like systems, we need to determine the default terminal
                terminal_commands = [
                    ["gnome-terminal", "--", "bash", "-c", f'source "{activate_script}" && bash'],
                    ["konsole", "-e", "bash", "-c", f'source "{activate_script}" && bash'],
                    ["xterm", "-e", "bash", "-c", f'source "{activate_script}" && bash'],
                    ["terminator", "-e", f'bash -c "source {activate_script} && bash"'],
                ]
                
                for cmd in terminal_commands:
                    try:
                        subprocess.Popen(cmd)
                        return
                    except FileNotFoundError:
                        continue
                
                raise FileNotFoundError("Could not find a suitable terminal emulator")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open terminal:\n{str(e)}")

    def open_cursor(self):
        item = self.venv_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "Please select a venv first.")
            return
        
        path = Path(item.text())
        python_exe = path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        
        try:
            # Try different Cursor commands and locations
            commands = [
                ["cursor"],  # PATH
                ["cursor.cmd"],  # Windows PATH
                # Common Windows installation locations
                [r"C:\Program Files\Cursor\Cursor.exe"],
                [r"C:\Program Files (x86)\Cursor\Cursor.exe"],
                [r"C:\Users\{}\AppData\Local\Programs\Cursor\Cursor.exe".format(os.getenv('USERNAME'))],
                # Common macOS installation locations
                ["/Applications/Cursor.app/Contents/MacOS/Cursor"],
                # Common Linux installation locations
                ["/usr/bin/cursor"],
                ["/usr/local/bin/cursor"],
                ["/opt/cursor/cursor"]
            ]
            
            # Try each command until one works
            for cmd in commands:
                try:
                    # Expand any environment variables in the path
                    if isinstance(cmd[0], str):
                        cmd[0] = os.path.expandvars(cmd[0])
                    
                    # Check if the executable exists
                    if not os.path.exists(cmd[0]):
                        continue
                        
                    # Set the Python interpreter environment variable
                    env = os.environ.copy()
                    env["PYTHONPATH"] = str(python_exe.parent.parent)
                    
                    subprocess.Popen([*cmd], env=env)
                    return  # Success, exit the function
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            raise FileNotFoundError(
                "Could not find Cursor executable in PATH or common installation locations.\n\n"
                "To install Cursor:\n"
                "1. Download from https://cursor.sh/\n"
                "2. During installation, make sure to check 'Add to PATH'"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Could not launch Cursor:\n{str(e)}"
            )

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan for Venvs")
        if folder:
            self.base_path = folder
            self.load_venvs()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VenvManager()
    win.show()
    sys.exit(app.exec_())
