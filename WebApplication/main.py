from flask import Flask, request, render_template, send_file, jsonify,  redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs1.db'  # SQLite database for logs1
app.config['SQLALCHEMY_BINDS'] = {
    'logs2': 'sqlite:///logs2.db'  # SQLite database for logs2
}

db = SQLAlchemy(app)

class Log1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_detected = db.Column(db.String(50))
    photo_capture = db.Column(db.String(50))
    image_name = db.Column(db.String(100))
    time = db.Column(db.String(50))


class Log2(db.Model):
    __bind_key__ = 'logs2'
    id = db.Column(db.Integer, primary_key=True)
    object_detected = db.Column(db.String(50))
    photo_capture = db.Column(db.String(50))
    image_name = db.Column(db.String(100))
    time = db.Column(db.String(50))


@app.route('/logs1', methods=['POST', 'GET'])
def handle_logs1():
    if request.method == 'POST':
        data = request.get_json()
        object_detected = data['object_detected']
        photo_capture = data['photo_capture']
        image_name = data['image_name']
        time = data['time']

        log = Log1(object_detected=object_detected, photo_capture=photo_capture, image_name=image_name, time=time)
        db.session.add(log)
        db.session.commit()

        return 'Log created successfully'
    elif request.method == 'GET':
        logs = Log1.query.all()

        logs_list = []
        for log in logs:
            log_dict = {
                'id': log.id,
                'object_detected': log.object_detected,
                'photo_capture': log.photo_capture,
                'image_name': log.image_name,
                'time': log.time
            }
            logs_list.append(log_dict)

        return jsonify({'logs': logs_list})


@app.route('/logs2', methods=['POST', 'GET'])
def handle_logs2():
    if request.method == 'POST':
        data = request.get_json()
        object_detected = data['object_detected']
        photo_capture = data['photo_capture']
        image_name = data['image_name']
        time = data['time']

        log = Log2(object_detected=object_detected, photo_capture=photo_capture, image_name=image_name, time=time)
        db.session.add(log)
        db.session.commit()

        return 'Log created successfully'
    elif request.method == 'GET':

        logs = Log2.query.all()

        logs_list = []
        for log in logs:
            log_dict = {
                'id': log.id,
                'object_detected': log.object_detected,
                'photo_capture': log.photo_capture,
                'image_name': log.image_name,
                'time': log.time
            }
            logs_list.append(log_dict)

        return jsonify({'logs': logs_list})

class User:
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

# Set up the login manager to load the user
@login_manager.user_loader
def load_user(username):
    # Replace this with your logic to load the user from your data store
    if username == 'admin':
        return User(username)
    return None

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate the username and password
        if username == 'admin' and password == 'admin':
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')
@app.route('/')
@login_required
def index():
    return render_template('index.html')

class Image:
    def __init__(self, filename, name, size, modified):
        self.filename = filename
        self.name = name
        self.size = size
        self.modified = modified

@app.route('/gallery')
@login_required
def gallery():
    images = []
    folder_path = '/home/pi/Pictures/LoRaComm_Imgs'  # Update with your image folder path

    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            file_path = os.path.join(folder_path, filename)
            size = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)

            image = {
                'name': filename,
                'size': size,
                'modified_time': modified_time
            }
            images.append(image)

    return render_template('gallery.html', images=images)

@app.route('/images/<path:image_path>')
def get_image(image_path):
    folder_path = '/home/pi/Pictures/LoRaComm_Imgs'  # Update with your image folder path
    file_path = os.path.join(folder_path, image_path)
    return send_file(file_path)

@app.route('/gallery2')
@login_required
def gallery2():
    images = []
    folder_path = '/home/pi/Pictures/LoRaComm_Imgs/'  # Update with your image folder path

    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            file_path = os.path.join(folder_path, filename)
            size = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)

            image = {
                'name': filename,
                'size': size,
                'modified_time': modified_time
            }
            images.append(image)

    return render_template('gallery2.html', images=images)

@app.route('/images/<path:image_path>')
def get_image2(image_path):
    folder_path = '/home/pi/Pictures/LoRaComm_Imgs/'  # Update with your image folder path
    file_path = os.path.join(folder_path, image_path)
    return send_file(file_path)

@app.route('/trigger', methods=['POST'])
def trigger():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"Triggered/{current_time}\n"

    try:
        with open('trigger.log', 'w') as file:
            file.write(log_message)
        return 'Triggered successfully'
    except Exception as e:
        return f"An error occurred: {str(e)}"

def initialize_database():
    with app.app_context():
        db.create_all()

def create_trigger_log_file():
    if not os.path.isfile('trigger.log'):
        try:
            with open('trigger.log', 'w') as file:
                file.write()
            print("Created trigger.log file")
        except Exception as e:
            print(f"Failed to create trigger.log file: {str(e)}")


if __name__ == '__main__':
    initialize_database()
    create_trigger_log_file()
#    app.run(host='0.0.0.0',port=5100)
