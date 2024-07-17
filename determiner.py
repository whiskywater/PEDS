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
        # Regular expression to match Python versions (with and without decimal points)
        version_pattern = re.compile(r'python(\d+\.\d+|\d{2,})')
        versions = version_pattern.findall(result.stdout)
        # Normalize versions to include a decimal point if missing
        normalized_versions = []
        for v in versions:
            if '.' not in v and len(v) >= 2:
                normalized_versions.append(f"{v[0]}.{v[1:]}")
            else:
                normalized_versions.append(v)
        # Filter for versions above 2.3
        valid_versions = [v for v in normalized_versions if float(v) > 2.3]
        if valid_versions:
            return sorted(valid_versions, reverse=True)[0]  # Return the highest version found
    except Exception as e:
        print(f"Error getting version for {file_path}: {e}")
    return "Version unidentified"

def extract_with_pyinstxtractor(python_version, file_path):
    try:
        # Command to run pyinstxtractor
        command = f"python{python_version} pyinstxtractor/pyinstxtractor.py {file_path}"
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            print(f"Successfully extracted {file_path} using pyinstxtractor.")
        else:
            print(f"Failed to extract {file_path} using pyinstxtractor.")
    except Exception as e:
        print(f"Error running pyinstxtractor for {file_path}: {e}")

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
                if version != "Version unidentified":
                    print(f"Python EXE found: {file}, Version: {version}")
                    extract_with_pyinstxtractor(version, file_path)

if __name__ == "__main__":
    scan_for_python_exes(os.getcwd())
