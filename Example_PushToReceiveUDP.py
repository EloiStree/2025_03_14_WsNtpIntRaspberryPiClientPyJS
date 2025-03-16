"""
The following code shows how you can create a small script that becomes a UDP listener for an APint Gate.  
If you send a UDP message with an IID to the Python client, it registers you as a listener to broadcast back.  
Send any byte sequence of size 4, 8, 12, or 16 to push data to the server and become a listener of the client.  
"""

import socket
import struct
import threading
import time

def udp_sender():
    target_address = ('apint.local', 3620)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    value = 0
    
    while True:
        packed_data = struct.pack('<i', value)  # Little-endian unsigned int
        sock.sendto(packed_data, target_address)
        print(f"Sent: {value}")
        value += 1
        time.sleep(1)

def udp_listener():
    listen_address = ('0.0.0.0', 3621)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(listen_address)
    
    while True:
        data, addr = sock.recvfrom(1024)
        l = len(data)
        if l==16:    
            index,value,date = struct.unpack('<iiq', data)
            print(f"{index}|{value}|{date}")

if __name__ == "__main__":
    listener_thread = threading.Thread(target=udp_listener, daemon=True)
    listener_thread.start()
    
    udp_sender()
