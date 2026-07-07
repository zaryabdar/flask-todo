from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import (LoginManager, UserMixin, login_user,login_required, logout_user,current_user)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY']= ' Escapist '
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Login_manager = LoginManager()
Login_manager.init_app(app)
Login_manager.login_view = 'login'
Login_manager.login_message_category = 'warning'

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key = True )
    title = db.Column(db.String(200), nullable = False )
    Description = db.Column(db.String(500), nullable = False )
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)

    def __repr__(self) -> str:
        return f"{self.sno}-{self.title}"
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@Login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
    
        if existing_user: 
            flash('Username or email already taken.', 'danger')
            return redirect('/')
    
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account Created ! Please Login.','success')
        return redirect('/login')
    return render_template('signup.html', active_page="signup")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
 
        user = User.query.filter_by(username=username).first()
 
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect('/home')
 
        flash('Invalid username or password.', 'danger')
 
    return render_template('login.html', active_page="signup")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/home', methods = ['GET', 'POST'])
@login_required
def hello_world():
    if request.method == 'POST':
        title =request.form['title']
        desc =request.form['desc']
        todo = Todo(title=title, Description =desc, user_id = current_user.id)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.filter_by(user_id= current_user.id).all()
    return render_template('index.html',active_page="home", allTodo=allTodo)

@app.route('/about')
@login_required
def Products():
    return render_template('About.html', active_page="about")
@app.route('/update/<int:sno>', methods = ['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title =request.form['title']
        desc =request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.Description = desc
        db.session.add(todo)
        db.session.commit()
        return redirect('/home')
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo) 
@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/home')

if __name__ =="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)