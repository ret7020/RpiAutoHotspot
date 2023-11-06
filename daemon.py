import pyaccesspoint
import time
import logging
import os
import subprocess
import threading

def led_blinking():
    t = threading.currentThread()
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


logging.basicConfig(filename="events.log",
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
    if not connected_to_wifi:
        logging.info("No wifi connected, starting hotspot")
        '''
        access_point = pyaccesspoint.AccessPoint()
        access_point.start()
        logging.info("Hotspot started")
        time.sleep(10)
        access_point.stop()
        logging.info("Hotspot stopped")
        time.sleep(5)
        logging.info("Rebooting now...")
        os.system("sudo reboot")
        '''
    

    
