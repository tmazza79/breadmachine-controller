import time
from mqtt_utils import *
from sync_utils import *
from machine import Pin, WDT
import network
import gc

# --- GPIO ---
BUTTONS = {
    "menu":       Pin(6, Pin.OUT),
    "loaf_size":  Pin(5, Pin.OUT),
    "color":      Pin(1, Pin.OUT),
    "minus":      Pin(3, Pin.OUT),
    "plus":       Pin(2, Pin.OUT),
    "start_stop": Pin(0, Pin.OUT),
}

def press(name, duration_ms=150):
    BUTTONS[name].on()
    time.sleep_ms(duration_ms)
    BUTTONS[name].off()
    time.sleep_ms(300)  # debounce inter-press

def select_program(n):
    """Preme MENU n volte per arrivare al programma n."""
    for _ in range(n-1):
        press("menu")

def select_loaf(target="1000g"):
    """Cicla LOAF SIZE fino al peso desiderato (750→1000→1250→750…)."""
    sizes = ["1250g", "750g", "1000g"]
    for _ in range(sizes.index(target)):
        press("loaf_size")

def select_color(target="medium"):
    """Cicla COLOR: lower→medium→dark→rapid."""
    colors = ["medium", "dark", "rapid", "lower"]
    for _ in range(colors.index(target)):
        press("color")

def select_delay(delay):
    for _ in range(int(delay/10)+1):
        press("plus")

'''
def select_delay(delay):
    delay = int(delay)
    programs_5_minutes = [1,2,3,7,9]
    if program in programs_5_minutes:
        delay+=4
    for _ in range(int(delay/10)+1):
        press("plus")

cmd = "start:3:1000g:dark"
cmd = "start:7::"
cmd = "stop"
'''

# --- MQTT ---
def on_message(topic, msg):
    print((topic, msg))
    cmd = msg.decode().lower()
    print(cmd)
    if cmd.startswith("start:"):
        _, prog, loaf, color, delay = cmd.split(":")
        print(prog)
        if prog:
            select_program(int(prog))
        print(loaf)
        if loaf:
            select_loaf(loaf)
        print(color)
        if color:
            select_color(color)
        print(delay)
        if delay:
            select_delay(delay,int(prog))
        press("start_stop")

    elif cmd == "stop":
        press("start_stop", duration_ms=2000)


wlan = network.WLAN(network.STA_IF)

ip = connect()
client = connectMQTT(81)
client.set_callback(on_message)
print(client)
sync_time()

client.connect()
client.subscribe(b'breadmachine/cmd')  # ← once, outside the loop

sleep(1)

wdt = WDT(timeout=8000)  # reset se non viene toccato entro 30s
c = 0
while True:
    wdt.feed()

    try:
        if not wlan.isconnected():
            raise Exception('WiFi perso')
        client.check_msg()
    except Exception as e:
        print('Errore:', e)
        sleep(1)
        try:
            try:
                client.disconnect()
            except:
                pass
            gc.collect()
            ip = connect()
            client = connectMQTT(81)
            client.set_callback(on_message)
            client.connect()
            client.subscribe(b'breadmachine/cmd')
            print('Riconnesso')
        except Exception as e2:
            print('Riconnessione fallita:', e2)
            time.sleep(2)
            machine.reset()
            # il watchdog resetterà il Pico se questo si ripete

    sleep(.5)
    c += 1
    if c % 100 == 0:
        c = 1
        #year, month, day, hour, minute, second = get_current_time()
        dt = rtc.datetime()
        TIMEZONE_OFFSET = get_timezone_offset(dt[0], dt[1], dt[2], dt[4])
        hour = (dt[4] + TIMEZONE_OFFSET) % 24
        minute = dt[5]
        if hour == 3 and minute == 10:
            print('reset')
            sleep(1)
            machine.reset()

