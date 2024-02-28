import bluetooth
import logger

def enum_services(device: str):
    logger.info(f"Enumerating services for {device}...")
    services = bluetooth.find_service(address = device)
    
    if len(services) == 0:
        logger.warn("No services found.")
        return
    
    logger.info("Services found:")
    for service in services:
        name = service['name']
        
        if name is None:
            name = "Unknown"
        elif isinstance(name, bytes):
            name = name.decode('utf-8')
        
        logger.info(f"> <cyan>{name}")
        logger.info(f"    <lblack>* <reset>Description: <lgreen>{service['description']}")
        logger.info(f"    <lblack>* <reset>Protocol: <lgreen>{service['protocol']}")
        logger.info(f"    <lblack>* <reset>Provider: <lgreen>{service['provider']}")
        logger.info(f"    <lblack>* <reset>Port: <lgreen>{service['port']}")
        print("")