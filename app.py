from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from functools import wraps
from wtforms import StringField, PasswordField, SubmitField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import bleach
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    end_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    expired = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_type = db.Column(db.String(20), nullable=False, default='single')

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Todo', backref='user', lazy=True)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(message='Password is required.'),
        validators.Length(min=8, message='Password must be at least 8 characters long.'),
        validators.EqualTo('confirm_password', message='Passwords must match.'),
        validators.Regexp(
            regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).+$',
            message='Password must contain at least one uppercase letter, one lowercase letter, and one symbol.'
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[validators.DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise validators.ValidationError('Username already exists. Please choose a different username.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise validators.ValidationError('Email already exists. Please choose a different email.')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_id'] = user.id
            flash('You have been logged in successfully', 'success')
            return redirect(url_for('home'))
        else:
            form.username.errors.append('Invalid username or password.')
    return render_template('login.html', form=form)

def is_logged_in():
    return 'user_id' in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_logged_in():
    return dict(is_logged_in=is_logged_in, is_admin=is_admin)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = bleach.clean(form.username.data.strip())
        email = bleach.clean(form.email.data.strip())
        password = form.password.data

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                form.username.errors.append('Username already exists. Please choose a different username.')
            if existing_user.email == email:
                form.email.errors.append('Email already exists. Please choose a different email.')
            return render_template('signup.html', form=form)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Your account has been created! You are now logged in.', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

def check_task_owner(task):
    if task.user_id != current_user.id:
        flash('You are not authorized to perform this action on this task.', 'error')
        return redirect(url_for('home'))

@app.route('/', methods=["GET", "POST"])
@login_required
def home():
    user = current_user

    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        todo = Todo(title=user_title, desc=user_desc, user_id=user.id)
        db.session.add(todo)
        db.session.commit()

        all_items = Todo.query.filter_by(user_id=user.id).all()
        return render_template("index.html", all_todos=all_items)

    all_items = Todo.query.filter_by(user_id=user.id).all()
    return render_template("index.html", all_todos=all_items, fc_event_class='fc-event')

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    user = current_user
    title = request.form.get('title')
    desc = request.form.get('desc')
    task_type = request.form.get('taskType')

    if title:
        new_task = Todo(title=title, desc=desc, user_id=user.id, task_type=task_type)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully', 'success')
        return jsonify(sno=new_task.sno, title=new_task.title, desc=new_task.desc, task_type=new_task.task_type)
    else:
        flash('Title is required', 'error')
        return jsonify(error='Title is required'), 400

@app.route('/update_task_position', methods=['POST'])
@login_required
def update_task_position():
    task_id = request.form.get('taskId')
    start_date_iso = request.form.get('startDate')
    end_date_iso = request.form.get('endDate')

    start_date = datetime.fromisoformat(start_date_iso)
    end_date = datetime.fromisoformat(end_date_iso)

    task = Todo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('You are not authorized to update this task.', 'error')
        return jsonify(error='Unauthorized'), 403

    task.date_created = start_date
    task.end_date = end_date

    db.session.commit()

    return jsonify(message='Task position and dates updated successfully.')

@app.route('/fetch_tasks')
@login_required
def fetch_tasks():
    user_id = current_user.id
    tasks = Todo.query.filter_by(user_id=user_id).all()

    events = []
    for task in tasks:
        if task.task_type == 'multi':
            event = {
                'id': task.sno,
                'title': task.title,
                'start': task.date_created.strftime('%Y-%m-%d'),
                'end': task.end_date.strftime('%Y-%m-%d') if task.end_date else None,
                'editable': True,
            }
        else:
            event = {
                'id': task.sno,
                'title': task.title,
                'start': task.date_created.isoformat(),
                'end': task.end_date.isoformat(),
                'editable': True,
            }
        events.append(event)

    return jsonify(events)

@app.route("/manage/<int:sno>", methods=["GET", "POST"])
@login_required
def manage_item(sno):
    item = Todo.query.get_or_404(sno)
    check_task_owner(item)

    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        item.title = user_title
        item.desc = user_desc
        db.session.commit()

        return redirect("/")

    return render_template("manage.html", todo=item)

@app.route('/delete/<int:sno>')
@login_required
def delete_item(sno):
    item = Todo.query.get_or_404(sno)
    check_task_owner(item)

    db.session.delete(item)
    db.session.commit()
    return redirect('/')

@app.route('/search', methods=["GET", "POST"])
@login_required
def search_item():
    search_query = request.args.get('query')
    if not search_query:
        flash('Please provide a search query', 'error')
        return redirect(url_for('home'))

    user_id = current_user.id
    result = Todo.query.filter(Todo.title == search_query, Todo.user_id == user_id).all()
    if not result:
        flash('No results found', 'info')

    return render_template('result.html', posts=result)

@app.route('/complete/<int:sno>', methods=["POST"])
@login_required
def complete_item(sno):
    item = Todo.query.get_or_404(sno)

    if item.user_id != current_user.id:
        flash('You are not authorized to complete this task.', 'error')
        return redirect(url_for('home'))

    item.completed = not item.completed
    db.session.commit()
    return redirect('/')

def is_admin():
    user = current_user

    if user.is_authenticated:
        return user.username == 'admin'
    return False

@app.route('/admin/users')
@login_required
def admin_users():
    if not is_admin():
        flash('Access denied. Only administrators can access this page.', 'error')
        return redirect(url_for('home'))

    all_users = User.query.all()
    return render_template('admin_users.html', users=all_users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not is_admin():
        flash('Access denied. Only administrators can perform this action.', 'error')
        return redirect(url_for('home'))

    user_to_delete = User.query.get_or_404(user_id)

    Todo.query.filter_by(user_id=user_to_delete.id).delete()

    db.session.delete(user_to_delete)
    db.session.commit()

    flash('User and associated tasks have been successfully deleted.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/profile')
@login_required
def profile():
    user = current_user
    all_tasks_count = Todo.query.filter_by(user_id=user.id).count()
    completed_tasks_count = Todo.query.filter_by(user_id=user.id, completed=True).count()
    incomplete_tasks_count = Todo.query.filter_by(user_id=user.id, completed=False).count()
    errors = session.pop('errors', None)
    success = session.pop('success', None)
    return render_template('profile.html', username=user.username,
                           all_tasks=all_tasks_count,
                           completed_tasks=completed_tasks_count,
                           incomplete_tasks=incomplete_tasks_count,
                           errors=errors,
                           success=success)

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    password = request.form.get('password')
    errors = []

    if not password or not check_password_hash(user.password, password):
        errors.append('Incorrect password. Account deletion failed.')
        session['errors'] = errors
        return redirect(url_for('profile'))

    Todo.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    logout_user()
    session['success'] = ['Your account has been successfully deleted.']
    return redirect(url_for('login'))

def check_current_password(user, password):
    return check_password_hash(user.password, password)

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    errors = []

    if not current_password or not new_password or not confirm_new_password:
        errors.append('All fields are required')
    else:
        user = current_user

        if not check_current_password(user, current_password):
            errors.append('Incorrect current password')
        if new_password != confirm_new_password:
            errors.append('New passwords do not match')
        if len(new_password) < 8:
            errors.append('New password must be at least 8 characters long')
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).+$', new_password):
            errors.append('New password must contain at least one uppercase letter, one lowercase letter, and one symbol')

        if not errors:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            session['success'] = ['Your password has been updated successfully']
            return redirect(url_for('profile'))

    session['errors'] = errors
    return redirect(url_for('profile'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=False, port=5000)
