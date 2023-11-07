import pyaccesspoint
import time
import logging
import os
import subprocess
import threading
from config import *
from flask import Flask, render_template, request, redirect

class WebUI:
    def __init__(self, name, host='0.0.0.0', port='7777'):
        self.app = Flask(name)
        self.host = host
        self.port = port
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True
    
        @self.app.route('/')
        def __index():
            return self.index()

        @self.app.route("/add", methods=["POST"])
        def __add():
            return self.add()
    
    def index(self):
        logs = ""
        try:
            with open(LOGS_PATH) as fd:
                for line in (fd.readlines() [-25:]):
                    logs += line + "<br>"
        except Exception as e:
            logs = f"Can't read logs: {e}"

        wifi_config = ""
        try:
            with open(NETPLAN_CONFIG_PATH) as fd:
                wifi_config = fd.read()
        except Exception as e:
            wifi_config = "Can't read wpa_supplicant.conf: {e}"

        return render_template("index.html", logs=logs, wifi_config=wifi_config.replace("\n", "<br>"))

    def add(self):
        ssid = request.form.get("ssid")
        password = request.form.get("password")
        if ssid and password:
            print(ssid, password)
            network_config = f'''
        wlan0:
            access-points:
                "{ssid}":
                    password: {password}
            dhcp4: true
            optional: true
'''
            print(network_config)
            with open(NETPLAN_CONFIG_PATH, "a") as fd:
                fd.write(network_config)

            os.system("sudo netplan apply")

            return "OK"
        else:
            return redirect("/")


    def run(self):
        self.app.run(host=self.host, port=self.port)


def led_blinking():
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        os.system("echo 255 |sudo tee /sys/class/leds/led0/brightness")
        time.sleep(0.05)
        os.system("echo 0 |sudo tee /sys/class/leds/led0/brightness")
        time.sleep(0.05)

def check_wifi():
    ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
        return output
    except subprocess.CalledProcessError:
        return None


logging.basicConfig(filename=LOGS_PATH,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)


if __name__ == "__main__":
    logging.info("Daemon started")
    logging.info("Checking wifi")
    connected_to_wifi = False
    blinking = threading.Thread(target=led_blinking)
    blinking.start()
    for attempt in range(5):
        if check_wifi():
            logging.info("Wifi already connected, skipping hotspot starting")
            connected_to_wifi = True
            break
        time.sleep(3)
        #print("Attempt: ", attempt)
    blinking.do_run = False
    if 1: #not connected_to_wifi:
        logging.info("No wifi connected, starting hotspot")
        
        #access_point = pyaccesspoint.AccessPoint()
        #access_point.start()
        logging.info("Hotspot started")
        web = WebUI(__name__)
        web.run()
        logging.info("WebUI started")
        '''time.sleep(10)
        access_point.stop()
        logging.info("Hotspot stopped")
        time.sleep(5)
        logging.info("Rebooting now...")
        os.system("sudo reboot")
        '''
        
    

    
