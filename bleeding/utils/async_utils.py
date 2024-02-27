import multiprocessing
import sys
import time

def create_async_task(threads: int, func, args=()):
    print(f"\nStarting thread pool with {threads} workers...")
    time.sleep(1)

    error = None
    
    def error_callback(e):
        nonlocal error
        if not error:
            error = e
    
    with multiprocessing.Pool(processes=threads) as pool:
        for worker_id in range(0, threads):
            worker_args = args + (worker_id,)
            pool.apply_async(func, args=worker_args, error_callback=lambda e: error_callback(e))
        
        while True:
            try:
                time.sleep(1)
                if error:
                    break
            except KeyboardInterrupt:
                break
        
        if error:
            print(f"\nThread pool throws an exception: {error}")
        
        print("Stopping threads...")
        pool.close()
        pool.terminate()
        pool.join()
        exit(1)