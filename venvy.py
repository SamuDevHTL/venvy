import os
import sys
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QLabel, QHBoxLayout, QInputDialog, QMessageBox, QFrame, QScrollArea, QLineEdit, QComboBox, QDialog, QMenu, QToolTip
)
from PyQt6.QtCore import Qt, QSize, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QCursor
import fnmatch

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(35)  # Slightly smaller height
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
            }
            QPushButton {
                text-align: left;
                padding: 4px;
                border: none;
                color: #E0E0E0;
                font-weight: bold;
                background-color: #2D2D2D;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #2D2D2D;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)  # Start folded
        self.toggle_button.clicked.connect(self.toggle)
        
        self.content = QWidget()
        self.content.setMaximumHeight(0)  # Start with content hidden
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(4)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.content)
        
        self.animation = QPropertyAnimation(self.content, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.update_arrow()
        
    def toggle(self):
        checked = self.toggle_button.isChecked()
        self.content.setMaximumHeight(0 if not checked else 16777215)
        self.update_arrow()
        
    def update_arrow(self):
        arrow = "▼" if self.toggle_button.isChecked() else "▶"
        self.toggle_button.setText(f"{arrow} Paths")
        
    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

class VenvManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Venvy")
        self.setGeometry(100, 100, 700, 500)  # Smaller window size
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QListWidget {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3D3D3D;
            }
            QListWidget::item:selected {
                background-color: #2E7D32;
                color: white;
            }
            QLabel {
                font-size: 13px;
                color: #B0B0B0;
            }
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                color: #E0E0E0;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #2E7D32;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # Reduced spacing
        main_layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins

        # Title
        title = QLabel("Venvy")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #4CAF50;
                padding: 8px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # List widget with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4CAF50;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.venv_list = QListWidget()
        self.venv_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.venv_list.customContextMenuRequested.connect(self.show_context_menu)
        self.venv_list.setStyleSheet("""
            QListWidget {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3D3D3D;
            }
            QListWidget::item:selected {
                background-color: #2E7D32;
                color: white;
            }
        """)
        scroll.setWidget(self.venv_list)
        main_layout.addWidget(scroll)

        # Info label with frame
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 2px 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
            QLabel {
                color: #B0B0B0;
                font-size: 12px;
            }
        """)
        self.info_layout = QVBoxLayout(info_frame)
        self.info_layout.setSpacing(4)  # Reduced spacing between elements
        self.info_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        self.info_label = QLabel("Select a venv to see details.")
        self.info_layout.addWidget(self.info_label)
        main_layout.addWidget(info_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)  # Reduced spacing between buttons

        self.open_terminal_btn = ModernButton("Open Terminal")
        self.new_btn = ModernButton("Create New Venv")
        self.browse_btn = ModernButton("Browse Folder")

        self.open_terminal_btn.clicked.connect(self.open_terminal)
        self.new_btn.clicked.connect(self.create_venv)
        self.browse_btn.clicked.connect(self.browse_folder)
        self.venv_list.currentItemChanged.connect(self.update_info)

        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.open_terminal_btn)
        btn_layout.addWidget(self.browse_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.base_path = str(Path.home())
        self.load_venvs()

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

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        # Show a temporary tooltip
        QToolTip.showText(QCursor.pos(), "Copied to clipboard!", self, QRect(), 1000)

    def update_info(self):
        item = self.venv_list.currentItem()
        if item:
            path = Path(item.text())
            python_exe = path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            
            # Get activation command
            if os.name == "nt":  # Windows
                activate_cmd = f'"{path / "Scripts" / "activate.bat"}"'
            else:  # Unix-like systems
                activate_cmd = f'source "{path / "bin" / "activate"}"'
            
            # Clear previous widgets
            for i in reversed(range(self.info_layout.count())): 
                self.info_layout.itemAt(i).widget().setParent(None)
            
            # Create collapsible section for paths
            paths_section = CollapsibleSection("Paths")
            path_label = QLabel(f"<b>Path:</b> {path}")
            python_label = QLabel(f"<b>Python:</b> {python_exe}")
            paths_section.add_widget(path_label)
            paths_section.add_widget(python_label)
            self.info_layout.addWidget(paths_section)
            
            # Add separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("background-color: #3D3D3D;")
            separator.setFixedHeight(1)
            self.info_layout.addWidget(separator)
            
            # Command layout with inline copy button
            cmd_layout = QHBoxLayout()
            cmd_layout.setSpacing(4)  # Reduced spacing
            
            cmd_text = QLabel(f"<span style='color: #4CAF50;'>{activate_cmd}</span>")
            
            cmd_copy_btn = QPushButton("Copy")
            cmd_copy_btn.setFixedSize(45, 22)  # Even smaller button
            cmd_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(activate_cmd))
            
            cmd_layout.addWidget(cmd_text)
            cmd_layout.addWidget(cmd_copy_btn)
            cmd_layout.addStretch()
            self.info_layout.addLayout(cmd_layout)
        else:
            self.info_label.setText("Select a venv to see details.")

    def find_python_versions(self):
        """Find available Python versions on the system."""
        versions = []
        if os.name == "nt":  # Windows
            # Check common Windows Python installation locations
            common_paths = [
                r"C:\Python*",
                r"C:\Program Files\Python*",
                r"C:\Program Files (x86)\Python*",
                r"C:\Users\{}\AppData\Local\Programs\Python\Python*".format(os.getenv('USERNAME'))
            ]
            
            for path_pattern in common_paths:
                # Convert glob pattern to list of matching paths
                try:
                    # Use os.path.expandvars to handle environment variables
                    expanded_path = os.path.expandvars(path_pattern)
                    # Use os.path.expanduser to handle ~
                    expanded_path = os.path.expanduser(expanded_path)
                    # Get the directory part for globbing
                    dir_path = os.path.dirname(expanded_path)
                    pattern = os.path.basename(expanded_path)
                    
                    if not os.path.exists(dir_path):
                        continue
                        
                    # List all matching directories
                    for item in os.listdir(dir_path):
                        full_path = os.path.join(dir_path, item)
                        if os.path.isdir(full_path) and fnmatch.fnmatch(item, pattern):
                            python_exe = os.path.join(full_path, "python.exe")
                            if os.path.exists(python_exe):
                                try:
                                    result = subprocess.run([python_exe, "--version"], 
                                                          capture_output=True, text=True)
                                    version = result.stdout.strip()
                                    versions.append((version, python_exe))
                                except:
                                    continue
                except Exception as e:
                    print(f"Error checking path {path_pattern}: {e}")
                    continue
        else:  # Unix-like systems
            # Check common Unix Python locations
            common_paths = [
                "/usr/bin/python*",
                "/usr/local/bin/python*",
                "/opt/python*/bin/python*"
            ]
            
            for path_pattern in common_paths:
                try:
                    dir_path = os.path.dirname(path_pattern)
                    pattern = os.path.basename(path_pattern)
                    
                    if not os.path.exists(dir_path):
                        continue
                        
                    for item in os.listdir(dir_path):
                        full_path = os.path.join(dir_path, item)
                        if os.path.isfile(full_path) and not os.path.islink(full_path) and fnmatch.fnmatch(item, pattern):
                            try:
                                result = subprocess.run([full_path, "--version"], 
                                                      capture_output=True, text=True)
                                version = result.stdout.strip()
                                versions.append((version, full_path))
                            except:
                                continue
                except Exception as e:
                    print(f"Error checking path {path_pattern}: {e}")
                    continue
        
        # Add the current Python version
        current_version = f"Python {sys.version.split()[0]} (Current)"
        versions.insert(0, (current_version, sys.executable))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_versions = []
        for version, path in versions:
            if path not in seen:
                seen.add(path)
                unique_versions.append((version, path))
        
        return unique_versions

    def create_venv(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder for New Venv")
        if not folder:
            return
            
        # Get available Python versions
        versions = self.find_python_versions()
        if not versions:
            QMessageBox.critical(self, "Error", "No Python versions found on the system.")
            return
            
        # Create dialog for venv name and Python version
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Virtual Environment")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QLineEdit, QComboBox {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 5px;
                color: #E0E0E0;
                min-width: 200px;
            }
            QLabel {
                color: #B0B0B0;
            }
        """)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # Python version selection
        version_layout = QHBoxLayout()
        version_label = QLabel("Python Version:")
        version_combo = QComboBox()
        for version, path in versions:
            version_combo.addItem(version, path)
        version_layout.addWidget(version_label)
        version_layout.addWidget(version_combo)
        layout.addLayout(version_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = ModernButton("Create")
        cancel_btn = ModernButton("Cancel")
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Dialog setup
        dialog.setFixedSize(400, 150)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Connect signals
        create_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Please enter a name for the virtual environment.")
                return
                
            python_path = version_combo.currentData()
            venv_path = Path(folder) / name
            
            try:
                subprocess.run([python_path, "-m", "venv", str(venv_path)], check=True)
                QMessageBox.information(self, "Success", f"Venv '{name}' created!")
                self.load_venvs()
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Error", f"Failed to create virtual environment:\n{str(e)}")

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

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan for Venvs")
        if folder:
            self.base_path = folder
            self.load_venvs()

    def show_context_menu(self, position):
        item = self.venv_list.itemAt(position)
        if not item:
            return

        menu = QMenu()
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_venv(item))
        
        menu.exec(self.venv_list.mapToGlobal(position))

    def delete_venv(self, item):
        path = Path(item.text())
        
        # Create confirmation dialog
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("Confirm Deletion")
        confirm_dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QLabel {
                color: #B0B0B0;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout()
        confirm_dialog.setLayout(layout)
        
        message = QLabel(f"Are you sure you want to delete the virtual environment at:\n{path}?")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        button_layout = QHBoxLayout()
        delete_btn = ModernButton("Delete")
        cancel_btn = ModernButton("Cancel")
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        confirm_dialog.setFixedSize(400, 150)
        confirm_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        delete_btn.clicked.connect(confirm_dialog.accept)
        cancel_btn.clicked.connect(confirm_dialog.reject)
        
        if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                import shutil
                shutil.rmtree(path)
                self.load_venvs()  # Refresh the list
                QMessageBox.information(self, "Success", "Virtual environment deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete virtual environment:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VenvManager()
    win.show()
    sys.exit(app.exec())
