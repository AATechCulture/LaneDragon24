import secrets 
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import bcrypt
from datetime import datetime
from flask_migrate import Migrate
import openai
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Cros%40ncat@localhost/homeless_support'
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'in_need' or 'volunteer'
    
    # Relationship for volunteer (one-to-many)
    volunteer_hours = db.relationship('VolunteerHour', backref='user', lazy=True)
    
    # Relationship for in-need users (one-to-many)
    shelter_references = db.relationship('ShelterReference', backref='user', lazy=True)

    def hash_password(self, password):
        salt = bcrypt.gensalt()  # Generate a random salt
        self.password = bcrypt.hashpw(password.encode(), salt).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())
    def is_active(self):
        return True  # or False based on whether the user is active or not

    def is_authenticated(self):
        return True  # Return True if the user is authenticated, typically handled by Flask-Login

    def is_anonymous(self):
        return False  # False because we do not use anonymous users in this case

    def get_id(self):
        return str(self.id)

class VolunteerHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours_contributed = db.Column(db.Integer, nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ShelterReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shelter_name = db.Column(db.String(100), nullable=False)
    advisory_service = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Shelter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    services = db.Column(db.String(300), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/profile')
@login_required
def profile():
    # Fetch the user's profile based on their user type
    if current_user.user_type == 'in_need':
        shelter_references = ShelterReference.query.filter_by(user_id=current_user.id).all()
        return render_template('profile_in_need.html', shelter_references=shelter_references, user=current_user)
    
    elif current_user.user_type == 'volunteer':
        volunteer_hours = VolunteerHour.query.filter_by(user_id=current_user.id).all()
        return render_template('profile_volunteer.html', volunteer_hours=volunteer_hours, user=current_user)
    
    else:
        flash("Invalid user type", "danger")
        return redirect(url_for('home'))



@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.datetime.now().year)

@app.route('/resources')
def resources():
    shelters = Shelter.query.all()
    return render_template('resources.html', shelters=shelters)

@app.route('/ai-advisor', methods=['GET', 'POST'])
def ai_advisor():
    # Initialize session if not already initialized
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": "You are a helpful assistant for people living in shelters, offering advice, resources, and support."}]

    if request.method == 'POST':
        location = request.form['location']
        needs = request.form['needs']
        
        # Append user input to session for context
        session['messages'].append({"role": "user", "content": f"Help with shelter options in {location} for needs: {needs}"})

        # Call OpenAI API to generate the scenario based on user input
        try:
            chat_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=session['messages']
            )
            scenario = chat_response.choices[0].message['content']

            # Call OpenAI API to generate an image based on the scenario
            image_response = openai.Image.create(
                model="dall-e-3",
                prompt=f"Generate an image based on: {scenario}",
                size="1024x1024"
            )
            image_url = image_response.data[0].url

            # Add the AI's response to the session
            session['messages'].append({"role": "assistant", "content": scenario})

            # Example recommended shelters (replace with real data from your database)
            recommended_shelter = {
                "name": "Hope Shelter",
                "address": "123 Main St, Springfield",
                "capacity": 50,
                "services": "Food, Clothing, Temporary Shelter"
            }

            return render_template('ai_advisor.html', scenario=scenario, image_url=image_url, recommended=recommended_shelter)

        except Exception as e:
            assistant_message = "Sorry, there was an error processing your request. Please try again."
            session['messages'].append({"role": "assistant", "content": assistant_message})
            return render_template('ai_advisor.html', error_message="Error processing your request. Please try again.")

    return render_template('ai_advisor.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        # Check if the email is already taken
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, user_type=user_type)
        new_user.hash_password(password)  # Hash and set the password
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('profile'))  # Redirect to the profile page after login
        flash("Invalid credentials", "danger")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/add_shelter', methods=['GET', 'POST'])
@login_required
def add_shelter():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        capacity = request.form.get('capacity')
        services = request.form.get('services')

        new_shelter = Shelter(name=name, address=address, capacity=capacity, services=services)
        db.session.add(new_shelter)
        db.session.commit()
        flash("Shelter added successfully!", "success")
        return redirect(url_for('resources'))

    return render_template('add_shelter.html')
@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    shelters = Shelter.query.all()
    if request.method == 'POST':
        # Handle the form submission here if needed
        pass
    return render_template('volunteer.html', shelters=shelters, current_year=datetime.now().year)

@app.route('/volunteer-signup', methods=['POST'])
def volunteer_signup():
    name = request.form.get('name')
    email = request.form.get('email')
    shelter_id = request.form.get('shelter')
    task = request.form.get('task')
    
    # You can store this information in the database or process it as needed
    selected_shelter = Shelter.query.get(shelter_id)
    flash(f"Thank you, {name}, for signing up to help at {selected_shelter.name} with {task}!", "success")
    return redirect(url_for('volunteer'))

@app.route('/donate', methods=['POST'])
def donate():
    shelter_id = request.form.get('donation_shelter')
    amount = request.form.get('amount')
    selected_shelter = Shelter.query.get(shelter_id)
    
    # Here, you would integrate with a payment processor like PayPal or Stripe
    flash(f"Thank you for your generous donation of ${amount} to {selected_shelter.name}!", "success")
    return redirect(url_for('volunteer'))

if __name__ == "__main__":
    # Create tables before starting the app
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    app.run(debug=True)
