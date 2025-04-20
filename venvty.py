import os
import sys
import subprocess
from pathlib import Path
import shutil
import re

def find_venvs(base_path):
    venvs = []
    for root, dirs, files in os.walk(base_path):
        if 'pyvenv.cfg' in files:
            venvs.append(Path(root))
    return venvs

def is_venv(path):
    return (path / 'pyvenv.cfg').exists()

def get_python_version(python_path):
    try:
        out = subprocess.check_output([python_path, '--version'], stderr=subprocess.STDOUT, text=True, timeout=2)
        match = re.search(r'(\d+\.\d+\.\d+)', out)
        return match.group(1) if match else "?"
    except Exception:
        return "?"

def list_installed_pythons():
    # Try to find all accessible python executables
    paths = set()
    try:
        output = subprocess.check_output(['where', 'python'], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            paths.add(line.strip())
    except Exception:
        pass
    try:
        output = subprocess.check_output(['where', 'python3'], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            paths.add(line.strip())
    except Exception:
        pass
    try:
        output = subprocess.check_output(['where', 'py'], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            paths.add(line.strip())
    except Exception:
        pass
    # Filter only unique, existing paths
    valid_paths = [p for p in paths if Path(p).exists()]
    # Get version for each
    python_infos = []
    for p in valid_paths:
        version = get_python_version(p)
        python_infos.append((p, version))
    # Sort by version descending
    python_infos.sort(key=lambda x: x[1], reverse=True)
    return python_infos

def list_venvs(base_path):
    venvs = find_venvs(base_path)
    if not venvs:
        print(f"No virtual environments found in {base_path}")
    else:
        print("Found virtual environments:")
        for idx, venv in enumerate(venvs, 1):
            print(f"  [{idx}] {venv}")
    return venvs

def create_venv(target_dir, python_exec=None):
    if not python_exec:
        pythons = list_installed_pythons()
        if not pythons:
            print("No Python executables found on your system.")
            return
        print("Select a Python executable to use:")
        for idx, (exe, version) in enumerate(pythons, 1):
            print(f"  [{idx}] {exe} (version {version})")
        while True:
            choice = input(f"Enter number (1-{len(pythons)}), or path: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(pythons):
                python_exec = pythons[int(choice)-1][0]
                break
            elif Path(choice).exists():
                python_exec = choice
                break
            else:
                print("Invalid selection. Try again.")
    subprocess.run([python_exec, '-m', 'venv', str(target_dir)], check=True)
    print(f"Created venv at {target_dir}")

def delete_venv(path):
    if is_venv(path):
        confirm = input(f"Are you sure you want to delete the venv at {path}? (y/N): ")
        if confirm.lower() == 'y':
            shutil.rmtree(path)
            print(f"Deleted venv at {path}")
        else:
            print("Deletion cancelled.")
    else:
        print(f"{path} is not a valid venv.")

def activate_venv(path):
    if os.name == 'nt':
        activate_script = path / 'Scripts' / 'activate.bat'
        if not activate_script.exists():
            print("Activation script not found.")
            return
        subprocess.run(["cmd.exe", "/K", str(activate_script)])
    else:
        activate_script = path / 'bin' / 'activate'
        if not activate_script.exists():
            print("Activation script not found.")
            return
        shell = os.environ.get('SHELL', '/bin/bash')
        subprocess.run([shell, '-i', '-c', f'source \"{activate_script}\" && exec {shell}'])

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Venvy Terminal - Manage Python virtual environments from the terminal.")
    parser.add_argument('--base', type=str, default=str(Path.cwd()), help='Base directory to search for venvs (default: current directory)')
    subparsers = parser.add_subparsers(dest='command')

    parser_list = subparsers.add_parser('list', help='List all virtual environments')
    parser_create = subparsers.add_parser('create', help='Create a new virtual environment')
    parser_create.add_argument('target', type=str, help='Target directory for new venv')
    parser_create.add_argument('--python', type=str, help='Python executable to use')
    parser_delete = subparsers.add_parser('delete', help='Delete a virtual environment')
    parser_delete.add_argument('target', type=str, help='Path to venv to delete')
    parser_activate = subparsers.add_parser('activate', help='Activate a virtual environment')
    parser_activate.add_argument('target', type=str, help='Path to venv to activate')

    args = parser.parse_args()

    if args.command == 'list':
        list_venvs(Path(args.base))
    elif args.command == 'create':
        create_venv(Path(args.target), args.python)
    elif args.command == 'delete':
        delete_venv(Path(args.target))
    elif args.command == 'activate':
        activate_venv(Path(args.target))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
