from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_security import login_required, roles_required, roles_accepted, current_user

from app import db

from raspberry import arm, get_armed, get_active, setup_sensors, list_events, get_config, get_rooms, get_sensors, add_sensor, add_room, add_config, remove_sensor, remove_room, remove_config

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('main.html')
    else:
        return render_template('login.html')

@main.route('/main/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin','basicuser')
def appmain(action):

    if request.method == 'POST':
        if action=='alarms':
            strCount = request.form.get('count')
            if strCount.strip().isdigit():
                count = int(strCount)
            else:
                count = int(0)

            return redirect(url_for('main.listevents', count=count))
        elif action=='arm':
            arm()
            return render_template('main.html')
        else:
            return render_template('main.html')
    else:
        return render_template('main.html')

@main.route('/config/<action>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin','basicuser')
def config(action):

    if request.method == 'POST':
        if action=='addsensor':
            name = request.form.get('name')
            GPIO_pin = int(request.form.get('GPIO_pin'))
            add_sensor(name=name, pin=GPIO_pin)
            return redirect(url_for('main.config', action='main'))

        elif action=='addroom':
            name = request.form.get('name')
            add_room(name=name)
            return redirect(url_for('main.config', action='main'))

        elif action=='addconfig':
            sensor_id = request.form.get('sensor_id')
            room_id = request.form.get('room_id')
            add_config(sensor_id=sensor_id, room_id=room_id)
            return redirect(url_for('main.config', action='main'))

        elif action=='removesensor':
            id = request.form.get('id')
            remove_sensor(id)
            return redirect(url_for('main.config', action='main'))

        elif action=='removeroom':
            id = request.form.get('id')
            remove_room(id)
            return redirect(url_for('main.config', action='main'))

        elif action=='removeconfig':
            id = request.form.get('id')
            remove_config(id)
            return redirect(url_for('main.config', action='main'))

        else:
            return redirect(url_for('main.config', action='main'))
    else:

        config = get_config()
        sensors = get_sensors()
        rooms = get_rooms()

        return render_template('config.html', config=config, sensors=sensors,rooms=rooms)

@main.route('/listevents')
@login_required
@roles_accepted('admin','basicuser')
def listevents():

    count = request.args.get('count')

    if count != None:
        #get list of events from db
        list = list_events(count)
    else:
        list = []

    #put into json list
    return render_template('alarms.html', alarms=list)

@main.route('/api/getstate')
@login_required
@roles_accepted('admin','basicuser')
def getstate():

    armed = get_armed()
    active = get_active()

    ret = {'armed': armed, 'active': active}

    return jsonify(ret)
