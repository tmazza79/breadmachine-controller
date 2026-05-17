from umqtt.simple import MQTTClient
import network
from picozero import pico_temp_sensor, pico_led
from time import sleep
import machine

ssid = 'my_ssid'
password = 'my_passwd'

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    cc=0
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        pico_led.on()
        sleep(.5)
        pico_led.off()
        sleep(.5)
        cc+=1
        if cc>10:
            machine.reset()
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    for ii in range(4):
        pico_led.on()
        sleep(.1)
        pico_led.off()
        sleep(.1)
    
    return ip

def connectMQTT(ip):
    client = MQTTClient(\
        client_id=b"raspberrypi_picow_"+str(ip),
        server=b"192.168.188.50",
        port=1883,
        keepalive=7200,
        ssl=False,
        )

    client.connect()
    return client

def publish(client, topic, value):
    print(topic)
    print(value)
    client.publish(topic, value)
    print("publish Done")






