#! /usr/bin/env python3
import sys
import click
from colorama import Fore
import logger

from modules.enum import enum_services
from modules.discover import discover, ble_discover
from modules.deauth import deauth_async

from utils.bt_utils import BTProtocol
from utils.cli_utils import EnumType
from utils.mac_utils import random_mac_all_vendors
from utils.os_utils import get_vcores, is_ble_supported, is_windows

# Constants
DEFAULT_BT_INTERFACE = "hci0"
DEFAULT_BT_PROTOCOL = "l2cap"
DEFAULT_BUFFER_SIZE = 512
L2CAP_PSM_HCI = 0x1001
VCORES_COUNT = get_vcores()

# Banner
def print_banner():
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

# Main command
@click.group()
@click.option("--headless", default=False, is_flag=True, help="Headless mode (No colors and formatting)")
def main(headless: bool):
    logger.init_logger(headless)
    pass

# Scan command
@main.command()
# @click.option("--async", "-a", "is_async", default=False, is_flag=True, help="Scan for devices asynchronously") // ToDo
@click.option("--ble", "-b", default=False, is_flag=True, help="Scan for BLE devices")
def scan(ble: bool):
    mode = "ble" if ble else "default"
    
    if ble and not is_ble_supported():
        logger.err("BLE not supported on this platform")
        exit(1)
        
    match mode:
        case "default":
            discover()
        case "ble":
            ble_discover()
        
# DeAuth command
@main.command()
@click.argument("target", required=True, type=str)
@click.option("--port", "-p", default=L2CAP_PSM_HCI, help="Port to use")
@click.option("--protocol", "-P", default=DEFAULT_BT_PROTOCOL, help="Port to use",type=EnumType(BTProtocol))
@click.option("--size", "-s", default=DEFAULT_BUFFER_SIZE, help="Length of packets to send")
@click.option("--threads", "-t", default=VCORES_COUNT, help="Threads count to use")
def deauth(target: str, port: int, protocol: BTProtocol, size: int, threads: int):
    if protocol == BTProtocol.l2cap and is_windows():
        logger.err("L2CAP protocol is not supported on Windows, please select RFCOMM using -P flag.")
        exit(1)
    
    logger.info("Initializing DeAuth attack...")
    logger.info(f"  Target:         <lblue>{target}")
    logger.info(f"  Port:           <lblue>{port}")
    logger.info(f"  Protocol:       <lblue>{protocol.name}")
    logger.info(f"  Packet size:    <lblue>{size}")
    logger.info(f"  Threads:        <lblue>{threads}")
    deauth_async(target, port, protocol, size, threads)

# Enum command
@main.command()
@click.argument("target", required=True, type=str)
def enum(target: str):
    enum_services(target)
    
# Random MAC
@main.command()
def random_mac():
    logger.info("Generating random MAC addresses...")
    macs = random_mac_all_vendors()
    
    for mac in macs:
        vendor = mac[0].ljust(10, " ")
        addr = mac[1]
        
        logger.info(f" <lblack>* <reset>{vendor}\t<lgreen>{addr}")
    

# Start CLI
def start():
    args = sys.argv[1:]
    headless = False
    
    for _, arg in enumerate(args):
        if arg == "--headless":
            headless = True
            
    if not headless:
        print_banner()
    
    try:
        main()
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    