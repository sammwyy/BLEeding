#! /usr/bin/env python3
import click

from modules.discover import discover, ble_discover
from modules.deauth import deauth_async
from modules.mass_ping import mass_ping_async
from utils.os_utils import get_vcores, is_ble_supported, is_l2ping_supported

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
@click.option("--size", "-s", default=512, help="Length of packets to send")
@click.option("--threads", "-t", default=get_vcores(), help="Threads count to use")
def deauth(target: str, size: int, threads: int):
    print("Initializing DeAuth attack...")
    print(f"Target:         {target}")
    print(f"Packet size:    {size}")
    print(f"Threads:        {threads}")
    deauth_async(target, size, threads)
        
# MassPing command
@main.command()
@click.argument("target", required=True, type=str)
@click.option("--interface", "-i", default="hci0", help="Bluetooth interface to use")
@click.option("--size", "-s", default=512, help="Length of packets to send")
@click.option("--threads", "-t", default=get_vcores(), help="Threads count to use")
def massping(target: str, interface: str, size: int, threads: int):
    if not is_l2ping_supported():
        print("l2ping not installed, please install it first (Only linux is supported)")
        exit(1)
    
    print("Initializing DeAuth attack...")
    print(f"Target:         {target}")
    print(f"Interface:      {interface}")
    print(f"Packet size:    {size}")
    print(f"Threads:        {threads}")
    mass_ping_async(target, interface, size, threads)
    
def start():
    try:
        main()
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    