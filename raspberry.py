import RPi.GPIO as GPIO
import sqlite3
from datetime import datetime

#house alarm globals
buzzerpin = 7

def setup():
    global alarm_armed
    global alarm_active

    alarm_armed = False
    alarm_active = False

    #setup the buzzer
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzzerpin,GPIO.OUT)
    GPIO.output(buzzerpin, GPIO.LOW)

    #setup the sensors as found in the db
    setup_sensors()

    return

def arm():
    global alarm_armed
    global alarm_active

    if alarm_armed:
        alarm_armed = False
        alarm_active = False
        GPIO.output(buzzerpin, GPIO.LOW)
    else:
        alarm_armed = True
        alarm_active = False
        GPIO.output(buzzerpin, GPIO.LOW)

        #check all sensor inputs. If one is active and the alarm would be armed alarm will activate
        alarm_db = sqlite3.connect('db.sqlite3')
        cur = alarm_db.cursor()
        cur.execute("""SELECT id, GPIO_pin FROM sensors""")
        recs = cur.fetchall()

        for rec in recs:
            sensor_id = rec[0]
            pin = rec[1]
            if(GPIO.input(pin)):
                sensor_triggered(pin)

        alarm_db.close()
    return

def get_armed():
    global alarm_armed
    return alarm_armed

def get_active():
    global alarm_active
    return alarm_active

def add_sensor(name, pin):
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """INSERT INTO sensors(name, GPIO_pin) VALUES ('{name}',{pin})""".format(name=name,pin=pin)

    cur.execute(cmd)

    alarm_db.commit()

    GPIO.setup(int(pin),GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(int(pin), GPIO.RISING, callback=sensor_triggered, bouncetime=100)

    return

def add_room(name):
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """INSERT INTO rooms(name) VALUES ('{name}')""".format(name=name)

    cur.execute(cmd)

    alarm_db.commit()

    return

def add_config(sensor_id, room_id):
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """INSERT INTO config(sensor_id, room_id) VALUES ({sensor_id},{room_id})""".format(sensor_id=sensor_id, room_id=room_id)

    cur.execute(cmd)

    alarm_db.commit()

    return

def remove_sensor(id):
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """DELETE FROM sensors WHERE id={id}""".format(id=id)

    cur.execute(cmd)

    alarm_db.commit()

    return

def remove_room(id):
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """DELETE FROM rooms WHERE id={id}""".format(id=id)

    cur.execute(cmd)

    alarm_db.commit()

    return

def remove_config(id):
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """DELETE FROM config WHERE id={id}""".format(id=id)

    cur.execute(cmd)

    alarm_db.commit()

    return


def get_config():
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """SELECT id, sensor_id, room_id FROM config"""

    cur.execute(cmd)

    rec = cur.fetchall()

    list = []

    for r in rec:
        item = {'id':r[0], 'sensor_id':r[1], 'room_id':r[2]}
        list.append(item)

    return list

def get_rooms():
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """SELECT id, name FROM rooms"""

    cur.execute(cmd)

    rec = cur.fetchall()

    list = []

    for r in rec:
        item = {'id':r[0], 'name':r[1]}
        list.append(item)

    return list

def get_sensors():
    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """SELECT id, name, GPIO_pin FROM sensors"""

    cur.execute(cmd)

    rec = cur.fetchall()

    list = []

    for r in rec:
        item = {'id':r[0], 'name':r[1], 'GPIO_pin':r[2]}
        list.append(item)

    return list

def list_events(count):

    alarm_db = sqlite3.connect('db.sqlite3')

    cur = alarm_db.cursor()

    cmd = """SELECT timestamp, sensor_id, room_id, type, alarm FROM alarms ORDER BY timestamp DESC LIMIT {count}""".format(count=count)

    cur.execute(cmd)

    rec = cur.fetchall()

    list = []

    for r in rec:
        item = {'timestamp':r[0], 'sensor_id':r[1], 'room_id':r[2], 'type':r[3], 'alarm':r[4]}
        list.append(item)

    return list

def sensor_triggered(pin):

    global alarm_armed
    global alarm_active

    if alarm_armed:

        alarm_db = sqlite3.connect('db.sqlite3')

        #write event to db
        cur = alarm_db.cursor()

        cmd = """SELECT room_id FROM config WHERE sensor_id = (SELECT id FROM sensors WHERE GPIO_pin = {pinid})""".format(pinid=pin)
        cur.execute(cmd)
        roomid = cur.fetchone()[0]

        cmd = """SELECT id, name FROM sensors WHERE GPIO_pin = {pinid}""".format(pinid=pin)
        cur.execute(cmd)
        rec = cur.fetchone()
        sensorid = rec[0]
        sensorname = rec[1]

        timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S.%f")

        cmd = """INSERT INTO alarms(timestamp, sensor_id, room_id, type, alarm) VALUES ('{timestamp}',{sensorid},{roomid},'alarm','sensor triggered')""".format(timestamp=timestamp, sensorid = sensorid, roomid=roomid)

        cur.execute(cmd)

        alarm_db.commit()

        alarm_active = True
        GPIO.output(buzzerpin, GPIO.HIGH)

        alarm_db.close()

    return

def setup_sensors():

    alarm_db = sqlite3.connect('db.sqlite3')
    cur = alarm_db.cursor()
    cur.execute("""SELECT GPIO_pin FROM sensors""")
    pins = cur.fetchall()

    GPIO.setmode(GPIO.BOARD)

    for pin in pins:
        GPIO.setup(int(pin[0]),GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(int(pin[0]), GPIO.RISING, callback=sensor_triggered, bouncetime=100)

    alarm_db.close()

    return
