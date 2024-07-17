import os
import subprocess


def is_python_exe(file_path):
    try:
        # Run the strings command on the file
        result = subprocess.run(['strings', file_path], capture_output=True, text=True)
        if "PYZ-00.pyz" in result.stdout:
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return False


def scan_for_python_exes(directory):
    # List all files in the given directory
    files = os.listdir(directory)

    for file in files:
        # Check if the file has a .exe extension
        if file.endswith('.exe'):
            file_path = os.path.join(directory, file)
            # Check if the .exe file is a Python executable
            if is_python_exe(file_path):
                print(f"Python EXE found: {file}")


if __name__ == "__main__":
    scan_for_python_exes(os.getcwd())
