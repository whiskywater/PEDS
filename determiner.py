import os, subprocess, re, sys

PYINSTXTRACTOR_PATH = '../pyinstxtractor/pyinstxtractor.py'
PYCDC_PATH = '../../../apps/pycdc/pycdc'
PYCDAS_PATH = '../../../apps/pycdc/pycdas'
OUTPUT_PATH = './'
PADDING = '-'*10
HOTWORDS = ['key','secret','encoded', 'encrypt', 'decrypt', 'http', 'https', 'token', 
            '://', 'hidden', 'password', 'credential', 'bank', 'discord', 'video',
            'screenshot', 'record', 'exfiltrate', 'exploit', 'takeover', 'rat', 'hack',
            'database', 'store', 'pay', 'ransom', 'mp4', 'mp3', 'log']


def is_python_exe(file_path):
    try:
        # Run the strings command on the file
        result = run_command('strings', file_path)
        if "PYZ-00.pyz" in result: return True
    except Exception as e: print(f"Error processing {file_path}: {e}")
    return False


def get_python_version(file_path):
    try:
        # Run the strings command on the file
        result = run_command('strings',file_path)
        # Regular expression to match Python versions (with and without decimal points)
        version_pattern = re.compile(r'python(\d+\.\d+|\d{2,})')
        versions = version_pattern.findall(result)
        # Normalize versions to include a decimal point if missing
        normalized_versions = []
        for v in versions:
            if '.' not in v and len(v) >= 2: normalized_versions.append(f"{v[0]}.{v[1:]}")
            else: normalized_versions.append(v)
        # Filter for versions above 2.3
        valid_versions = [v for v in normalized_versions if float(v) > 2.3]
        if valid_versions: return sorted(valid_versions, reverse=True)[0]  # Return the highest version found
    except Exception as e: print(f"Error getting version for {file_path}: {e}")
    return "Version unidentified"


def extract_with_pyinstxtractor(python_version, file_path):
    try:
        # Command to run pyinstxtractor
        command = f"python{python_version} {PYINSTXTRACTOR_PATH} {file_path}"
        result = subprocess.run(command, shell=True)
        if result.returncode == 0: print(f"Successfully extracted {file_path} using pyinstxtractor.")
        else: print(f"Failed to extract {file_path} using pyinstxtractor.")
    except Exception as e:
        print(f"Error running pyinstxtractor for {file_path}: {e}")


def scan_for_python_exes(directory):
    # List all files in the given directory
    files = os.listdir(directory)

    for file in files.copy():
        # Check if the file has a .exe extension
        if file.endswith('.exe'):
            file_path = os.path.join(directory, file)
            # Check if the .exe file is a Python executable
            if is_python_exe(file_path):
                version = get_python_version(file_path)
                if version != "Version unidentified":
                    print(f"Python EXE found: {file}, Version: {version}")
                    extract_with_pyinstxtractor(version, file_path)
                    continue
        # Remove the file if it wasn't successfully extracted
        files.remove(file)
    return [f"{file}_extracted" for file in files]


def blacklisted(s): return any(s.startswith(x) for x in ('pyimod', 'pyi_rth', 'pyiboot')) or s in ('struct.pyc',)

def find_pyc_files(directory): return [f'{directory}/{x}' for x in os.listdir(directory) if x.endswith('pyc') and not blacklisted(x)]

def run_command(command, file): return subprocess.run([command, file], capture_output=True, text=True).stdout


def find_secrets(texts):
    #create a dict of filename : {(line#, line)} pairs
    output = {}
    for filetype, text in texts:
        output[filetype] = {}
        if text:
            for i, line in enumerate(text.splitlines(),start=1):
                line=line.strip().lower()
                for token in HOTWORDS:
                    if token in line and str(i) not in output[filetype].get(line,[]): output[filetype][line] = output[filetype].get(line, []) + [str(i)] #inefficient to create a new list each time but this program is fast enough
    return output


def pretty_print(file, scanned): 
    for filetype, dct in scanned.items():
        if dct: print(f"\n{PADDING}items found in {'.'.join(file.split('.')[:-1])}.{filetype}{PADDING}\n")
        for line, nums in dct.items(): print(f"#{',#'.join(nums)}: {line}")



def scan_files(files, aggressive_mode=False, save_files=False):
    found = []
    for file in files:
        curr = []
        print(f'scanning {file}...')
        text1 = 'pyc', run_command('strings',file).lower()
        py_file = run_command(PYCDC_PATH, file)
        text2 = 'py', py_file.lower()
        curr = [text1, text2]
        file_stub = '.'.join(py_file.split('.')[:-1])
        if save_files and py_file:
            with open(f"{file_stub}.py", 'w') as f: f.write(py_file)
        if aggressive_mode: 
            disas_file = run_command(PYCDAS_PATH, file)
            text3 = 'disassembly', disas_file.lower()
            curr.append(text3)
            if save_files and disas_file:
                with open(f"{file_stub}.disassembly", 'w') as f: f.write(disas_file)
        new_found = find_secrets(curr)
        found.append(new_found)
        if new_found: pretty_print(file, new_found)


def main():
    dirs = scan_for_python_exes(sys.argv[1])
    files_to_check = [find_pyc_files(dr) for dr in dirs] #collecting pyc files to scan and filtering blacklisted items
    print(f"scanning following files: ", *files_to_check)
    for files in files_to_check: scan_files(files) # scanning files for secrets


if __name__ == "__main__": main()
