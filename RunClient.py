 


"""
pip  install web3 asyncio websockets eth_account ntplib tornado aiohttp  --break-system-packages
git clone https://github.com/EloiStree/2025_03_14_WsNtpIntRaspberryPiClientPyJS.git /git/apint_client/
cd /git/apint_client/
python3 RunClient.py
"""

import socket
import struct
import web3
import os
import asyncio
import websockets
import threading
import eth_account 

from eth_account.messages import encode_defunct
from eth_account import Account
from eth_account import messages

import ntplib
from time import ctime
from datetime import datetime
import tornado


current_path_directory = os.path.dirname(os.path.realpath(__file__))

relative_file_path_private_eth_key ="Keys/PrivateKey.txt"
relative_file_path_public_eth_key ="Keys/Address.txt"
relative_file_path_coaster ="Keys/CoasterOfAddress.txt"


ntp_server = "apint.ddns.net"
ws_int_server = "ws://apint.ddns.net:4615"  
ntp_server = "apint.local"
ws_int_server = "ws://apint.local:4615" 

udp_listener_ip_mask= "127.0.0.1" # localhost only
udp_listener_ip_mask= "0.0.0.0" # all sources
udp_listener_port = 3620

udp_boardcast_server_to_local =[
    "127.0.0.1:7000",
]


udp_additional_port=3621
# IS the app receive a UDP 
# The broadcast will also be sent to the additional UDP server
# To Code later. (Useful for Raspberry Pi Pico mainly)
additional_interaction_udp_server_ipv4=[]



ntp_server_offset = 0

try:
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request(ntp_server, version=3)
    offset = response.offset
    print(f"NTP server offset: {offset} seconds")
except Exception as e:
    print(f"Failed to get NTP offset: {e}")
    offset = 0

def get_milliseconds_timestamp():
    return int((datetime.now().timestamp() + offset) * 1000)


