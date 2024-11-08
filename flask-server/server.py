from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import pyodbc
import bcrypt


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = 'JzOPlDd9LG'


# Configure the database connection string for SQL Server
# Replace DRIVER={SQL Server};SERVER=YOUR_HOST;DATABASE=YOUR_DB;UID=YOUR_USER-ID;PWD=YOUR_PASSWORD
connection_string = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=4.240.110.36,1433;DATABASE=edztest;UID=sa;PWD=dDPD28QPqf;TrustServerCertificate=yes;'

def init_db():
    """ Initialize database tables for Coaches and Users if they do not already exist. """
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        # SQL commands to create Coaches and Users tables
        cursor.execute('''
              IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Coaches')
            CREATE TABLE Coaches (
                EmailAddress VARCHAR(100) PRIMARY KEY,
                FullName VARCHAR(100) NOT NULL,
                PasswordHash VARCHAR(255) NOT NULL,
                PhoneNumber BIGINT NOT NULL,
                Experience VARCHAR(250) NOT NULL,
                Specialization VARCHAR(50) NOT NULL,
                Qualifications VARCHAR(250) NOT NULL,
                Availability VARCHAR(50) NOT NULL,
                Location VARCHAR(100) NOT NULL,
                Gender VARCHAR(10) NOT NULL,
                LanguagesSpoken VARCHAR(100) NOT NULL,
                PreferredCoachingMethod VARCHAR(50) NOT NULL,
                TwitterLink VARCHAR(150),
                FacebookLink VARCHAR(150),
                SubscribeToNewsletter BIT NOT NULL,
                ReferralSource VARCHAR(50)
            );
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
            CREATE TABLE Users (
                EmailAddress VARCHAR(100) PRIMARY KEY,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                Username VARCHAR(50) NOT NULL UNIQUE,
                PasswordHash VARCHAR(255) NOT NULL,
                PhoneNumber BIGINT NOT NULL,
                Gender VARCHAR(10),
                DateOfBirth DATE,
                Address VARCHAR(100) NOT NULL,
                PreferredLanguage VARCHAR(100) NOT NULL,
                Occupation VARCHAR(20) NOT NULL,
                Nationality VARCHAR(20) NOT NULL
            );
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CoachSelection')
            CREATE TABLE CoachSelection (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                EmailAddress VARCHAR(100) NOT NULL,  -- User's Email
                CoachType VARCHAR(50) NOT NULL,
                CoachEmailAddress VARCHAR(100) NULL,
                CoachName VARCHAR(100) NULL,
                FOREIGN KEY (EmailAddress) REFERENCES Users(EmailAddress),
                FOREIGN KEY (CoachEmailAddress) REFERENCES Coaches(EmailAddress)
);
        ''')
        conn.commit()

