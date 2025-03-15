
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