class EthUtility:
    def __init__(self):
        self.make_sure_key_folder_exists()
        bool_has_private_key = self.has_private_key()
        if not bool_has_private_key:
            print("You don't have a private key yet. Generating one for you.")
            self.private_key = os.urandom(32).hex()
            self.address = self.get_address()
            self.save_key_to_file(self.private_key)
            print("Private key: ", self.private_key[4:]+"...")
            self.save_address_file(self.get_address())
            print("To Acte in name of a secure account, please sign the following message with MetaMask: ", self.address)
            url = self.get_sign_url_to_generate_coaster(self.address)
            print ("URL: ", url)
            result = input("Copy past the mark letter result of the link here:")
            print("Result: ", result)
            self.save_coaster_to_file(result)
            
        self.private_key = self.load_key_from_file()
        self.coaster_in_file = self.load_coaster_from_file()
        self.address= self.get_address()
        self.has_coaster = len(self.coaster_in_file.strip()) > 0
        self.has_valid_coaster = False
        
        
        coaster_pieces = self.coaster_in_file.split("|")
        if len(coaster_pieces) == 3:
            self.coaster_target = coaster_pieces[0].strip()
            self.coaster_master = coaster_pieces[1].strip()
            self.coaster_proof = coaster_pieces[2].strip()
            self.has_valid_coaster = EthUtility.is_valid_signed_message(self.coaster_in_file)    
        if self.has_coaster and self.has_valid_coaster:
            print("You have a valide coaster and so are working in name of:", self.coaster_master)
        elif self.has_coaster and not self.has_valid_coaster:
            print("You have a coaster but it is not valid.")
        elif not self.has_coaster:
            print("You are not using coaster and so are working in name of:", self.address)

       
    def get_sign_url_to_generate_coaster(self, address):
        return "https://eloistree.github.io/SignMetaMaskTextHere/index.html?q=" + address
    
    def make_sure_key_folder_exists(self):
        current_python_file_path = os.path.realpath(__file__)
        target_private_key_path = os.path.join(os.path.dirname(current_python_file_path), "Keys")
        target_private_key_path = os.path.normpath(target_private_key_path)
        os.makedirs(target_private_key_path, exist_ok=True)
    
    def save_coaster_to_file(self, coaster):
        self.make_sure_key_folder_exists()
        current_python_file_path = os.path.realpath(__file__)
        target_coaster_key_path = os.path.join(os.path.dirname(current_python_file_path), relative_file_path_coaster)
        with open(target_coaster_key_path, "w") as f:
            f.write(coaster)
        return coaster
    def save_key_to_file(self, private_key):
        self.make_sure_key_folder_exists()
        current_python_file_path = os.path.realpath(__file__)
        target_private_key_path = os.path.join(os.path.dirname(current_python_file_path), relative_file_path_private_eth_key)
        
        # make sure the os path is well formated / \\
        target_private_key_path = os.path.normpath(target_private_key_path)
        
        # create the file if not exist
        if not os.path.exists(target_private_key_path):
            with open(target_private_key_path, "w") as f:
                f.write(private_key)
            return private_key
        ## write over file
        with open(target_private_key_path, "w") as f:
            f.write(private_key)
        return private_key

    
    def has_private_key(self):
        current_python_file_path = os.path.realpath(__file__)
        target_private_key_path = os.path.join(os.path.dirname(current_python_file_path), relative_file_path_private_eth_key)
        return os.path.exists(target_private_key_path)
    
    def save_address_file(self, address):
        current_python_file_path = os.path.realpath(__file__)
        target_address_path = os.path.join(os.path.dirname(current_python_file_path), relative_file_path_public_eth_key)
        with open(target_address_path, "w") as f:
            f.write(address)
        return address
        
    def load_coaster_from_file(self):
        current_python_file_path = os.path.realpath(__file__)
        target_coaster_key_path = os.path.join(os.path.dirname(current_python_file_path), relative_file_path_coaster)
        if not os.path.exists(target_coaster_key_path):
            with open(target_coaster_key_path, "w") as f:
                f.write("")
                
        with open(target_coaster_key_path, "r") as f:
            coaster = f.read().strip()
            return coaster

    def sign_message_as_clipboard(self, message):
        signed_message = self.sign_message(message)
        if not self.has_valid_coaster:
            address_to_use = self.address
            signature_to_use = signed_message.signature.hex()
            clip = f"{message}|{address_to_use}|{signature_to_use}"
        else:
            address_to_use = self.address
            signature_to_use = signed_message.signature.hex()
            master_address = self.coaster_master
            proof = self.coaster_proof
            clip = f"{message}|{address_to_use}|{signature_to_use}|{master_address}|{proof}"
        
        return clip
        
    def sign_message(self, message):
        message = encode_defunct(text=message)
        signed_message = Account.sign_message(message, private_key=self.private_key)
        return signed_message
    
    def verify_message(self, message, signed_message):
        message = encode_defunct(text=message)
        verified = Account.recover_message(message, signature=signed_message.signature)
        return verified == self.get_address()
    
    def is_valid_signed_message(message: str) -> bool:
        """
        Verifies if the provided signed message is valid.

        :param message: A string in the format "message|signer_address|signature"
        :return: True if the signature is valid, False otherwise.
        """
        try:
            # Split the message into components
            message_pieces = message.split("|")
            if len(message_pieces) != 3:
                print("❌ Invalid message format! Expected 'message|signer_address|signature'.")
                return False

            message_content, signer_address, signature = message_pieces
            message_content = message_content.strip()
            signer_address = signer_address.strip()
            signature = signature.strip()

            # Encode the message for Ethereum signature verification
            message_encoded = encode_defunct(text=message_content)

            print ("Message: ", message_content)
            print ("Signer Address: ", signer_address)
            print ("Signature: ", signature)
            print ("Encoded Message: ", message_encoded)
            
            # Recover the address from the signature
            recovered_address = Account.recover_message(message_encoded, signature=signature)

            print("🔍 Recovered address: ", recovered_address)
            print("🎯 Expected address: ", signer_address)

            # Check if the recovered address matches the expected signing address
            if recovered_address.lower() == signer_address.lower():
                print("✅ Signature is valid! The address matches the signer.")
                return True
            else:
                print("❌ Invalid signature! The signer address does not match.")
                return False

        except Exception as e:
            print("❌ Error during signature verification:", str(e))
            return False


    def get_address(self):
        address = Account.from_key(self.private_key).address
        return address
    def load_key_from_file(self):
        current_python_file_path = os.path.realpath(__file__)
        target_private_key_path = os.path.join(os.path.dirname(current_python_file_path), relative_file_path_private_eth_key)
        if not os.path.exists(target_private_key_path):
            key = os.urandom(32).hex()
            # create folder
            os.makedirs(os.path.dirname(target_private_key_path), exist_ok=True)
            # create file
            with open(target_private_key_path, "w") as f:
                f.write(key)
                
        with open(target_private_key_path, "r") as f:
            private_key = f.read().strip()
            return private_key    

