import bluetooth

def discover():
    print(f"Discovering devices...")
    
    nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=5, flush_cache=True, lookup_class=True)
    for addr, name, dev_class in nearby_devices:
        print(f" * {addr} ({name}) [{dev_class}]")
        
def ble_discover():
    from bluetooth.ble import DiscoveryService
    print(f"Discovering BLE devices...")
    
    service = DiscoveryService()
    devices = service.discover(2)
    
    for address, name in devices.items():
        print(f" * {address} ({name})") 