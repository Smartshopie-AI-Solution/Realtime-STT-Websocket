from scripts.exception_handling import ProjectException

from pathlib import Path
import sys
import subprocess

subprocess.check_call([sys.executable, "main.py"])



def install_requirements(venv_path):
    """Install the requirements from requirements.txt."""
    try:
        print("Installing dependencies from requirements.txt...")
        pip_path = venv_path / 'bin' / 'pip' if sys.platform != 'win32' else venv_path / 'Scripts' / 'pip.exe'
        subprocess.check_call([str(pip_path), "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: \n")
        raise ProjectException(e,sys)


def run_main(venv_path):
    """Run the main.py file."""
    try:
        print("Running main.py...")
        python_path = venv_path / 'bin' / 'python' if sys.platform != 'win32' else venv_path / 'Scripts' / 'python.exe'
        subprocess.check_call([sys.executable, "main.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running main.py: \n")
        raise ProjectException(e,sys)

def main():
    """Main setup procedure."""
    try:
        # Set the path to the virtual environment
        venv_path = Path("venv")
        
        # Step 1: Install additional requirements from requirements.txt
        install_requirements(venv_path)
        
        # Step 2: Run the main.py file
        run_main(venv_path)
    
    except Exception as e:
        print(f"An unexpected error occurred: \n")
        raise ProjectException(e, sys)
        

if __name__ == "__main__":
    main()
