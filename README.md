
# Ws Ntp Int Raspberry Pi Client Py JS  

This is an example of how you can use a Raspberry Pi to connect to a WebSocket server linked to NTP, allowing integer sharing between devices using Python and JavaScript.  

### Install Auto Start  

Then, add the following two commands.  
Replace the paths with your own.  

#### Open the JavaScript Client when the Raspberry Pi starts  
(Useful for human interaction)  

If you need to edit the script frequently:  
```
chromium-browser /home/student/Desktop/GitEdit/apint_client/RunClient.html
```  
If you just need to run it without editing on the Pi directly:  
```
chromium-browser /git/apint_client/RunClient.html
```  

#### Open the Python Client when the Raspberry Pi starts  
(Useful as a relay LAN app without authentication)  
```
lxterminal -e "python3 /home/student/Desktop/GitEdit/apint_client/RunClient.py"
```  
If you just need to run it without editing on the Pi directly:  
```
lxterminal -e "python3 /git/apint_client/RunClient.py"
```


--------------

```
su root

sudo git clone https://github.com/EloiStree/2025_03_14_WsNtpIntRaspberryPiClientPyJS.git /git/apint_client
rm Keys -r


crontab -e

@reboot lxterminal -e "python3 /git/apint_client/RunClient.py"
@reboot chromium-browser /git/apint_client/RunClient.html
```


Create a SSH key on your window:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIS2syCcYRDf+O0sn+goxBnb6tKjYPZo6F0q/95TcPrd elois@Phenix
```
Then you can use this command and replace with yourse:

Add the key to the allows user by ssh  
```
mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIS2syCcYRDf+O0sn+goxBnb6tKjYPZo6F0q/95TcPrd elois@Phenix" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && sudo systemctl restart ssh
```

Connect as this user.
```
ssh -i ~/.ssh/eloistree_all_pi root@raspberrypi.local
```