wallet = EthUtility()

        

        

import aiohttp
import asyncio

ws_int_server = "ws://apint.ddns.net:4615/"
global_websocket = None
async def websocket_client():
    global global_websocket
    while True:
        print(">>> WebSocket client starting...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_int_server) as ws:
                    global_websocket = ws
                    print("Connected to WebSocket server")
                    await ws.send_str("Hello, Server!")
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            print(f"Received: {msg.data}")
                            if msg.data.startswith("SIGN:"):
                                to_sign = msg.data[5:].strip()
                                clip = wallet.sign_message_as_clipboard(to_sign)
                                # print(f"SENT: {clip}")
                                await ws.send_str(clip)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            print(f"Received binary data: {msg.data}")
                            dl = len(msg.data)
                            if dl == 4 or dl == 8 or dl == 16 or dl == 12:
                                int_found =handle_bytes_as_integer(msg.data)
                                udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                for udp_server in udp_boardcast_server_to_local:
                                    if udp_server is not None:
                                        udp_server_ip, udp_server_port = udp_server.split(":")
                                        udp_server_port = int(udp_server_port)
                                        udp_client.sendto(msg.data, (udp_server_ip, udp_server_port))

                                for udp_server_ip in additional_interaction_udp_server_ipv4:
                                    print(f"HERE to {udp_server_ip}:{udp_additional_port}")
                                    try:
                                        udp_server_port = int(udp_additional_port)
                                        udp_client.sendto(msg.data, (udp_server_ip, udp_server_port))
                                    except Exception as e:
                                        print(f"Error sending to {udp_server_ip}:{udp_server_port} {e}")
                                        pass
                                print(f"Broadcast {dl} bytes to UDPs")    
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print("WebSocket connection closed with exception:", ws.exception())
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSE:
                            print("WebSocket connection closed by the server")
                            break
        except aiohttp.ClientConnectorError as e:
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        print("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)

def handle_bytes_as_integer(data):
    dl = len(data)
    integer=None
    if dl==4 or dl==8 or dl==16 or dl==12:
        if dl == 4:
            integer = struct.unpack("<i", data)
            handle_integer_received(integer)
        elif dl == 8:
            index, integer = struct.unpack("<ii", data)
            handle_integer_received(integer)
            handle_index_integer_received(index, integer)
        elif dl == 12:
            integer, date = struct.unpack("<iq", data)
            handle_integer_received(integer)
            handle_integer_date_received(integer, date)
            
        elif dl == 16:
            index, integer, date = struct.unpack("<iiq", data)
            handle_integer_received(integer)
            handle_index_integer_received(index, integer)
            handle_integer_date_received(integer, date)
            handle_index_integer_date_received(index, integer, date)
    return integer
            
            
def handle_integer_received(integer):
    print(f"Received integer: {integer}")
    integer_to_gpio(integer)
    
def handle_index_integer_received(index, integer):
    print(f"Received integer: {integer} for index {index}")
    integer_to_gpio(integer)
    
def handle_integer_date_received(integer, date):
    print(f"Received integer: {integer} for date {date}")
    integer_to_gpio(integer)
    
def handle_index_integer_date_received(index,integer, date):
    print(f"Received integer: {integer} for index {index} and date {date}")
    integer_to_gpio(integer)
    
    
# Assuming global_websocket is set somewhere else in your code
global_websocket = None



async def console_handler():
    print(">>> Console handler started")
    
    # Use loop to handle input without blocking
    loop = asyncio.get_event_loop()

    while True:
        try:
            # Use run_in_executor to call input in a non-blocking manner
            user_input = await loop.run_in_executor(None, input, "Enter a message to send: ")

            if user_input.strip():
                print(f"Console input: {user_input}")
                user_input = user_input.strip()
                bool_is_integer = user_input.isdigit()
                if bool_is_integer:
                    user_input = int(user_input)
                    byte_integer = struct.pack("<i", user_input)
                    global global_websocket
                    print(f"A {user_input} as {byte_integer}")
                    if global_websocket:
                        print(f"Sending {user_input} as {byte_integer}")
                        await global_websocket.send_bytes(byte_integer)
                await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"Console error: {e}")


async def udp_listener():
    ip = udp_listener_ip_mask
    port = udp_listener_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    
    print(f">>> UDP listener started on {ip}:{port}")
    loop = asyncio.get_event_loop()
    
    while True:
        # Corrected line: Use `sock_recvfrom()` to receive both data and address
        data, addr = await loop.sock_recvfrom(sock, 1024)  

        try:
            global global_websocket
            if global_websocket is None:
                continue

            dl = len(data)
            if dl in {4, 8, 12, 16}:  # Cleaner way to check allowed lengths
                await global_websocket.send_bytes(data)
                
                ipv4 = addr[0]
                if ipv4 not in additional_interaction_udp_server_ipv4:
                    additional_interaction_udp_server_ipv4.append(ipv4)
                    print("Added to broadcast list: ", ipv4)   

                print(f"Sent {dl} bytes to WebSocket server")            
        except Exception as e:
            print(f"Error processing data: {e}")
            print(f"Received data: {data}")
            print(f"Received from: {addr}")


bool_is_raspberry_pi = os.path.exists("/dev/tty")
if bool_is_raspberry_pi:
    from gpiozero import LED
    
async def handle_raspberry_pi():
    if bool_is_raspberry_pi == False:
        return
    print(">>> Raspberry Pi detected")
    list_read_gpio = [
        AllowedReadGPIO(4, 20017, 20017),
        AllowedReadGPIO(17, 20017, 20017),
        AllowedReadGPIO(18, 20018, 20018),
        AllowedReadGPIO(22, 20022, 20022),
        AllowedReadGPIO(23, 20023, 20023),
        AllowedReadGPIO(24, 20024, 20024),
        AllowedReadGPIO(25, 20025, 20025),
        AllowedReadGPIO(27, 20027, 20027),
    ]
    list_read_gpio = [
        # AllowedReadGPIO(4, 20017, 20017),
        # AllowedReadGPIO(17, 20017, 20017),
        # AllowedReadGPIO(18, 20018, 20018),
        # AllowedReadGPIO(22, 20022, 20022),
        # AllowedReadGPIO(23, 20023, 20023),
        # AllowedReadGPIO(24, 20024, 20024),
        # AllowedReadGPIO(25, 20025, 20025),
        # AllowedReadGPIO(27, 20027, 20027),
    ]  
    
    
    while True:
        for gpio in list_read_gpio:
            current = gpio.is_on()
            if current != gpio.previous_value:
                gpio.previous_value = current
                print(f"GPIO {gpio.gpio_index} is {current}")
                if current:
                    byte_integer = struct.pack("<i", gpio.on_integer)
                else:
                    byte_integer = struct.pack("<i", gpio.off_integer)
                global global_websocket
                if global_websocket:
                    await global_websocket.send_bytes(byte_integer)
                
                                
        await asyncio.sleep(1)
    

class AllowedReadGPIO:
    def __init__(self,gpio_index, on_integer, off_integer):
        self.gpio_index = gpio_index
        self.on_integer = on_integer
        self.off_integer = off_integer
        self.led = LED(gpio_index)
        self.previous_value= False
        
    def is_on(self):
        return self.led.value
    
    def is_off(self):
        return not self.led.value
    
    def set_as_pull_up(self):
        self.led.on()

class AllowedWriteGPIO:
    def __init__(self,dev_index, gpio_index, default_value=False):
        self.dev_index = dev_index
        self.gpio_index = gpio_index
        self.led = LED(gpio_index)
        if default_value:
            self.led.on()
        else:
            self.led.off()
    
    def on(self):
        self.led.on()
    
    def off(self):
        self.led.off()
        
    def write(self, value):
        self.led.value = value
        
    def read(self):
        return self.led.value

def integer_to_gpio(integer):
    global bool_is_raspberry_pi
    if bool_is_raspberry_pi == False:
        return
    
    """
    DONT USE
    GPIO 27 28  are I2C
    GPIO 3 5 are I2C
    GPIO 14 15 are UART
    GPIO 8 10 are UART
    GPIO 28, GPIO 29, GPIO 30, GPIO 31: These pins are not available on the GPIO header and should not be used.
    3.3V Power (Pin 1 and Pin 17): These pins provide a 3.3V power supply, which is safe to use for powering low-current components like LEDs.
    5V Power (Pin 2 and Pin 4): These pins provide a 5V power supply, but be cautious when using them, as they can power higher-current devices.
    
    In Ou
    GPIO 17 (Pin 11): This is a general-purpose input/output pin that is commonly used in tutorials and examples. It's a good starting point for simple projects like blinking an LED.
    GPIO 18 (Pin 12): This pin can be used for general-purpose input/output or for PWM (Pulse Width Modulation), which is useful for controlling the brightness of LEDs or the speed of motors.
    GPIO 27 (Pin 13): Another general-purpose input/output pin that is often used in beginner projects.
    GPIO 22 (Pin 15): This pin is also suitable for general-purpose input/output and is frequently used in tutorials.
    GPIO 23 (Pin 16): This pin can be used for general-purpose input/output and is a good choice for simple projects.
    GPIO 24 (Pin 18): This pin is available for general-purpose input/output and is safe to use for basic projects.
    GPIO 25 (Pin 22): This pin can be used for general-purpose input/output and is another good option for beginners.
    GPIO 4 (Pin 7): This pin is often used in tutorials and is suitable for general-purpose input/output.

    | Label | HIGH | LOW|
    | -| - |-|
    | GPIO1  | 1401 |2401|
    | GPIO2  | 1402 |2402|
    | GPIO3  | 1403 |2403|
    | GPIO3  | 14.. |24..|
    | GPIO40 | 1440 |2440|
    | Allowed by dev 1  | 1441 |2441|
    | Allowed by dev 2  | 1442 |2442|
    | Allowed by dev 3  | 1443 |2443|
    | Allowed by dev 3  | 144. |24..|
    | Allowed by dev 40 | 1480 |2480|
    """    
    list_of_allowed_gpio=[4,17,18,22,23,24,25,27]
    list_of_allowed_gpio=[4,27,21,13]
    allowed = []
    count =1
    for gpio_index in list_of_allowed_gpio:
        allowed.append(AllowedWriteGPIO(count, gpio_index, False))
        count+=1
    
    if integer== 1400:
        for gpio in allowed:
            gpio.on()
    if integer== 2400:
        for gpio in allowed:
            gpio.off()
    
    if integer>=1441 and integer<=1448:
        dev_index = integer - 1440
        for gpio in allowed:
            if gpio.dev_index == dev_index:
                return gpio.on() 
            
    if integer>=2441 and integer<=2448:
        dev_index = integer - 2440
        for gpio in allowed:
            if gpio.dev_index == dev_index:
                return gpio.off()
            
    if integer>=1401 and integer<=1440:
        dev_index = integer - 1400
        for gpio in allowed:
            if gpio.gpio_index == dev_index:
                return gpio.on()
            
    if integer>=2401 and integer<=2440:
        dev_index = integer - 2400
        for gpio in allowed:
            if gpio.gpio_index == dev_index:
                return gpio.off()


    
    
    
    
    



def run_in_thread(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutine)

if __name__ == "__main__":
    ws_thread = threading.Thread(target=run_in_thread, args=(websocket_client(),))
    console_thread = threading.Thread(target=run_in_thread, args=(console_handler(),))
    udp_thread = threading.Thread(target=run_in_thread, args=(udp_listener(),))

    ws_thread.start()
    console_thread.start()
    udp_thread.start()

    ws_thread.join()
    console_thread.join()
    udp_thread.join()