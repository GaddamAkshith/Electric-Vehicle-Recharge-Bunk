from flask import Flask, render_template, redirect, url_for, session, flash, get_flashed_messages
from flask_wtf import FlaskForm  
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import DataRequired, Email, ValidationError 
import bcrypt 
from flask_mysqldb import MySQL 

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Akshith@373'
app.config['MYSQL_DB'] = 'ev-user'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM loginusers WHERE email=%s", (field.data,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            raise ValidationError('Email is already in use.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def index():
    print("Index route accessed")  # Add this line for debugging
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store data into database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO loginusers (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM loginusers WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash("Login failed. Please check your email and password.")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/index')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM loginusers WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('index.html', user=user)

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)





































# from flask import Flask, render_template, request, jsonify
# import datetime

# app = Flask(__name__)

# # Sample data for charging stations (to be replaced with a real database)
# charging_stations = [
#     {"id": 1, "name": "Station 1", "lat": 37.7749, "lng": -122.4194, "connector": "CCS", "price": 5},
#     {"id": 2, "name": "Station 2", "lat": 37.7849, "lng": -122.4294, "connector": "CHAdeMO", "price": 7},
# ]

# @app.route('/')
# def index():
#     return render_template('index.html')

# # API for providing charging station data
# @app.route('/api/stations')
# def stations():
#     return jsonify(charging_stations)

# # Handle slot booking requests
# @app.route('/book-slot', methods=['POST'])
# def book_slot():
#     station = request.form['station']
#     date = request.form['date']
#     time = request.form['time']
    
#     # Logic to save the booking information in the database goes here
    
#     return f'Slot booked at {station} on {date} at {time}!'

# if __name__ == '__main__':
#     app.run(debug=True)