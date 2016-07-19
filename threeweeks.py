#!/usr/bin/python3
"""
3weeks
"""
import eventlet

eventlet.monkey_patch()

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import flask_login
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = '3weeks!Secret!terceS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

async_mode=None #None, threading, eventlet, or gevent
socketio = SocketIO(app, async_mode=async_mode)
socketio = SocketIO(app)
thread = None

db = SQLAlchemy(app)


"""
User for Authentication
"""

class User(flask_login.UserMixin):
    """
    A wrapper class for UserMixin
    """
    def __init__(self, user_id, username, subject_location, subject_password, subject_email, subject_group, subject_event):
        self.id = user_id
        self.username = username
        self.location = subject_location
        self.password = subject_password
        self.email = subject_email
        self.groups = subject_group
        self.events = subject_event

@login_manager.user_loader
def user_loader(user_id):
    login_user = get_employee(user_id)
    if login_user is not None:
        subject_group =  get_groups_for_employee(login_user.username)
        subject_event = get_events_for_employee(login_user.username)
        user = User(login_user.id, login_user.username, login_user.location, login_user.password, login_user.email, subject_group, subject_event)
        return user

"""

DATABASE STUFF

"""
#Association Table for Employees to Groups
memberships = db.Table(
    'memberships',
    db.Column('emp_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('grp_id', db.Integer, db.ForeignKey('group.id')))

#Employee Table
class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    location = db.Column(db.String(120), unique=False)
    password = db.Column(db.String(120), unique=False)

    def __init__(self, username, location, password, email):
        self.username = username
        self.location = location
        self.password = password
        self.email = email

    def __repr__(self):
        return '<Employee %r>' % self.username
#Group Table
class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(120), unique = False, nullable=True)
    members = db.relationship("Employee", secondary=memberships)
    events =  db.relationship("Event", backref='group')

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Group %r>' % self.name

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(120), unique = False, nullable=True)
    date = db.Column(db.DateTime)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    grp_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    creator = db.Column(db.String(80), unique=False)

    def __init__(self, name, description, date, latitude, longitude, grp_id, creator):
        self.name = name
        self.description = description
        self.date = date
        self.latitude = latitude
        self.longitude = longitude
        grp_id = grp_id
        self.creator = creator

    def __repr__(self):
        return '<Event %r>' % self.name

def serialize(self):
    return {
        'name': self.name,
        'description': self.description,
        'date': str(self.date),
        'lat': self.latitude,
        'lng': self.longitude,
        'grpId': self.grp_id,
        'creator': self.creator
    }

#DB FUNCTIONS
"""
Employee DB Functions
"""
def create_database():
    db.create_all()
    create_group("All Interns", "Group for all Viasat interns.")
    create_group("Tempe", "Group for all Viasat interns located in Tempe, AZ.")
    create_group("Carlsbad", "Group for all ViaSat interns located in Carlsbad, CA.")
    create_employee('Tempe1', 'Tempe', 'pass', 'riyan.setiadji@viasat.com')
    create_employee('Tempe2', 'Tempe', 'pass', 'ian.kane@viasat.com')
    create_employee('Carlsbad1', 'Carlsbad', 'pass', 'anthony.black@viasat.com')
    create_employee('TestDelete1', 'Carlsbad', 'pass', 'test123@viasat.com')
    add_emp_to_group('Tempe1', 'Carlsbad')
    create_event('Hackathon', "Let's hack all the things!", "2017-01-01 00:00", 33.127341, -117.265361, 3, "Ian")
    create_event('Submarine Party', "Getting there is the challenge...", "2017-01-01 00:00", 32.127341, -118.265361, 3, "ian")
    create_event('Party in Baja', "Not the Mountain Dew drink...", "2017-01-01 00:00", 32.127341, -116.265361, 3, "Ian")
    create_event('Metro Center Shopping', "Toys R Us, Best Buy, all you need.", "2017-01-01 00:00", 34.127341, -118.265361, 3, "Ian")
    create_event('Nature Hike', "Checking out the Joshua trees.", "2017-01-01 00:00", 34.127341, -116.265361, 3, "Ian")

def create_employee(name, location, password, email):
    new_emp = Employee(name, location, password, email)
    db.session.add(new_emp)
    db.session.commit()
    add_emp_to_group(new_emp.username, "All Interns")
    add_emp_to_group(new_emp.username, new_emp.location)

def get_employee(user_id):
    return Employee.query.filter_by(id=user_id).first()

def user_login(username, password):
    return Employee.query.filter_by(username=username, password=password).first()

def get_creator_of_event(id):
    return Event.query.filter_by(id=id).first().creator

"""
Group DB Functions
"""
def create_group(name, description=""):
    group_exists = Group.query.filter_by(name=name).first()
    if group_exists is None:
        new_group = Group(name, description)
        db.session.add(new_group)
        db.session.commit()
        return True
    else:
        return False

def create_event(name, description, date, latitude, longitude, grp_id, creator):
    g = Group.query.filter_by(id=grp_id).first()
    if g is None:
        return False
    else:
        formatted_date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        ev = Event(name, description, formatted_date, latitude, longitude, grp_id, creator)
        db.session.add(ev)
        g.events.append(ev)
        db.session.add(g)
        db.session.commit()
        return True

def delete_event(event_id):
    ev = Event.query.filter_by(id=event_id).first()
    if ev is None:
        return False
    else:
        db.session.delete(ev)
        db.session.commit()
        return True

