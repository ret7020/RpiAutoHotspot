sudo apt install hostapd
sudo apt install wireless-tools
sudo apt install python3-dev python3-pip && sudo pip3 install wireless netifaces psutil
sudo pip3 install pyaccesspoint flask
echo gpio |sudo tee /sys/class/leds/led0/trigger
