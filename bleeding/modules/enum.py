import bluetooth

def enum_services(device: str):
    print(f"Enumerating services for {device}...")
    services = bluetooth.find_service(address = device)
    
    if len(services) == 0:
        print("No services found.")
        return
    
    print("Services found:")
    for service in services:
        name = service['name']
        
        if name is None:
            name = "Unknown"
        elif isinstance(name, bytes):
            name = name.decode('utf-8')
        
        print(f"> {name}")
        print(f"    * Description: {service['description']}")
        print(f"    * Protocol: {service['protocol']}")
        print(f"    * Provider: {service['provider']}")
        print(f"    * Port: {service['port']}")
        print("")