def remove_user_from_group(user_id, group_id):
    user = Employee.query.get(user_id)
    group = Group.query.get(group_id)
    if user is None or group is None:
        return False
    else:
        group.members.remove(user)
        db.session.commit()
        return True

def add_emp_to_group(emp_name, grp_name):
    e = Employee.query.filter_by(username=emp_name).first()
    g = Group.query.filter_by(name=grp_name).first()
    if g is None or e is None:
        return False
    else:
        g.members.append(e)
        db.session.add(g)
        db.session.commit()
        return True
def get_group_members(grp_name):
    g = Group.query.filter_by(name=grp_name).first()
    result = []
    for member in g.members:
        result.append(member.username)
    return result

def get_groups_for_employee(username):
    return Group.query.filter(Group.members.any(username=username)).all()

def get_events_for_employee(username):
    g = Group.query.filter(Group.members.any(username=username)).all()
    ev = []
    if g is not None:
        for group in g:
            ev += group.events
    return list(set(ev))

"""
Routes
"""
@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        result = user_login(username, password)
        if result is not None:
            users_group = get_groups_for_employee(result.username)
            users_event = get_events_for_employee(result.username)
            user = User(result.id, result.username, result.location, result.password, result.email, users_group, users_event)
            flask_login.login_user(user)
            return redirect(url_for('home'))
    return render_template('login-paper.html')

@app.route('/welcome')
@app.route('/home')
@flask_login.login_required
def home():
    username = flask_login.current_user.username
    all_events = get_events_for_employee(username)
    all_events.sort(key=lambda x: x.date)
    return render_template('welcome.html', username = username, all_events=all_events, groups=flask_login.current_user.groups, events=flask_login.current_user.events)


@app.route("/create_group", methods=['GET', 'POST'])
@flask_login.login_required
def start_group():
    if request.method == 'POST':
        new_groupname = request.form['groupName']
        group_description = request.form['description']
        current_user = flask_login.current_user.username
        if not new_groupname:
            return redirect(url_for('start_group'))
        result = create_group(new_groupname, group_description)
        if result:
            result2 = add_emp_to_group(current_user, new_groupname)
            return redirect(url_for('start_group'))
        else:
            return render_template("create-group.html")
    else:
        return render_template("create-group.html", groups=flask_login.current_user.groups)

@app.route('/createEvent', methods=['GET', 'POST'])
@flask_login.login_required
def schedule_event():
    if request.method == 'GET':
        usernameOfEmployee = flask_login.current_user.username
        all_groups = get_groups_for_employee(usernameOfEmployee)
        return render_template('create-event.html', all_groups = all_groups, groups=flask_login.current_user.groups, events=flask_login.current_user.events)
    else:
        try:
            content = request.json
            lat = content['latitude']
            lng = content['longitude']
            name = content['name']
            group_id = content['groupId']
            description = content['description']
            date = content['date']
            date = date.replace("T"," ")
            creator = flask_login.current_user.username
            create_event(name,description,date,lat,lng,group_id, creator)
            return jsonify(status="success")
        except:
            return jsonify(status="error")

@app.route('/getEvents', methods=['GET', 'POST'])
@flask_login.login_required
def get_events():
    username = request.json['username']
    all_events = get_events_for_employee(username)
    json_events = []
    for event in all_events:
        json_events.append(serialize(event))
    result = Response(
        response=json.dumps(json_events),
        status=200,
        mimetype="application/json")
    return result

@app.route('/removeEvent', methods=['GET', 'POST'])
@flask_login.login_required
def remove_event():
    event_id = request.json['eventId']
    creator_of_event = get_creator_of_event(event_id)
    if creator_of_event != flask_login.current_user.username:
        return jsonify(status="error")
    else:
        delete_event(event_id)
        return jsonify(status="success")

@app.route('/leaveGroup', methods=['GET', 'POST'])
@flask_login.login_required
def leave_group():
    user_id = request.json['userId']
    group_id = request.json['groupId']
    username = request.json['username']
    if username != flask_login.current_user.username:
        return jsonify(status="error")
    else:
        remove_user_from_group(user_id, group_id)
        return jsonify(status="success")
"""
Chat
"""

@app.route('/group/<group_name>')
def group(group_name):
    global thread
    current_user = flask_login.current_user.username
    users_group = get_groups_for_employee(current_user)
    group = [group for group in users_group if group.name == group_name]
    group_object = group[0]

    if thread is None:
        pass
    return render_template('group.html',
        async_mode=socketio.async_mode,
        group_object=group_object,
        group_name=group_name,
        groups=flask_login.current_user.groups, #For Navigation
        username=flask_login.current_user.username,
        userid=flask_login.current_user.id)

@app.route('/addUser', methods=['GET', 'POST'])
@flask_login.login_required
def add_user():
    group_name = request.json['groupname']
    username = request.json['username']
    result = add_emp_to_group(username, group_name)
    return jsonify(status="success")

@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'user': flask_login.current_user.username})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'user': flask_login.current_user.username})


@socketio.on('close room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'user': flask_login.current_user.username},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'user': flask_login.current_user.username},
         room=message['room'])


@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'user': flask_login.current_user.username})
    disconnect()


@socketio.on('my ping', namespace='/test')
def ping_pong():
    emit('my pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'user': flask_login.current_user.username})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

@app.template_test()
def creator(event_id):
    """
    Makes a Jinja test to see if the media is a SVG
    """
    if get_creator_of_event(event_id) == flask_login.current_user.username:
        return True
    return False

if __name__ == '__main__':
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database()
    socketio.run(app, debug=True)