@app.route('/register/coach', methods=['POST'])
def register_coach():
    # Endpoint to register a new coach, requiring all specified fields. 
    data = request.form
    required_fields = ['email', 'fullname', 'password', 'phone', 'experience', 'specialization', 'qualifications', 'availability', 'location', 'gender', 'languages', 'preferredMethod', 'twitter', 'facebook', 'referral']
    # Check for missing fields in the submitted form
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return render_template('error.html', error_message="Missing fields: " + ", ".join(missing_fields)), 400

    # Generate bcrypt password hash
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    subscribe_to_newsletter = 1 if data.get('newsletter') == 'on' else 0
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            # Insert new coach into the database
            cursor.execute("""
                INSERT INTO Coaches (EmailAddress, FullName, PasswordHash, PhoneNumber, Experience, Specialization,
                    Qualifications, Availability, Location, Gender, LanguagesSpoken, PreferredCoachingMethod,
                    TwitterLink, FacebookLink, SubscribeToNewsletter, ReferralSource) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data['email'], data['fullname'], password_hash, data['phone'], data['experience'], 
                data['specialization'], data['qualifications'], data['availability'], data['location'], 
                data['gender'], data['languages'], data['preferredMethod'], data['twitter'], data['facebook'], 
                subscribe_to_newsletter, data['referral']))
            conn.commit()
        return render_template('confirmation.html', message='Coach registered successfully.'), 201
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 400

@app.route('/register/user', methods=['POST'])
def register_user():
    # Endpoint to register a new user, requiring all specified fields. 
    data = request.form
    required_fields = ['email', 'firstname', 'lastname', 'username', 'password', 'phone', 'gender', 'dob', 'address', 'language', 'occupation', 'nationality']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return render_template('error.html', error_message="Missing fields: " + ", ".join(missing_fields)), 400

    # Generate bcrypt password hash
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            # Insert new user into the database
            cursor.execute("INSERT INTO Users (EmailAddress, FirstName, LastName, Username, PasswordHash, PhoneNumber, Gender, DateOfBirth, Address, PreferredLanguage, Occupation, Nationality) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (data['email'], data['firstname'], data['lastname'], data['username'], password_hash, data['phone'], data['gender'], data['dob'], data['address'], data['language'], data['occupation'], data['nationality']))
            conn.commit()
        return render_template('confirmation.html', message='User registered successfully.'), 201
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 400

@app.route('/login', methods=['POST'])
def login():
    # Endpoint for user login. Validates email and password against stored hashes.
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            # First, try to find the user in Coaches
            cursor.execute("SELECT PasswordHash FROM Coaches WHERE EmailAddress = ?", (email,))
            coach = cursor.fetchone()
            if coach:
                user_data = coach
                user_type = 'coach'
            else:
                # Try to find the user in Users
                cursor.execute("SELECT PasswordHash FROM Users WHERE EmailAddress = ?", (email,))
                user = cursor.fetchone()
                if user:
                    user_data = user
                    user_type = 'user'
                else:
                    user_data = None
                    user_type = None

            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[0].encode('utf-8')):
                # Store the logged-in user's email and user_type in the session
                session['email'] = email
                session['user_type'] = user_type
                if user_type == 'coach':
                    return redirect(url_for('coach_dashboard'))
                elif user_type == 'user':
                    return redirect(url_for('user_dashboard'))
                else:
                    return render_template('error.html', error_message="Invalid user type"), 401
            else:
                return render_template('error.html', error_message="Invalid credentials"), 401
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 400

@app.route('/coach/dashboard', methods=['GET'])
def coach_dashboard():
    if 'email' not in session or session.get('user_type') != 'coach':
        return redirect(url_for('login_form'))  
    return render_template('coach_dashboard.html')

@app.route('/user/dashboard', methods=['GET'])
def user_dashboard():
    if 'email' not in session or session.get('user_type') != 'user':
        return redirect(url_for('login_form'))  
    return render_template('user_dashboard.html')

@app.route('/coach', methods=['GET', 'POST'])
def coach_selection():
    # Ensure the user is logged in before allowing access to the coach selection form
    if 'email' not in session:
        return redirect(url_for('login_form'))  # Redirect to login if not logged in

    if request.method == 'POST':
        # Handle coach selection, ensuring no duplicate entries and updating if needed
        coach_type = request.form.get('coachType')
        email = session['email']
        coach_email = None
        coach_name = None

        if coach_type == 'Human':
            coach_email = request.form.get('humanCoachEmail')
            coach_name = request.form.get('humanCoachName')

        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                # Check if the user already made a selection and update instead of inserting a new row
                cursor.execute("SELECT * FROM CoachSelection WHERE EmailAddress = ?", (email,))
                existing_selection = cursor.fetchone()

                if existing_selection:
                    cursor.execute("""
                        UPDATE CoachSelection 
                        SET CoachType = ?, CoachEmailAddress = ?, CoachName = ? 
                        WHERE EmailAddress = ?
                    """, (coach_type, coach_email, coach_name, email))
                else:
                    cursor.execute("""
                        INSERT INTO CoachSelection (EmailAddress, CoachType, CoachEmailAddress, CoachName) 
                        VALUES (?, ?, ?, ?)
                    """, (email, coach_type, coach_email, coach_name))
                conn.commit()
            return render_template('confirmation_select.html', message='Coach selection submitted successfully.'), 201
        except Exception as e:
            return render_template('error.html', error_message=str(e)), 400

    else:
        # GET method: fetch the list of coaches from the 'Coaches' table
        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT EmailAddress, FullName, Specialization FROM Coaches")
                coaches = cursor.fetchall()
            return render_template('coach.html', coaches=coaches)
        except Exception as e:
            return render_template('error.html', error_message=str(e)), 400


    return render_template('coach.html')
@app.route('/checkcoach', methods=['GET'])
def check_coach():
    # Check the user's current coach selection
    if 'email' not in session:
        return redirect(url_for('login_form'))

    email = session['email']
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT CoachType, CoachEmailAddress FROM CoachSelection WHERE EmailAddress = ?", (email,))
            coach_selection = cursor.fetchone()

            if coach_selection:
                coach_type, coach_email = coach_selection
                if coach_type == 'Human':
                    # Fetch coach details
                    cursor.execute("SELECT FullName, Specialization FROM Coaches WHERE EmailAddress = ?", (coach_email,))
                    coach_info = cursor.fetchone()
                    if coach_info:
                        full_name, specialization = coach_info
                        return render_template('coach_info.html', message=f'You selected {full_name} ({specialization}) as your Human Coach.')
                    else:
                        return render_template('coach_info.html', message='Selected coach not found.')
                else:
                    return render_template('coach_info.html', message='You selected Freddie (AI Coach).')
            else:
                return render_template('coach_info.html', message='No coach selected.')
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 400
    
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('user_type', None)  
    return redirect(url_for('home'))

@app.route('/dash', methods=['GET'])
def dash():
    if 'email' not in session:
        return redirect(url_for('login_form'))  
    return render_template('user_dashboard.html')

@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        conn = pyodbc.connect(connection_string)
        conn.close()
        return jsonify({"message": "Database connection successful."}), 200
    except pyodbc.Error as ex:
        return jsonify({"error": str(ex)}), 500
    
    
# Routes for displaying registration and login forms
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register-coach')
def register_coach_form():
    return render_template('register-coach.html')

@app.route('/register-user')
def register_user_form():
    return render_template('register-user.html')

@app.route('/login')
def login_form():
    return render_template('login.html')

@app.route('/coach')
def coach_selection_form():
    return render_template('coach.html')



if __name__ == '__main__':
    app.run(debug=True)
