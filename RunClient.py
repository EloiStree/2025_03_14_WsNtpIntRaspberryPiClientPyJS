

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



relative_file_path_private_eth_key ="Keys/PrivateKey.txt"
relative_file_path_public_eth_key ="Keys/Address.txt"
relative_file_path_coaster ="Keys/CoasterOfAddress.txt"

ntp_server = "apint.ddns.net"
ws_int_server = "ws://apint.ddns.net:4615"  

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
        self.coaster_valid = False
        
        
        coaster_pieces = self.coaster_in_file.split("|")
        if len(coaster_pieces) == 3:
            self.coaster_target = coaster_pieces[0].strip()
            self.coaster_master = coaster_pieces[1].strip()
            self.coaster_proof = coaster_pieces[2].strip()
            self.coaster_valid = EthUtility.is_valid_signed_message(self.coaster_in_file)    
        if self.has_coaster and self.coaster_valid:
            print("You have a valide coaster and so are working in name of:", self.coaster_master)
        elif self.has_coaster and not self.coaster_valid:
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

        

        


global_websocket = None

ws_int_server = "ws://apint.ddns.net:4615/"

async def websocket_client():
    global global_websocket
    while True:
        try:
            # Establish the WebSocket connection
            print("Connecting to the WebSocket server...")
            async with websockets.connect(ws_int_server, open_timeout=3) as websocket:

                global_websocket = websocket
                print("WebSocket connection established.")
                
                # You can now send and receive messages
                while True:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                    
                    # Example: Send a response back
                    response = f"Echo: {message}"
                    await websocket.send(response)
                    print(f"Sent response: {response}")
                    
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
        finally:
            global_websocket = None
            print("WebSocket connection closed.")
            
        await asyncio.sleep(5)

async def console_handler():
    
    print ("Console handler started")
    while True:
        try:
            
            user_input = input("Enter a message to send: ")
            global global_websocket
            if user_input.strip():
                print(f"Console input: {user_input}")
                bool_is_integer = user_input.isdigit()
                if bool_is_integer:
                    user_input = int(user_input)
                    byte_integer =struct.pack("<i", user_input)
                    await global_websocket.send(byte_integer, text=False)
                    
                    
        except Exception as e:
            print(f"Console error: {e}")
            break

async def main():
    await asyncio.gather(websocket_client(), console_handler())

if __name__ == "__main__":
    asyncio.run(main())