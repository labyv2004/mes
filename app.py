from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'kabachok'  # Замените на ваш секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_online = db.Column(db.Boolean, default=False)  # Поле для отслеживания состояния

# Модель сообщения
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)

# Создание базы данных
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if User.query.filter_by(username=username).first() is not None:
        return "Пользователь с таким именем уже существует!", 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return '', 200  # Успешная регистрация без сообщения

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password, password):
        return "Неверные имя пользователя или пароль!", 400

    session['username'] = username
    user.is_online = True  # Устанавливаем пользователя в "В сети"
    db.session.commit()
    return '', 200  # Успешный вход без сообщения

@app.route('/logout', methods=['POST'])
def logout():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_online = False  # Устанавливаем пользователя в "Вне сети"
            db.session.commit()
        session.pop('username', None)  # Удаляем пользователя из сессии
    return '', 200  # Успешный выход без сообщения

@app.route('/send_message', methods=['POST'])
def send_message():
    username = session.get('username')
    content = request.form.get('message')

    if username and content:
        new_message = Message(username=username, content=content)
        db.session.add(new_message)
        db.session.commit()
        return '', 200  # Успешная отправка сообщения
    return "Вы не авторизованы!", 403  # Ошибка, если пользователь не авторизован

@app.route('/get_messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{'username': msg.username, 'content': msg.content} for msg in messages])

@app.route('/get_users_status', methods=['GET'])
def get_users_status():
    users = User.query.all()
    user_status = [{'username': user.username, 'is_online': user.is_online} for user in users]
    return jsonify(user_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1488, debug=True)