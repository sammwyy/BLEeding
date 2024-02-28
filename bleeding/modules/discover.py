import bluetooth
import logger

def discover():
    logger.info("Discovering devices...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=5, flush_cache=True, lookup_class=True)
    for addr, name, dev_class in nearby_devices:
        logger.info(f" <lblack>* <reset>{addr} <lgreen>({name}) <lblack>[{dev_class}]")
        
def ble_discover():
    from bluetooth.ble import DiscoveryService
    logger.info(f"Discovering BLE devices...")
    
    service = DiscoveryService()
    devices = service.discover(2)
    
    for address, name in devices.items():
        logger.info(f" <lblack>* <reset>{address} <lgreen>({name})") 