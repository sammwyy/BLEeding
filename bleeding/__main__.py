#! /usr/bin/env python3

"""
    Bleeding: Bluetooth DeAuth tool.
"""

import sys

if __name__ == "__main__":
    # Check for Python 3.6 or newer
    python_version = sys.version_info
    
    # Init colorama
    from colorama import init
    init(autoreset=True)
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("Bleeding requires Python 3.6 or newer.")
        sys.exit(1)
        
    import bleeding
    bleeding.start()
    