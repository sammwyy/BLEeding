import os
import platform
import subprocess

def get_vcores():
    return os.cpu_count()

def is_linux():
    return platform.system() == 'Linux'

def is_windows():
    return platform.system() == 'Windows'

# Unused function
def is_binary_installed(binary_name: str):
    command = is_linux() and f"which {binary_name}" or f"where {binary_name}"
    try:
        out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10)
        return out != b''
    except subprocess.CalledProcessError as _:
        return False

def is_ble_supported():
    if is_linux():
        return True
    else:
        return False