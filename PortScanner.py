import socket
import threading
from queue import Queue 

# ───────────────────────────────────────────────────────────────
#  Function: ScanPort
#  Performs a TCP connect scan on a single port.
#  Returns whether the port is open or closed/filtered.
#  (Closed and filtered look the same in a TCP connect scan.)
# ───────────────────────────────────────────────────────────────

def ScanPort(ip,port):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2) # Avoid waiting forever on filtered ports
    result=s.connect_ex((ip,port)) # 0=open, else closed/filtered
    s.close()
    if result==0:
        status="open"
    else:
        status="closed"
    return port,status

# Thread-safe queue containing all ports to scan
queue=Queue() 
# Lists for storing results (shared across all threads)
OpenList=[]
CloseList=[]
# Target IP (will be filled by user later)
ip = ""
# ───────────────────────────────────────────────────────────────
#  Thread worker function
#  Runs forever waiting for ports from the queue.
#  Each worker:
#     1. Takes one port from queue
#     2. Scans it
#     3. Saves it to the correct list
#     4. Marks task as done for queue synchronization
# ───────────────────────────────────────────────────────────────
def worker():
    while True:
        port = queue.get()# Blocks until a port is available
        r = ScanPort(ip,port)
        if r[1]=="open":
            OpenList.append(r)
        else:
            CloseList.append(r)
        queue.task_done()# Signals this port is processed

# ───────────────────────────────────────────────────────────────
#  Create a pool of worker threads (once)
#  These threads will stay alive and wait for work from the queue.
#  Using daemon threads allows the program to exit even if they
#  are still running.
# ───────────────────────────────────────────────────────────────
for _ in range(200):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

print("This is a port scanner script")
print("in this script closed and filtred are the same")
# Ask user for the target IP
ip = input("Enter the IP address in form of ?.?.?.? : ")
# ───────────────────────────────────────────────────────────────
#  Main scanning loop:
#  Allows repeated scanning without restarting the program.
# ───────────────────────────────────────────────────────────────
while True:
    # Clear results from previous scan
    OpenList.clear()
    CloseList.clear()

    print("This script gives you the opportunity to scan a specific port or a range of them.")
    choice = input("For range enter 1, or anything else for one port: ")
    # Determine scanning range
    if choice == "1":
        sp = int(input("Enter the start port: "))
        ep = int(input("Enter the end port: "))
    else:
        sp = int(input("Enter the port: "))
        ep = sp

    # Push all ports into the queue (workers will process them)
    for port in range(sp, ep+1):
        queue.put(port)

    # Block until all queued ports have been scanned
    queue.join()

    # Print scanning results
    print("\nOpen ports:")
    for r in OpenList:
        print(r)
    print("\nClosed/Filtered ports:")
    for r in CloseList:
        print(r)

    print("\nAll ports scanned.\n")

    # Option to exit
    if input("Press ENTER to scan again, or type 1 to exit: ") == "1":
        break
