import os
import subprocess
import re


def is_python_exe(file_path):
    try:
        # Run the strings command on the file
        result = subprocess.run(['strings', file_path], capture_output=True, text=True)
        if "PYZ-00.pyz" in result.stdout:
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return False


def get_python_version(file_path):
    try:
        # Run the strings command on the file
        result = subprocess.run(['strings', file_path], capture_output=True, text=True)
        # Regular expression to match Python versions
        version_pattern = re.compile(r'python(\d+\.\d+)')
        versions = version_pattern.findall(result.stdout)
        # Filter for versions above 2.3
        valid_versions = [v for v in versions if float(v) > 2.3]
        if valid_versions:
            return sorted(valid_versions, reverse=True)[0]  # Return the highest version found
    except Exception as e:
        print(f"Error getting version for {file_path}: {e}")
    return "Version unidentified"


def scan_for_python_exes(directory):
    # List all files in the given directory
    files = os.listdir(directory)

    for file in files:
        # Check if the file has a .exe extension
        if file.endswith('.exe'):
            file_path = os.path.join(directory, file)
            # Check if the .exe file is a Python executable
            if is_python_exe(file_path):
                version = get_python_version(file_path)
                print(f"Python EXE found: {file}, Version: {version}")


if __name__ == "__main__":
    scan_for_python_exes(os.getcwd())
