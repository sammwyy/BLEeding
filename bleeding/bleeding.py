#! /usr/bin/env python3
import click

from modules.enum import enum_services
from modules.discover import discover, ble_discover
from modules.deauth import deauth_async

from utils.bt_utils import BTProtocol
from utils.cli_utils import EnumType
from utils.mac_utils import random_mac_all_vendors, random_mac_tail
from utils.os_utils import get_vcores, is_ble_supported

# Constants
DEFAULT_BT_INTERFACE = "hci0"
DEFAULT_BT_PROTOCOL = "l2cap"
DEFAULT_BUFFER_SIZE = 512
L2CAP_PSM_HCI = 0x1001
VCORES_COUNT = get_vcores()

# Main command
@click.group()
def main():
    pass

# Scan command
@main.command()
@click.option("--ble", "-b", default=False, is_flag=True, help="Scan for BLE devices")
def scan(ble: bool):
    if ble:
        if is_ble_supported():
            ble_discover()
        else:
            print("BLE not supported on this platform")
            exit(1)
    else:
        discover()
        
# DeAuth command
@main.command()
@click.argument("target", required=True, type=str)
@click.option("--port", "-p", default=L2CAP_PSM_HCI, help="Port to use")
@click.option("--protocol", "-P", default=DEFAULT_BT_PROTOCOL, help="Port to use",type=EnumType(BTProtocol))
@click.option("--size", "-s", default=DEFAULT_BUFFER_SIZE, help="Length of packets to send")
@click.option("--threads", "-t", default=VCORES_COUNT, help="Threads count to use")
def deauth(target: str, port: int, protocol: BTProtocol, size: int, threads: int):
    print("Initializing DeAuth attack...")
    print(f"Target:         {target}")
    print(f"Port:           {port}")
    print(f"Protocol:       {protocol.name}")
    print(f"Packet size:    {size}")
    print(f"Threads:        {threads}")
    deauth_async(target, port, protocol, size, threads)

# Enum command
@main.command()
@click.argument("target", required=True, type=str)
def enum(target: str):
    enum_services(target)
    
# Random MAC
@main.command()
def random_mac():
    print("Generating random MAC addresses...")
    macs = random_mac_all_vendors()
    
    for mac in macs:
        vendor = mac[0].ljust(10, " ")
        addr = mac[1]
        
        print(f" * {vendor}\t{addr}")
    

# Start CLI
def start():
    try:
        main()
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    